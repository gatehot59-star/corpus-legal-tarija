"""sistema/api/protected_search.py: bounded, authorized synthetic discovery.

No listener or issuance. Reuses the existing grant decision and exact reader.
Session eligibility is separate so an empty catalog never skips authentication.
"""
from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
import hashlib
from http import HTTPStatus
import json
import math
from pathlib import Path
import re
import sqlite3
import time
from typing import Callable
import unicodedata
from urllib.parse import unquote_to_bytes

from access_policy import SQLiteAccessPolicy
from exact_http import ExactReaderApp
from isolated_session import IsolatedSessionApp
from version_text import read_version

SEARCH_PATH = "/api/v2/buscar"
BODY_CAP = 16384


@dataclass(frozen=True)
class Candidate:
    """A trusted configured locator, never a client-selected collection."""
    uid: str
    version: str
    collection: str


def search_reply(environ: dict, start_response: Callable, status: int,
                 body: dict) -> list[bytes]:
    """Buffer bounded UTF-8 JSON; suppress HEAD content without inventing length."""
    data = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(data) > BODY_CAP:
        status, data = 503, b'{"error":"RESPONSE_LIMIT_EXCEEDED"}'
    headers = [("Content-Type", "application/json; charset=utf-8"),
               ("Cache-Control", "no-store"), ("X-Content-Type-Options", "nosniff"),
               ("Referrer-Policy", "no-referrer")]
    if status == 405:
        headers.append(("Allow", "GET"))
    if environ.get("REQUEST_METHOD") != "HEAD":
        headers.append(("Content-Length", str(len(data))))
    start_response(f"{status} {HTTPStatus(status).phrase}", headers)
    return [] if environ.get("REQUEST_METHOD") == "HEAD" else [data]


def parse_query(raw: str) -> tuple[str, int, int]:
    """Strict single transport decode, q codepoint/byte bounds, canonical numbers.

    Raises ValueError for invalid grammar. The caller checks the raw byte cap.
    """
    raw.encode("ascii", errors="strict")
    fields = raw.split("&")
    if not 1 <= len(fields) <= 3:
        raise ValueError("INVALID_QUERY")
    values: dict[str, str] = {}
    for field in fields:
        if "=" not in field or re.search(r"%(?![0-9a-fA-F]{2})", field):
            raise ValueError("INVALID_QUERY")
        key, value = (unquote_to_bytes(v.replace("+", " ")).decode("utf-8", "strict")
                      for v in field.split("=", 1))
        if key not in ("q", "offset", "limit") or key in values:
            raise ValueError("INVALID_QUERY")
        values[key] = value
    q = values.get("q", "")
    if (not 1 <= len(q) <= 128 or len(q.encode("utf-8")) > 256
            or q.isspace() or any(unicodedata.category(c) == "Cc" for c in q)):
        raise ValueError("INVALID_QUERY")
    offset, limit = values.get("offset", "0"), values.get("limit", "5")
    if not re.fullmatch(r"0|[1-9][0-9]?", offset) or int(offset) > 8:
        raise ValueError("INVALID_QUERY")
    if not re.fullmatch(r"[1-5]", limit):
        raise ValueError("INVALID_QUERY")
    return q, int(offset), int(limit)


class ProtectedSearchApp(IsolatedSessionApp):
    """Compose search after inherited guards, routing reads by trusted scope."""

    def __init__(self, candidate: str | Path, store: str | Path,
                 catalog: tuple[Candidate, ...], *,
                 clock: Callable[[], float] = time.time,
                 enable_test_login: bool = False,
                 browser_origin: str | None = None):
        if (not isinstance(catalog, tuple) or len(catalog) > 8
                or any(not isinstance(c, Candidate) for c in catalog)):
            raise ValueError("INVALID_CATALOG")
        if len({c.uid for c in catalog}) != len(catalog):
            raise ValueError("DUPLICATE_UID")
        for c in catalog:
            if (not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", c.uid)
                    or not re.fullmatch(r"[0-9a-f]{64}", c.version)
                    or not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", c.collection)):
                raise ValueError("INVALID_LOCATOR")
        self.catalog = tuple(sorted(catalog, key=lambda c: (c.uid, c.version)))
        self.policies = {c.collection: SQLiteAccessPolicy(store, c.collection, clock)
                         for c in catalog}
        super().__init__(candidate, store, "fixture-discovery",
                         clock=clock, enable_test_login=enable_test_login,
                         browser_origin=browser_origin)
        self.candidate_uri = Path(candidate).resolve(strict=True).as_uri() + "?mode=ro"
        self.scoped_reader = ExactReaderApp(candidate, self.authorize_locator)

    def authorize_locator(self, environ: dict, uid: str, version: str) -> bool:
        """Use the same configured locator and policy as search, rechecking now."""
        for item in self.catalog:
            if item.uid == uid and item.version == version:
                return self.policies[item.collection](environ, uid, version) is True
        return False

    def __call__(self, environ: dict, start_response: Callable) -> list[bytes]:
        """Normalize search only, including inherited guard errors and exceptions."""
        if environ.get("PATH_INFO") != SEARCH_PATH:
            return super().__call__(environ, start_response)
        captured: list[str] = []

        def capture(status: str, headers: list[tuple[str, str]], exc_info=None):
            captured.append(status)

        try:
            chunks = super().__call__(environ, capture)
            try:
                raw = bytearray()
                for chunk in chunks:
                    raw.extend(chunk)
                    if len(raw) > BODY_CAP:
                        return search_reply(environ, start_response, 503,
                                            {"error": "RESPONSE_LIMIT_EXCEEDED"})
            finally:
                if hasattr(chunks, "close"):
                    chunks.close()
            status = int(captured[0].split(" ", 1)[0])
            body = json.loads(raw)
            if not isinstance(body, dict) or (status != 200 and set(body) != {"error"}):
                raise ValueError("INVALID_UPSTREAM_RESPONSE")
        except Exception:
            status, body = 500, {"error": "INTERNAL_ERROR"}
        return search_reply(environ, start_response, status, body)

    def session_route(self, environ: dict, start_response: Callable) -> list[bytes]:
        """Keep login/logout inherited; route search and exact reads after guards."""
        if environ.get("PATH_INFO") == SEARCH_PATH:
            status, body = self.search_request(environ)
            # Internal serialization is captured by __call__, not sent to a peer.
            data = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            start_response(f"{status} {HTTPStatus(status).phrase}", [])
            return [data]
        if environ.get("PATH_INFO") == "/api/v2/logout":
            return super().session_route(environ, start_response)
        return self.scoped_reader(environ, start_response)

    def session_eligible(self, environ: dict) -> bool:
        """Check only existing session/user semantics, never duplicate grant SQL."""
        header = environ.get("HTTP_AUTHORIZATION", "")
        match = re.fullmatch(r"Bearer ([A-Za-z0-9_-]{43,128})", header) if isinstance(header, str) else None
        if match is None:
            return False
        now = self.clock()
        if isinstance(now, bool) or not isinstance(now, (int, float)) or not math.isfinite(now) or now < 0:
            raise ValueError("INVALID_CLOCK")
        digest = hashlib.sha256(match[1].encode("ascii")).hexdigest()
        with closing(sqlite3.connect(self.read_uri, uri=True, timeout=1)) as db:
            db.execute("PRAGMA query_only=ON")
            row = db.execute(
                "SELECT 1 FROM access_sessions s JOIN access_users u ON u.id=s.user_id "
                "WHERE s.token_sha256=? AND u.enabled=1 AND s.revoked_at IS NULL "
                "AND s.valid_from<=? AND ?<s.valid_until", (digest, now, now)).fetchone()
        return row is not None

    def search_request(self, environ: dict) -> tuple[int, dict]:
        """Validate, authenticate, authorize ALL locators, then read/match/page."""
        if environ.get("REQUEST_METHOD") != "GET":
            return 405, {"error": "METHOD_NOT_ALLOWED"}
        if environ.get("CONTENT_LENGTH", "") not in ("", "0") or "HTTP_TRANSFER_ENCODING" in environ:
            return 400, {"error": "EMPTY_REQUEST_REQUIRED"}
        raw = environ.get("QUERY_STRING", "")
        if not isinstance(raw, str):
            return 400, {"error": "INVALID_QUERY"}
        # WSGI encodes raw request target bytes as latin-1. Reject non-ASCII later.
        if len(raw.encode("latin-1", errors="replace")) > 2048:
            return 414, {"error": "QUERY_TOO_LONG"}
        try:
            q, offset, limit = parse_query(raw)
        except (ValueError, UnicodeError):
            return 400, {"error": "INVALID_QUERY"}
        try:
            if not self.session_eligible(environ):
                return 403, {"error": "ACCESS_DENIED"}
            allowed = [c for c in self.catalog
                       if self.policies[c.collection](environ, c.uid, c.version) is True]
        except Exception:
            return 503, {"error": "ACCESS_POLICY_UNAVAILABLE"}
        if not allowed:
            return 403, {"error": "ACCESS_DENIED"}
        results: list[dict] = []
        needle = unicodedata.normalize("NFC", q).casefold()
        try:
            with closing(sqlite3.connect(self.candidate_uri, uri=True, timeout=1)) as db:
                db.execute("PRAGMA query_only=ON")
                for item in allowed:
                    record = read_version(db, item.uid, item.version, 0, 4097)
                    text = record["text"]
                    if (record["total_characters"] > 4096 or record["next"] is not None
                            or len(text.encode("utf-8")) > 16384):
                        raise ValueError("TEXT_LIMIT")
                    if needle in unicodedata.normalize("NFC", text).casefold():
                        results.append(dict(uid=item.uid, version=item.version,
                            title=next((line[:80] for line in text.splitlines() if line), item.uid),
                            snippet=text[:160], authority="secondary", oficial=False,
                            legal_validity="NOT_MEASURED", source_url_scope="current_document"))
        except Exception:
            return 503, {"error": "SEARCH_UNAVAILABLE"}
        page = results[offset:offset + limit]
        next_offset = offset + len(page) if offset + len(page) < len(results) else None
        return 200, dict(schema="corpus-search-v1", environment="isolated_test",
                         total=len(results), offset=offset, limit=limit,
                         next_offset=next_offset, results=page)
