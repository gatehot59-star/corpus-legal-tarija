"""sistema/api/demo_discovery.py: exclusive two-scope, synthetic loopback demo.

No imported database, real credentials, grants or production mode.
The public fixture password is intentionally not a secret.
"""
from __future__ import annotations

import argparse
import base64
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import sqlite3
import sys
import time
from wsgiref.simple_server import ServerHandler, WSGIRequestHandler, make_server

from access_policy import SCHEMA
from demo_aislada import checked_file, checked_root
from isolated_login import LOGIN_SCHEMA, password_digest
from protected_search import Candidate, ProtectedSearchApp, SEARCH_PATH, search_reply
from version_text import read_version

PASSWORD = "solo-demo-ficticia"
TEXTS = {
    "fixture-a1": "DEMO A: derechos ficticios\r\nArtículo único: Ñ, ⚖, e\u0301 y 😀. Straße.\r\n",
    "fixture-a2": "<img src=x onerror=alert(1)> DEMO A\r\nOtro derecho ficticio, sin valor jurídico.\r\n",
    "fixture-b1": "DEMO B: derechos ficticios\r\nDocumento reservado a Ben. 😀\r\n",
    "fixture-b2": "DEMO B: registro ficticio\r\nOtro derecho de prueba, no una ley.\r\n",
}
CATALOG = tuple(Candidate(uid, hashlib.sha256(text.encode()).hexdigest(),
                         "fixture-scope-" + uid[8])
                for uid, text in TEXTS.items())
IDENTITY = "corpus-synthetic-discovery-v1"


def initialize(value: str | Path) -> dict:
    """Create a new private fixed manifest; failed init never overwrites or cleans."""
    root = Path(os.path.abspath(value))
    if root.parent.resolve(strict=True) != root.parent:
        raise ValueError("SYMLINK_REJECTED")
    root.mkdir(mode=0o700, exist_ok=False)
    checked_root(root)
    for name in ("candidate.db", "sessions.db"):
        fd = os.open(root / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(fd)
    with closing(sqlite3.connect(root / "candidate.db")) as db, db:
        db.executescript(
            "CREATE TABLE documentos(uid PRIMARY KEY,sha256,fuente_id,fuente_url);"
            "CREATE TABLE corpus_cleanup_versions(uid,version_sha256,extraction_json,"
            "PRIMARY KEY(uid,version_sha256));")
        for c in CATALOG:
            db.execute("INSERT INTO documentos VALUES(?,?,?,?)",
                       (c.uid, c.version, "lexivox_nacional",
                        "https://example.invalid/discovery/" + c.uid))
            db.execute("INSERT INTO corpus_cleanup_versions VALUES(?,?,?)",
                       (c.uid, c.version, json.dumps(dict(text=TEXTS[c.uid],
                        text_sha256=c.version, source_sha256="a"*64,
                        authority="secondary"))))
    salt = bytes(range(16))
    digest = password_digest(PASSWORD, salt)
    now = int(time.time())
    with closing(sqlite3.connect(root / "sessions.db")) as db, db:
        db.executescript(SCHEMA + LOGIN_SCHEMA)
        db.execute("CREATE TABLE discovery_identity(kind TEXT NOT NULL,manifest TEXT NOT NULL)")
        db.execute("INSERT INTO discovery_identity VALUES(?,?)",
                   (IDENTITY, json.dumps([c.__dict__ for c in CATALOG], sort_keys=True)))
        db.execute("INSERT INTO login_environment VALUES(1,'isolated_test')")
        for person, scope in (("ana", "a"), ("ben", "b")):
            user, collection, group = "fixture-" + person, "fixture-scope-" + scope, "group-" + scope
            db.execute("INSERT INTO access_users VALUES(?,1)", (user,))
            db.execute("INSERT INTO login_passwords VALUES(?,?,?,?)", (person, user, salt, digest))
            db.execute("INSERT INTO access_collections VALUES(?,1,'SYNTHETIC-NOT-APPROVAL')", (collection,))
            db.execute("INSERT INTO access_memberships VALUES(?,?,1)", (user, group))
            db.execute("INSERT INTO access_grants VALUES(?,?,?,?,'pilot',?,?,NULL,"
                       "'fixture-provisioner','SYNTHETIC-NOT-APPROVAL')",
                       (person, user, group, collection, now-1, now+86400))
        for c in CATALOG:
            db.execute("INSERT INTO access_documents VALUES(?,?,?,NULL)",
                       (c.collection, c.uid, c.version))
    validate(root)
    return {"event": "initialized", "synthetic": True}


def validate(value: str | Path) -> tuple[Path, Path]:
    """Read-only bounded preflight; validate manifest and reject unsafe files."""
    root = checked_root(value)
    candidate, store = (checked_file(root, f) for f in ("candidate.db", "sessions.db"))
    if os.path.samefile(candidate, store) or any(p.stat().st_size > 1048576 for p in (candidate, store)):
        raise ValueError("INVALID_DATABASE_FILES")
    if {p.name for p in root.iterdir()} != {"candidate.db", "sessions.db"}:
        raise ValueError("UNEXPECTED_FILES")
    with closing(sqlite3.connect(candidate.as_uri()+"?mode=ro", uri=True, timeout=1)) as db:
        db.execute("PRAGMA query_only=ON")
        if db.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
            raise ValueError("INVALID_CANDIDATE")
        expected = sorted((c.uid, c.version, "lexivox_nacional",
                           "https://example.invalid/discovery/"+c.uid) for c in CATALOG)
        if db.execute("SELECT uid,sha256,fuente_id,fuente_url FROM documentos ORDER BY uid").fetchall() != expected:
            raise ValueError("MANIFEST_MISMATCH")
        if db.execute("SELECT COUNT(*) FROM corpus_cleanup_versions").fetchone() != (len(CATALOG),):
            raise ValueError("MANIFEST_MISMATCH")
        for c in CATALOG:
            r = read_version(db, c.uid, c.version, 0, 4097)
            if r["text"] != TEXTS[c.uid] or r["source_sha256"] != "a"*64:
                raise ValueError("TEXT_MISMATCH")
    with closing(sqlite3.connect(store.as_uri()+"?mode=ro", uri=True, timeout=1)) as db:
        db.execute("PRAGMA query_only=ON")
        if db.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
            raise ValueError("INVALID_STORE")
        if db.execute("SELECT kind,manifest FROM discovery_identity").fetchall() != [
                (IDENTITY, json.dumps([c.__dict__ for c in CATALOG], sort_keys=True))]:
            raise ValueError("MANIFEST_MISMATCH")
        if db.execute("SELECT singleton,mode FROM login_environment").fetchall() != [(1,"isolated_test")]:
            raise ValueError("MARKER_REQUIRED")
        if db.execute("SELECT id FROM access_users ORDER BY id").fetchall() != [("fixture-ana",),("fixture-ben",)]:
            raise ValueError("INVALID_IDENTITIES")
        if db.execute("SELECT username,user_id FROM login_passwords ORDER BY username").fetchall() != [("ana","fixture-ana"),("ben","fixture-ben")]:
            raise ValueError("INVALID_IDENTITIES")
        if db.execute("SELECT id FROM access_collections ORDER BY id").fetchall() != [("fixture-scope-a",),("fixture-scope-b",)]:
            raise ValueError("INVALID_SCOPES")
        if db.execute("SELECT collection_id,uid,version FROM access_documents ORDER BY uid").fetchall() != [
                (c.collection,c.uid,c.version) for c in CATALOG]:
            raise ValueError("MANIFEST_MISMATCH")
        for table in ("access_sessions","access_grants","access_memberships","login_budget","login_clock"):
            db.execute("SELECT * FROM "+table+" LIMIT 0")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("INVALID_FOREIGN_KEYS")
    return candidate, store


class SearchServerHandler(ServerHandler):
    """Prevent wsgiref from synthesizing a Content-Length on rejected search HEAD."""
    def cleanup_headers(self):
        super().cleanup_headers()
        if (self.environ.get("REQUEST_METHOD") == "HEAD"
                and self.environ.get("PATH_INFO") == SEARCH_PATH):
            for header in ("Content-Length", "Transfer-Encoding"):
                if header in self.headers:
                    del self.headers[header]


class DiscoveryHandler(WSGIRequestHandler):
    """Check ambiguous headers before application dispatch; never log secrets."""
    def setup(self):
        self.request.settimeout(2)
        super().setup()

    def log_message(self, format, *args):
        """Suppress request targets and bearer credentials in local access logs."""

    def handle(self):
        """Use stdlib parsing, then search-specific raw early rejection and WSGI."""
        self.raw_requestline = self.rfile.readline(65537)
        if len(self.raw_requestline) > 65536:
            self.requestline = ""
            self.request_version = ""
            self.command = ""
            self.send_error(414)
            return
        if not self.parse_request():
            return
        ambiguous = any(len(self.headers.get_all(k, [])) > 1 for k in (
            "Host", "Origin", "Authorization", "Content-Length", "Content-Type",
            "Transfer-Encoding", "Sec-Fetch-Site"))
        environ = self.get_environ()
        environ["corpus.ambiguous_headers"] = ambiguous
        if ambiguous and environ.get("PATH_INFO") == SEARCH_PATH:
            captured = []
            data = search_reply(environ, lambda s,h: captured.append((s,h)), 403,
                                {"error":"DEMO_LOCAL_REQUEST_REQUIRED"})
            status, headers = captured[0]
            wire = ("HTTP/1.0 "+status+"\r\n"+"".join(k+": "+v+"\r\n" for k,v in headers)+"\r\n").encode("ascii")
            self.wfile.write(wire + b"".join(data))
            return
        handler = SearchServerHandler(self.rfile, self.wfile, self.get_stderr(), environ,
                                      multithread=False)
        handler.request_handler = self
        handler.run(self.server.get_app())


def serve(value: str | Path, port: int = 0) -> int:
    """Serve one local synchronous request at a time, closing listener on signals."""
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValueError("INVALID_PORT")
    candidate, store = validate(value)
    running = [True]
    old = {}
    with make_server("127.0.0.1", port, lambda e,s: [], handler_class=DiscoveryHandler) as server:
        origin = "http://127.0.0.1:"+str(server.server_port)
        app = ProtectedSearchApp(candidate, store, CATALOG, enable_test_login=True, browser_origin=origin)
        page = (Path(__file__).resolve().parent.parent/"web"/"discovery_spike.html").read_bytes()
        def hashes(tag: bytes) -> str:
            return " ".join("'sha256-"+base64.b64encode(hashlib.sha256(s).digest()).decode()+"'"
                            for s in re.findall(b"<"+tag+b">(.*?)</"+tag+b">", page, re.S))
        csp = ("default-src 'none'; script-src "+hashes(b"script")+"; style-src "+hashes(b"style")+
               "; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'; object-src 'none'")

        def guarded(environ: dict, start_response):
            search = environ.get("PATH_INFO") == SEARCH_PATH
            if not app.browser_request_allowed(environ) or environ.get("corpus.ambiguous_headers"):
                if search:
                    return search_reply(environ,start_response,403,{"error":"DEMO_LOCAL_REQUEST_REQUIRED"})
                return app.reply(start_response,403,{"error":"DEMO_LOCAL_REQUEST_REQUIRED"})
            if environ.get("PATH_INFO") == "/":
                if environ.get("REQUEST_METHOD") != "GET" or environ.get("QUERY_STRING"):
                    return app.reply(start_response,400,{"error":"PAGE_REQUEST_REJECTED"})
                start_response("200 OK",[("Content-Type","text/html; charset=utf-8"),
                    ("Content-Length",str(len(page))),("Cache-Control","no-store"),
                    ("Content-Security-Policy",csp),("X-Frame-Options","DENY"),
                    ("X-Content-Type-Options","nosniff"),("Referrer-Policy","no-referrer"),
                    ("Cross-Origin-Opener-Policy","same-origin")])
                return [page]
            return app(environ,start_response)
        server.set_app(guarded)
        server.timeout = .2
        def stop(signum, frame):
            running[0] = False
        try:
            for sig in (signal.SIGINT, signal.SIGTERM):
                old[sig] = signal.signal(sig, stop)
            print(json.dumps({"event":"ready","synthetic":True,"url":origin,"pid":os.getpid()}),flush=True)
            while running[0]:
                server.handle_request()
        finally:
            for sig, previous in old.items():
                signal.signal(sig, previous)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Require explicit opt-in; never accept imported fixtures or real accounts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("init","serve"))
    parser.add_argument("--directory",required=True)
    parser.add_argument("--isolated-demo",action="store_true")
    parser.add_argument("--port",type=int,default=0)
    args = parser.parse_args(argv)
    if not args.isolated_demo or os.name != "posix" or not 0 <= args.port <= 65535:
        parser.error("explicit POSIX --isolated-demo and port 0..65535 required")
    try:
        if args.action == "init":
            print(json.dumps(initialize(args.directory)),flush=True)
            return 0
        return serve(args.directory,args.port)
    except (OSError,ValueError,sqlite3.Error):
        print("DISCOVERY_STARTUP_FAILED",file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
