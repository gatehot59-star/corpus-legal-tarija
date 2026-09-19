"""sistema/api/isolated_session.py: isolated login/read/logout composition.

No listener, real accounts, credentials, grants, migrations or deployment.
Uses PR12 dispatch guards unchanged. Logout revokes only the presented bearer;
it does not recall responses already authorized or invalidate other sessions.
"""
from __future__ import annotations

from contextlib import closing
import hashlib
import math
import re
import sqlite3
from typing import Callable

from isolated_login import IsolatedLoginApp


class IsolatedSessionApp(IsolatedLoginApp):
    """Add persistent logout to the explicitly enabled fixture-only wrapper."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._exact_reader = self.reader
        self.reader = self.session_route

    def session_route(self, environ: dict, start_response: Callable) -> list[bytes]:
        """Dispatch after inherited loopback/opt-in/marker checks."""
        if environ.get("PATH_INFO") != "/api/v2/logout":
            return self._exact_reader(environ, start_response)
        try:
            status, body = self.logout_request(environ)
        except Exception:
            status, body = 503, {"error": "LOGOUT_UNAVAILABLE"}
        return self.reply(start_response, status, body)

    def logout_request(self, environ: dict) -> tuple[int, dict]:
        """Revoke one bearer transactionally; unknown/repeated tokens return 200.

        POST with no query, Origin, transfer encoding or body is required.
        Logout deliberately needs no active user, grant, or unexpired session.
        Invalid clocks fail closed; rollback does not prevent revocation because
        access policy treats every non-NULL revoked_at as revoked.
        """
        if environ.get("REQUEST_METHOD") != "POST":
            return 405, {"error": "METHOD_NOT_ALLOWED"}
        origin_ok = (self.browser_request_allowed(environ)
                     if self.browser_origin is not None else "HTTP_ORIGIN" not in environ)
        if not origin_ok or "HTTP_TRANSFER_ENCODING" in environ:
            return 403, {"error": "REQUEST_REJECTED"}
        if environ.get("QUERY_STRING", "") or environ.get("CONTENT_LENGTH", "") not in ("", "0"):
            return 400, {"error": "EMPTY_REQUEST_REQUIRED"}
        authorization = environ.get("HTTP_AUTHORIZATION", "")
        match = re.fullmatch(r"Bearer ([A-Za-z0-9_-]{43,128})", authorization) if isinstance(authorization, str) else None
        if match is None:
            return 401, {"error": "INVALID_SESSION"}
        now = self.clock()
        if isinstance(now, bool) or not isinstance(now, (int, float)) or not math.isfinite(now) or now < 0:
            return 400, {"error": "INVALID_CLOCK"}
        digest = hashlib.sha256(match[1].encode("ascii")).hexdigest()
        with closing(sqlite3.connect(self.uri, uri=True, timeout=1)) as db:
            with db:
                db.execute("BEGIN IMMEDIATE")
                marker = db.execute("SELECT mode FROM login_environment WHERE singleton=1").fetchone()
                if marker != ("isolated_test",):
                    return 403, {"error": "ISOLATED_LOGIN_DISABLED"}
                db.execute(
                    "UPDATE access_sessions SET revoked_at=? "
                    "WHERE token_sha256=? AND revoked_at IS NULL "
                    "AND user_id GLOB 'fixture-*'",
                    (int(now), digest),
                )
        return 200, {"logged_out": True, "environment": "isolated_test"}
