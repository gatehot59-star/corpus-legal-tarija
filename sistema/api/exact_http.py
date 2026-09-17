"""sistema/api/exact_http.py: opt-in WSGI exact reader, never starts a listener.

The hosting application supplies an authorizer for a concrete (uid, version).
It must authenticate the request and enforce collection, grant and withdrawal
policy on EVERY call. No authorizer means deny, not anonymous public access.
This module does not install routes in servidor.py or discover a database.
"""
from __future__ import annotations

from contextlib import closing
from http import HTTPStatus
import json
from pathlib import Path
import re
import sqlite3
from typing import Callable, Iterable
from urllib.parse import parse_qs

from version_text import VersionReadError, read_version

Authorize = Callable[[dict, str, str], bool]
StartResponse = Callable[[str, list[tuple[str, str]]], object]
PREFIX = "/api/v2/documento/"
SUFFIX = "/texto"


class ExactReaderApp:
    """An isolated read-only HTTP adapter with a fail-closed policy boundary.

    db_path must name an existing explicit candidate file. authorize is trusted
    server-side code, not a client-controlled header or a query parameter.
    Only literal True permits reading; a missing/broken policy denies access.
    An allowed response is not evidence of legal review or release approval.
    """

    def __init__(self, db_path: str | Path, authorize: Authorize | None = None):
        path = Path(db_path).resolve(strict=True)
        if not path.is_file():
            raise ValueError("DATABASE_NOT_REGULAR")
        if authorize is not None and not callable(authorize):
            raise TypeError("INVALID_AUTHORIZER")
        self.uri = path.as_uri() + "?mode=ro"
        self.authorize = authorize

    def __call__(self, environ: dict, start_response: StartResponse) -> Iterable[bytes]:
        """Serve one GET, rechecking policy before database access or output."""
        headers = [("Content-Type", "application/json; charset=utf-8"),
                   ("Cache-Control", "no-store"), ("X-Content-Type-Options", "nosniff"),
                   ("Referrer-Policy", "no-referrer")]
        try:
            status, body = self.dispatch(environ)
        except Exception:
            # No traceback, document contents, file paths or policy exception in HTTP.
            status, body = 500, {"error": "INTERNAL_ERROR"}
        if status == 405:
            headers.append(("Allow", "GET"))
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers.append(("Content-Length", str(len(data))))
        start_response(f"{status} {HTTPStatus(status).phrase}", headers)
        return [data]

    def dispatch(self, environ: dict) -> tuple[int, dict]:
        """Validate a versioned locator, authorize it, then read exact bytes as text."""
        if environ.get("REQUEST_METHOD") != "GET":
            return 405, {"error": "METHOD_NOT_ALLOWED"}
        path = environ.get("PATH_INFO", "")
        if not (path.startswith(PREFIX) and path.endswith(SUFFIX)):
            return 404, {"error": "NOT_FOUND"}
        uid = path[len(PREFIX):-len(SUFFIX)]
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", uid):
            return 400, {"error": "INVALID_UID"}
        raw = environ.get("QUERY_STRING", "")
        if len(raw) > 2048:
            return 400, {"error": "INVALID_QUERY"}
        try:
            query = parse_qs(raw, keep_blank_values=True, strict_parsing=True,
                             max_num_fields=3)
        except ValueError:
            return 400, {"error": "INVALID_QUERY"}
        if set(query) - {"version", "start", "limit"} or any(len(v) != 1 for v in query.values()):
            return 400, {"error": "INVALID_QUERY"}
        version = query.get("version", [""])[0]
        if not re.fullmatch(r"[0-9a-f]{64}", version):
            return 400, {"error": "EXPLICIT_VERSION_REQUIRED"}
        start, limit = query.get("start", ["0"])[0], query.get("limit", ["2600"])[0]
        if not re.fullmatch(r"[0-9]{1,12}", start) or not re.fullmatch(r"[0-9]{1,5}", limit):
            return 400, {"error": "INVALID_RANGE"}
        if not 1 <= int(limit) <= 10000:
            return 400, {"error": "INVALID_RANGE"}
        try:
            allowed = self.authorize is not None and self.authorize(environ, uid, version) is True
        except Exception:
            return 503, {"error": "ACCESS_POLICY_UNAVAILABLE"}
        if not allowed:
            return 403, {"error": "ACCESS_DENIED"}
        try:
            with closing(sqlite3.connect(self.uri, uri=True, timeout=1)) as db:
                db.execute("PRAGMA query_only=ON")
                result = read_version(db, uid, version, int(start), int(limit))
        except VersionReadError as exc:
            status = {"NOT_FOUND": 404, "EXACT_VERSION_UNAVAILABLE": 409,
                      "VERSION_INTEGRITY_FAILED": 409, "UNSUPPORTED_PROVENANCE": 409,
                      "OFFSET_OUT_OF_RANGE": 416}.get(exc.code, 400)
            return status, {"error": exc.code}
        except sqlite3.Error:
            return 503, {"error": "DATABASE_UNAVAILABLE"}
        # URL is currently from the stable document row, not the historical ledger.
        result["source_url_scope"] = "current_document"
        result["offset_unit"] = "unicode_code_points"
        return 200, result
