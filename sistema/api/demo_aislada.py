"""Explicit synthetic Corpus demo. Never accepts an existing corpus database.

POSIX/local developer tool, not a production server or a sandbox against its
owner. Initialization is exclusive; serving never provisions or resets state.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import signal
import sqlite3
import stat
import sys
import time
from wsgiref.simple_server import WSGIRequestHandler, make_server

from access_policy import SCHEMA
from isolated_login import LOGIN_SCHEMA, password_digest
from isolated_session import IsolatedSessionApp
from version_text import read_version

TEXT = "DEMO FICTICIA, SIN VALOR JURIDICO\nArtículo único: Ñ, ⚖ y e\u0301.\r\n"
VERSION = hashlib.sha256(TEXT.encode("utf-8")).hexdigest()
UID = "fixture-demo"
COLLECTION = "fixture-demo"
# Public fixture credentials, deliberately NOT a secret or real account.
PASSWORD = "solo-demo-ficticia"
SALT = bytes(range(16))


def checked_root(value: str | Path) -> Path:
    """Require an owned private directory without symlinks in its path."""
    root = Path(os.path.abspath(value))
    if root.resolve(strict=True) != root:
        raise ValueError("DEMO_SYMLINK_REJECTED")
    info = root.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
        raise ValueError("DEMO_PRIVATE_DIRECTORY_REQUIRED")
    if stat.S_IMODE(info.st_mode) != 0o700:
        raise ValueError("DEMO_DIRECTORY_MODE_0700_REQUIRED")
    return root


def checked_file(root: Path, name: str) -> Path:
    """Reject missing, linked, shared or nonregular database files."""
    path = root / name
    info = path.lstat()
    if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
            or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600):
        raise ValueError("DEMO_PRIVATE_REGULAR_FILE_REQUIRED")
    return path


def initialize(value: str | Path) -> dict:
    """Create only a new private synthetic fixture; never overwrite or resume."""
    root = Path(os.path.abspath(value))
    if root.parent.resolve(strict=True) != root.parent:
        raise ValueError("DEMO_SYMLINK_REJECTED")
    root.mkdir(mode=0o700, exist_ok=False)
    checked_root(root)
    # A failed init deliberately leaves a non-servable directory for inspection.
    # There is no automatic deletion, overwrite, reset or retry into old files.
    for name in ("candidate.db", "sessions.db"):
        fd = os.open(root / name, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
    candidate = checked_file(root, "candidate.db")
    store = checked_file(root, "sessions.db")
    with closing(sqlite3.connect(candidate)) as db, db:
        db.executescript(
            "CREATE TABLE documentos(uid PRIMARY KEY,sha256,fuente_id,fuente_url);"
            "CREATE TABLE corpus_cleanup_versions(uid,version_sha256,extraction_json,"
            "PRIMARY KEY(uid,version_sha256));")
        # The existing reader supports this provenance schema. The URL and body
        # explicitly identify a fictional fixture, NOT a real LexiVox record.
        db.execute("INSERT INTO documentos VALUES(?,?,?,?)",
                   (UID, VERSION, "lexivox_nacional", "https://example.invalid/corpus-demo"))
        db.execute("INSERT INTO corpus_cleanup_versions VALUES(?,?,?)",
                   (UID, VERSION, json.dumps(dict(text=TEXT, text_sha256=VERSION,
                    source_sha256=VERSION, authority="secondary"))))
    digest = password_digest(PASSWORD, SALT)
    now = int(time.time())
    with closing(sqlite3.connect(store)) as db, db:
        db.executescript(SCHEMA + LOGIN_SCHEMA)
        db.execute("CREATE TABLE demo_identity(kind TEXT NOT NULL)")
        db.execute("INSERT INTO demo_identity VALUES('corpus-synthetic-demo-v1')")
        db.execute("INSERT INTO login_environment VALUES(1,'isolated_test')")
        db.execute("INSERT INTO access_collections VALUES(?,1,'SYNTHETIC-NOT-APPROVAL')",
                   (COLLECTION,))
        db.execute("INSERT INTO access_documents VALUES(?,?,?,NULL)",
                   (COLLECTION, UID, VERSION))
        for name in ("ana", "ben"):
            user = "fixture-" + name
            db.execute("INSERT INTO access_users VALUES(?,1)", (user,))
            db.execute("INSERT INTO login_passwords VALUES(?,?,?,?)",
                       (name, user, SALT, digest))
            db.execute("INSERT INTO access_memberships VALUES(?,'demo',1)", (user,))
            # Provisioning is explicit and separate from login. It is fictional.
            db.execute("INSERT INTO access_grants VALUES(?,?,'demo',?,'pilot',?,?,"
                       "NULL,'fixture-provisioner','SYNTHETIC-NOT-APPROVAL')",
                       (name, user, COLLECTION, now - 1, now + 86400))
    validate(root)
    return dict(event="initialized", directory=str(root), synthetic=True,
                uid=UID, version=VERSION, grant_lifetime_seconds=86400)


def validate(value: str | Path) -> tuple[Path, Path]:
    """Read-only preflight; require a complete synthetic fixture before binding."""
    root = checked_root(value)
    candidate = checked_file(root, "candidate.db")
    store = checked_file(root, "sessions.db")
    if os.path.samefile(candidate, store):
        raise ValueError("SEPARATE_POLICY_STORE_REQUIRED")
    # Unknown sidecars and partial journals require operator inspection, not
    # implicit SQLite recovery/migration of possibly unrelated files.
    if {p.name for p in root.iterdir()} != {"candidate.db", "sessions.db"}:
        raise ValueError("DEMO_UNEXPECTED_FILES")
    with closing(sqlite3.connect(candidate.as_uri() + "?mode=ro", uri=True)) as db:
        db.execute("PRAGMA query_only=ON")
        if db.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
            raise ValueError("DEMO_CANDIDATE_INVALID")
        if db.execute("SELECT uid,sha256,fuente_id,fuente_url FROM documentos").fetchall() != [
                (UID, VERSION, "lexivox_nacional", "https://example.invalid/corpus-demo")]:
            raise ValueError("DEMO_CANDIDATE_NOT_SYNTHETIC")
        if db.execute("SELECT COUNT(*) FROM corpus_cleanup_versions").fetchone() != (1,):
            raise ValueError("DEMO_CANDIDATE_NOT_SYNTHETIC")
        if read_version(db, UID, VERSION, 0, 10000)["text"] != TEXT:
            raise ValueError("DEMO_TEXT_MISMATCH")
    with closing(sqlite3.connect(store.as_uri() + "?mode=ro", uri=True)) as db:
        db.execute("PRAGMA query_only=ON")
        if db.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
            raise ValueError("DEMO_STORE_INVALID")
        if db.execute("SELECT kind FROM demo_identity").fetchall() != [
                ("corpus-synthetic-demo-v1",)]:
            raise ValueError("DEMO_STORE_NOT_SYNTHETIC")
        if db.execute("SELECT singleton,mode FROM login_environment").fetchall() != [
                (1, "isolated_test")]:
            raise ValueError("DEMO_MARKER_REQUIRED")
        if db.execute("SELECT id FROM access_users ORDER BY id").fetchall() != [
                ("fixture-ana",), ("fixture-ben",)]:
            raise ValueError("DEMO_USERS_INVALID")
        if db.execute("SELECT username,user_id FROM login_passwords ORDER BY username").fetchall() != [
                ("ana", "fixture-ana"), ("ben", "fixture-ben")]:
            raise ValueError("DEMO_USERS_INVALID")
        for table in ("login_clock", "login_budget", "access_sessions", "access_grants",
                      "access_memberships", "access_collections", "access_documents"):
            db.execute("SELECT * FROM " + table + " LIMIT 0")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("DEMO_FOREIGN_KEYS_INVALID")
    return candidate, store


class DemoHandler(WSGIRequestHandler):
    """Bound stalled local requests and avoid logging credentials or queries."""

    def setup(self):
        self.request.settimeout(2)
        super().setup()

    def log_message(self, format, *args):
        pass


def serve(value: str | Path, port: int) -> int:
    """Serve the existing wrapper on literal IPv4 loopback until SIGINT/SIGTERM."""
    if not 0 <= port <= 65535:
        raise ValueError("DEMO_INVALID_PORT")
    candidate, store = validate(value)
    app = IsolatedSessionApp(candidate, store, COLLECTION, enable_test_login=True)
    running = [True]
    old_handlers = {}
    with make_server("127.0.0.1", port, app, handler_class=DemoHandler) as server:
        # Block browser cross-origin requests/rebinding. No proxy support.
        expected_host = "127.0.0.1:" + str(server.server_port)

        def guarded(environ, start_response):
            if (environ.get("HTTP_HOST") != expected_host
                    or "HTTP_ORIGIN" in environ):
                return app.reply(start_response, 403, {"error": "DEMO_LOCAL_REQUEST_REQUIRED"})
            return app(environ, start_response)

        server.set_app(guarded)
        server.timeout = 0.2

        def stop(signum, frame):
            running[0] = False

        try:
            for sig in (signal.SIGINT, signal.SIGTERM):
                old_handlers[sig] = signal.signal(sig, stop)
            print(json.dumps(dict(event="ready", synthetic=True, pid=os.getpid(),
                                  url="http://" + expected_host, uid=UID, version=VERSION)),
                  flush=True)
            while running[0]:
                server.handle_request()
        finally:
            for sig, previous in old_handlers.items():
                signal.signal(sig, previous)
    return 0


def main(argv=None) -> int:
    """Parse explicit opt-in before any filesystem writes or listener creation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("init", "serve"))
    parser.add_argument("--directory", required=True)
    parser.add_argument("--isolated-demo", action="store_true",
                        help="explicit opt-in: synthetic data, local demo only")
    parser.add_argument("--port", type=int, default=0,
                        help="serve port; default 0 selects an unused local port")
    args = parser.parse_args(argv)
    if not args.isolated_demo:
        parser.error("--isolated-demo is required; no production mode exists")
    if not 0 <= args.port <= 65535:
        parser.error("--port must be 0..65535")
    if os.name != "posix":
        parser.error("POSIX private-directory semantics required")
    try:
        if args.action == "init":
            print(json.dumps(initialize(args.directory)), flush=True)
            return 0
        return serve(args.directory, args.port)
    except (OSError, ValueError, sqlite3.Error) as exc:
        # No SQL values, bodies or credentials in startup errors.
        print("DEMO_STARTUP_FAILED: " + type(exc).__name__, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
