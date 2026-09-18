"""sistema/api/isolated_login.py: disabled-by-default, loopback-only test login.

No real account provisioning, reset, grant issuance, production listener or
migration. The host must explicitly opt in AND mark a separate fixture store.
The only sessions this module may create belong to fixture-* test identities.
"""
from __future__ import annotations
from contextlib import closing
import hashlib
import hmac
import ipaddress
import json
import math
from pathlib import Path
import re
import secrets
import sqlite3
import time
from http import HTTPStatus
from typing import Callable

from access_policy import make_app

LOGIN_SCHEMA = """
CREATE TABLE login_environment (
 singleton INTEGER PRIMARY KEY CHECK(singleton=1),
 mode TEXT NOT NULL CHECK(mode='isolated_test')
) STRICT;
CREATE TABLE login_passwords (
 username TEXT PRIMARY KEY,
 user_id TEXT UNIQUE NOT NULL REFERENCES access_users(id)
 CHECK(user_id GLOB 'fixture-*'),
 salt BLOB NOT NULL CHECK(length(salt)=16),
 digest BLOB NOT NULL CHECK(length(digest)=32)
) STRICT;
CREATE TABLE login_budget (
 singleton INTEGER PRIMARY KEY CHECK(singleton=1),
 window_start INTEGER NOT NULL,
 attempts INTEGER NOT NULL CHECK(attempts>=0)
) STRICT;
"""


def password_digest(password: str, salt: bytes) -> bytes:
    """Derive a fixed-cost scrypt verifier; never writes or creates an account."""
    if not isinstance(password, str) or not 1 <= len(password.encode("utf-8")) <= 1024:
        raise ValueError("INVALID_PASSWORD")
    if not isinstance(salt, bytes) or len(salt) != 16:
        raise ValueError("INVALID_SALT")
    # OWASP Password Storage Cheat Sheet verified 2026-09-17.
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**17,
                          r=8, p=1, maxmem=256*1024*1024, dklen=32)


def unique_object(pairs: list) -> dict:
    """Reject duplicate JSON keys rather than selecting an ambiguous password."""
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("DUPLICATE_KEY")
        obj[key] = value
    return obj


class IsolatedLoginApp:
    """Compose login with PR10. No requests can be served off loopback.

    Opt-in and fixture-store markers are guardrails, not a sandbox against a
    malicious operator. This app is intentionally unsuitable for production.
    All authentication attempts share a persisted five-attempt/60s test budget.
    This coarse limit is not a production distributed rate-limiter.
    """

    def __init__(self, candidate: str | Path, store: str | Path, collection: str,
                 *, enable_test_login: bool = False,
                 clock: Callable[[], float] = time.time):
        self.reader = make_app(candidate, store, collection, clock)
        self.uri = Path(store).resolve(strict=True).as_uri() + "?mode=rw"
        self.enabled = enable_test_login is True
        self.clock = clock

    def __call__(self, environ: dict, start_response: Callable) -> list[bytes]:
        """Serve bounded JSON login or pass reads through the existing policy."""
        try:
            remote = ipaddress.ip_address(environ.get("REMOTE_ADDR", ""))
            if not self.enabled or not remote.is_loopback:
                return self.reply(start_response, 403, {"error": "ISOLATED_LOGIN_DISABLED"})
        except ValueError:
            return self.reply(start_response, 403, {"error": "ISOLATED_LOGIN_DISABLED"})
        if environ.get("PATH_INFO") != "/api/v2/login":
            return self.reader(environ, start_response)
        try:
            status, body = self.login_request(environ)
        except Exception:
            status, body = 503, {"error": "LOGIN_UNAVAILABLE"}
        return self.reply(start_response, status, body)

    @staticmethod
    def reply(start_response: Callable, status: int, body: dict) -> list[bytes]:
        """Serialize without cookies, CORS, secrets in errors or cache permission."""
        data = json.dumps(body).encode()
        headers = [("Content-Type", "application/json"), ("Cache-Control", "no-store"),
                   ("X-Content-Type-Options", "nosniff"), ("Content-Length", str(len(data)))]
        if status == 405:
            headers.append(("Allow", "POST"))
        if status == 429:
            headers.append(("Retry-After", "60"))
        start_response(f"{status} {HTTPStatus(status).phrase}", headers)
        return [data]

    def login_request(self, environ: dict) -> tuple[int, dict]:
        """Bound and validate HTTP input before KDF work or session insertion."""
        if environ.get("REQUEST_METHOD") != "POST":
            return 405, {"error": "METHOD_NOT_ALLOWED"}
        if environ.get("HTTP_ORIGIN") or environ.get("HTTP_TRANSFER_ENCODING"):
            return 403, {"error": "REQUEST_REJECTED"}
        if environ.get("CONTENT_TYPE", "").lower() != "application/json":
            return 415, {"error": "JSON_REQUIRED"}
        length = environ.get("CONTENT_LENGTH", "")
        if not re.fullmatch(r"[0-9]{1,4}", length) or not 1 <= int(length) <= 4096:
            return 400, {"error": "INVALID_BODY"}
        raw = environ["wsgi.input"].read(int(length))
        if len(raw) != int(length):
            return 400, {"error": "INVALID_BODY"}
        try:
            obj = json.loads(raw, object_pairs_hook=unique_object)
            if not isinstance(obj, dict) or set(obj) != {"username", "password"}:
                raise ValueError("INVALID_BODY")
            username, password = obj["username"], obj["password"]
            if not isinstance(username, str) or not re.fullmatch(r"[a-z0-9_-]{1,80}", username):
                raise ValueError("INVALID_BODY")
            if not isinstance(password, str) or not 1 <= len(password.encode("utf-8")) <= 1024:
                raise ValueError("INVALID_BODY")
        except (ValueError, UnicodeError):
            return 400, {"error": "INVALID_BODY"}
        return self.authenticate(username, password)

    def authenticate(self, username: str, password: str) -> tuple[int, dict]:
        """Internal validated-input operation; commit a fixture session atomically."""
        now = self.clock()
        if isinstance(now, bool) or not isinstance(now, (int, float)) or not math.isfinite(now) or now < 0:
            raise ValueError("INVALID_CLOCK")
        now = int(now)
        with closing(sqlite3.connect(self.uri, uri=True, timeout=1)) as db:
            db.execute("PRAGMA foreign_keys=ON")
            with db:
                # Serialize KDF/attempt/session writes in this isolated store.
                db.execute("BEGIN IMMEDIATE")
                mode = db.execute("SELECT mode FROM login_environment WHERE singleton=1").fetchone()
                if mode != ("isolated_test",) or not self.enabled:
                    return 403, {"error": "ISOLATED_LOGIN_DISABLED"}
                budget = db.execute("SELECT window_start,attempts FROM login_budget WHERE singleton=1").fetchone()
                if budget and now < budget[0]:
                    raise ValueError("CLOCK_ROLLBACK")
                start, count = budget if budget and now-budget[0] < 60 else (now, 0)
                if count >= 5:
                    return 429, {"error": "TRY_LATER"}
                db.execute("INSERT OR REPLACE INTO login_budget VALUES(1,?,?)", (start, count+1))
                row = db.execute(
                    "SELECT p.user_id,p.salt,p.digest,u.enabled FROM login_passwords p "
                    "JOIN access_users u ON u.id=p.user_id WHERE p.username=?", (username,)).fetchone()
                # Unknown and disabled users still perform one full KDF.
                salt = row[1] if row else b"\0"*16
                expected = row[2] if row else b"\0"*32
                actual = password_digest(password, salt)
                valid = hmac.compare_digest(actual, expected)
                if not row or row[3] != 1 or not row[0].startswith("fixture-") or not valid:
                    return 401, {"error": "INVALID_CREDENTIALS"}
                token = secrets.token_urlsafe(32)
                token_hash = hashlib.sha256(token.encode("ascii")).hexdigest()
                db.execute("INSERT INTO access_sessions VALUES(?,?,?,?,NULL)",
                           (token_hash, row[0], now, now+900))
                # Deliberately no access_grants write: login is not authorization.
                return 200, {"access_token": token, "token_type": "Bearer",
                             "expires_in": 900, "environment": "isolated_test"}
