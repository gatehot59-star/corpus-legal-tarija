"""Persistent access integration tests; all identities/approvals are fictional."""
import hashlib
from http.client import HTTPConnection
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import unittest
from urllib.parse import urlencode
from wsgiref.simple_server import make_server, WSGIRequestHandler

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sistema/api"))
from access_policy import SCHEMA, SQLiteAccessPolicy, make_app


class QuietHandler(WSGIRequestHandler):
    def log_message(self, *args):
        """Do not log fixture credentials or request data."""


class AccessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.store, self.candidate = self.root / "policy.db", self.root / "candidate.db"
        self.token = "synthetic_fixture_not_a_live_credential_000001"
        self.digest = hashlib.sha256(self.token.encode()).hexdigest()
        self.text = "Ley de prueba\n" + "No omitir esta clausula.\n" * 150
        self.sha = hashlib.sha256(self.text.encode()).hexdigest()
        self.now = 1000
        with sqlite3.connect(self.store) as db:
            db.executescript(SCHEMA)
            db.execute("INSERT INTO access_users VALUES('u',1)")
            db.execute("INSERT INTO access_sessions VALUES(?,?,900,1100,NULL)", (self.digest, "u"))
            db.execute("INSERT INTO access_collections VALUES('c',1,'synthetic-approval')")
            db.execute("INSERT INTO access_collections VALUES('other',1,'synthetic-other')")
            db.execute("INSERT INTO access_memberships VALUES('u','g',1)")
            db.execute("INSERT INTO access_grants VALUES('grant','u','g','c','pilot',900,1100,NULL,'fixture-issuer','fixture-evidence')")
            db.execute("INSERT INTO access_documents VALUES('c','uid',?,NULL)", (self.sha,))
        with sqlite3.connect(self.candidate) as db:
            db.executescript("CREATE TABLE documentos(uid TEXT,sha256 TEXT,fuente_id TEXT,fuente_url TEXT);"
                            "CREATE TABLE corpus_cleanup_versions(uid TEXT,version_sha256 TEXT,extraction_json TEXT);")
            db.execute("INSERT INTO documentos VALUES(?,?,?,?)", ("uid", self.sha, "lexivox_nacional", "https://example.org/fixture"))
            db.execute("INSERT INTO corpus_cleanup_versions VALUES(?,?,?)", ("uid", self.sha, json.dumps({
                "text": self.text, "text_sha256": self.sha, "source_sha256": "a"*64, "authority": "secondary"})))
        self.app = make_app(self.candidate, self.store, "c", lambda: self.now)
        self.server = make_server("127.0.0.1", 0, self.app, handler_class=QuietHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.01})
        self.thread.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.assertFalse(self.thread.is_alive())

    def sql(self, statement, params=()):
        with sqlite3.connect(self.store) as db:
            db.execute(statement, params)

    def request(self, token=None, uid="uid", version=None, start=0, extras=None):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        headers = {"Authorization": "Bearer " + (self.token if token is None else token)}
        headers.update(extras or {})
        try:
            conn.request("GET", "/api/v2/documento/" + uid + "/texto?" + urlencode(
                {"version": self.sha if version is None else version, "start": start, "limit": 301}), headers=headers)
            response = conn.getresponse()
            return response.status, dict(response.getheaders()), json.loads(response.read())
        finally:
            conn.close()

    def test_persisted_pilot_full_pagination_preserves_text_and_both_databases(self):
        before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in (self.store, self.candidate)]
        pieces, start = [], 0
        while True:
            status, headers, result = self.request(start=start)
            self.assertEqual(status, 200)
            self.assertEqual(headers["Cache-Control"], "no-store")
            pieces.append(result["text"])
            if result["next"] is None:
                break
            start = result["next"]["start"]
        self.assertEqual("".join(pieces), self.text)
        self.assertEqual(before, [hashlib.sha256(p.read_bytes()).hexdigest() for p in (self.store, self.candidate)])

    def test_each_persisted_gate_denies_independently(self):
        cases = [
            ("no-session", "DELETE FROM access_sessions"),
            ("no-user", "DELETE FROM access_users"),
            ("disabled-user", "UPDATE access_users SET enabled=0"),
            ("session-future", "UPDATE access_sessions SET valid_from=1001"),
            ("session-expired", "UPDATE access_sessions SET valid_until=1000"),
            ("session-revoked", "UPDATE access_sessions SET revoked_at=999"),
            ("no-grant", "DELETE FROM access_grants"),
            ("grant-future", "UPDATE access_grants SET valid_from=1001"),
            ("grant-expired", "UPDATE access_grants SET valid_until=1000"),
            ("grant-revoked", "UPDATE access_grants SET revoked_at=999"),
            ("wrong-user", "UPDATE access_grants SET user_id='someone-else'"),
            ("wrong-group", "UPDATE access_grants SET group_id='someone-else'"),
            ("no-membership", "DELETE FROM access_memberships"),
            ("disabled-membership", "UPDATE access_memberships SET enabled=0"),
            ("wrong-collection", "UPDATE access_grants SET collection_id='other'"),
            ("disabled-collection", "UPDATE access_collections SET enabled=0 WHERE id='c'"),
            ("missing-document", "DELETE FROM access_documents"),
            ("withdrawn-document", "UPDATE access_documents SET withdrawn_at=999"),
            ("different-version", "UPDATE access_documents SET version='" + "b"*64 + "'"),
        ]
        original = self.store.read_bytes()
        for name, statement in cases:
            with self.subTest(gate=name):
                self.store.write_bytes(original)
                self.assertEqual(self.request()[0], 200)
                self.sql(statement)
                status, headers, body = self.request()
                self.assertEqual((status, body), (403, {"error": "ACCESS_DENIED"}))
                self.assertEqual(headers["Cache-Control"], "no-store")
        self.store.write_bytes(original)

    def test_clock_boundaries_inclusive_start_exclusive_end(self):
        for now, expected in [(899,403),(900,200),(1099,200),(1100,403)]:
            with self.subTest(now=now):
                self.now = now
                self.assertEqual(self.request()[0], expected)

    def test_revocation_between_pages_uses_fresh_database_state(self):
        first = self.request()[2]
        self.sql("UPDATE access_grants SET revoked_at=1000")
        self.assertEqual(self.request(start=first["next"]["start"])[0], 403)

    def test_session_revocation_between_pages(self):
        self.assertEqual(self.request()[0], 200)
        self.sql("UPDATE access_sessions SET revoked_at=1000")
        self.assertEqual(self.request(start=301)[0], 403)

    def test_withdrawal_between_pages(self):
        self.assertEqual(self.request()[0], 200)
        self.sql("UPDATE access_documents SET withdrawn_at=1000")
        self.assertEqual(self.request(start=301)[0], 403)

    def test_same_document_different_version_does_not_inherit_permission(self):
        self.assertEqual(self.request(version="b"*64)[0], 403)

    def test_another_document_does_not_inherit_permission(self):
        self.assertEqual(self.request(uid="other")[0], 403)

    def test_headers_cannot_change_server_collection_or_user(self):
        self.sql("UPDATE access_grants SET collection_id='other'")
        self.assertEqual(self.request(extras={"X-Collection":"other","X-User":"u","X-Group":"g"})[0],403)

    def test_no_credential_or_forged_credential_denied(self):
        for token in ["", "x"*43, "bad token", "' OR 1=1 --", self.digest]:
            with self.subTest(kind=len(token)):
                self.assertEqual(self.request(token=token)[0], 403)

    def test_paid_and_pilot_use_same_gate_without_creating_payment(self):
        self.assertEqual(self.request()[0],200)
        self.sql("UPDATE access_grants SET origin='paid'")
        self.assertEqual(self.request()[0],200)
        self.sql("UPDATE access_grants SET revoked_at=1000")
        self.assertEqual(self.request()[0],403)

    def test_store_failure_returns_redacted_503(self):
        self.sql("DROP TABLE access_grants")
        self.assertEqual(self.request()[::2], (503, {"error": "ACCESS_POLICY_UNAVAILABLE"}))

    def test_invalid_clock_fails_closed(self):
        for now in [float("nan"),float("inf"),-1,True,"1000"]:
            with self.subTest(now=repr(now)):
                self.now=now
                self.assertEqual(self.request()[0],503)

    def test_policy_constructor_and_direct_input_validation(self):
        with self.assertRaises(FileNotFoundError):
            SQLiteAccessPolicy(self.root/"absent","c")
        with self.assertRaises(ValueError):
            SQLiteAccessPolicy(self.root,"c")
        with self.assertRaises(ValueError):
            SQLiteAccessPolicy(self.store,"../c")
        with self.assertRaises(TypeError):
            SQLiteAccessPolicy(self.store,"c",None)
        with self.assertRaises(ValueError):
            make_app(self.store,self.store,"c")
        policy=self.app.authorize
        self.assertFalse(policy({"HTTP_AUTHORIZATION":7},"uid",self.sha))
        self.assertFalse(policy({"HTTP_AUTHORIZATION":"Bearer "+self.token},"../uid",self.sha))
        self.assertFalse(policy({"HTTP_AUTHORIZATION":"Bearer "+self.token},"uid","bad"))

    def test_schema_requires_valid_intervals_origin_and_evidence(self):
        for statement in [
            "UPDATE access_grants SET valid_until=valid_from",
            "UPDATE access_grants SET origin='admin'",
            "UPDATE access_grants SET evidence_id=' '",
            "UPDATE access_grants SET issued_by=''",
            "UPDATE access_collections SET approval_evidence=''",
            "UPDATE access_sessions SET token_sha256='bad'",
            "UPDATE access_documents SET version='bad'",
        ]:
            with self.subTest(sql=statement):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.sql(statement)


if __name__ == "__main__":
    unittest.main(verbosity=2)
