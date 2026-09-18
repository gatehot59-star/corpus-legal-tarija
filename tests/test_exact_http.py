"""HTTP regression tests with real WSGI sockets and a synthetic access policy."""
import hashlib
from http.client import HTTPConnection
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.parse import urlencode
from wsgiref.simple_server import make_server, WSGIRequestHandler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sistema/api"))
import exact_http


class QuietHandler(WSGIRequestHandler):
    def log_message(self, *args):
        """Keep the fixture bearer label out of logs."""


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "candidate.db"
        self.text = "Ley 1\n" + "El pago no procede sin autorizacion judicial.\n" * 150
        self.sha = hashlib.sha256(self.text.encode()).hexdigest()
        with sqlite3.connect(self.db) as c:
            c.executescript("CREATE TABLE documentos(uid TEXT,sha256 TEXT,fuente_id TEXT,fuente_url TEXT);"
                            "CREATE TABLE corpus_cleanup_versions(uid TEXT,version_sha256 TEXT,extraction_json TEXT);")
            c.execute("INSERT INTO documentos VALUES(?,?,?,?)",
                      ("uid", self.sha, "lexivox_nacional", "https://example.org/law"))
            c.execute("INSERT INTO corpus_cleanup_versions VALUES(?,?,?)", ("uid", self.sha, json.dumps(
                {"text": self.text, "text_sha256": self.sha, "source_sha256": "a"*64, "authority": "secondary"})))
        self.allowed = {("uid", self.sha)}
        self.calls = []
        self.app = exact_http.ExactReaderApp(self.db, self.policy)
        self.server = make_server("127.0.0.1", 0, self.app, handler_class=QuietHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.01})
        self.thread.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.assertFalse(self.thread.is_alive())

    def policy(self, environ, uid, version):
        """Synthetic fixture only, NOT a deployed authentication implementation."""
        self.calls.append((uid, version))
        return (environ.get("HTTP_AUTHORIZATION") == "Bearer synthetic-fixture"
                and (uid, version) in self.allowed)

    def request(self, query=None, uid="uid", authenticated=True, method="GET", path=None):
        target = path or "/api/v2/documento/" + uid + "/texto?" + (
            urlencode({"version": self.sha}) if query is None else query)
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=2)
        try:
            conn.request(method, target, headers={"Authorization": "Bearer synthetic-fixture"}
                         if authenticated else {"X-User": "admin", "X-Collection": "all"})
            response = conn.getresponse()
            return response.status, dict(response.getheaders()), json.loads(response.read())
        finally:
            conn.close()

    def test_http_preserves_150_phrases_pages_digest_and_database(self):
        before = hashlib.sha256(self.db.read_bytes()).hexdigest()
        pieces = []
        start = 0
        while True:
            status, headers, result = self.request(urlencode({"version": self.sha, "start": start, "limit": 401}))
            self.assertEqual(status, 200)
            self.assertEqual(headers["Cache-Control"], "no-store")
            self.assertNotIn("Access-Control-Allow-Origin", headers)
            self.assertFalse(result["oficial"])
            self.assertEqual(result["source_url_scope"], "current_document")
            pieces.append(result["text"])
            if result["next"] is None:
                break
            self.assertEqual(result["next"]["version"], self.sha)
            start = result["next"]["start"]
        text = "".join(pieces)
        self.assertEqual(text, self.text)
        self.assertEqual(len(text), 6906)
        self.assertEqual(text.count("El pago no procede sin autorizacion judicial."), 150)
        self.assertEqual(hashlib.sha256(text.encode()).hexdigest(), self.sha)
        self.assertEqual(hashlib.sha256(self.db.read_bytes()).hexdigest(), before)

    def test_missing_identity_denied_before_reader_even_with_forged_headers(self):
        with patch.object(exact_http, "read_version", side_effect=AssertionError("must not read")) as reader:
            self.assertEqual(self.request(authenticated=False)[0], 403)
            reader.assert_not_called()

    def test_missing_policy_is_not_public_access(self):
        self.app.authorize = None
        self.assertEqual(self.request()[0], 403)

    def test_truthy_policy_is_not_authorization(self):
        self.app.authorize = lambda *args: "yes"
        self.assertEqual(self.request()[0], 403)

    def test_policy_failure_redacted_and_closed(self):
        def broken(*args):
            raise RuntimeError("private-policy-details")
        self.app.authorize = broken
        status, headers, body = self.request()
        self.assertEqual((status, body), (503, {"error": "ACCESS_POLICY_UNAVAILABLE"}))
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_withdrawal_rechecked_on_next_page(self):
        self.assertEqual(self.request()[0], 200)
        self.allowed.clear()
        self.assertEqual(self.request(urlencode({"version": self.sha, "start": 2600}))[0], 403)
        self.assertEqual(len(self.calls), 2)

    def test_other_uid_and_version_denied(self):
        self.assertEqual(self.request(uid="other")[0], 403)
        self.assertEqual(self.request("version=" + "b"*64)[0], 403)

    def test_authorized_unavailable_version_no_fallback(self):
        self.allowed.add(("uid", "b"*64))
        self.assertEqual(self.request("version=" + "b"*64)[0], 409)

    def test_historical_exact_version_survives_current_change(self):
        with sqlite3.connect(self.db) as c:
            c.execute("UPDATE documentos SET sha256=?", ("b"*64,))
        status, _, result = self.request()
        self.assertEqual(status, 200)
        self.assertFalse(result["is_current"])
        self.assertEqual(result["version"], self.sha)

    def test_invalid_locators_rejected_before_policy(self):
        queries = ["", "version=", "start=2", "version=" + "A"*64,
                   "version=" + self.sha + "&version=" + self.sha,
                   "version=" + self.sha + "&collection=all",
                   "version=" + self.sha + "&limit=10001",
                   "version=" + self.sha + "&start=-1",
                   "version=" + self.sha + "&limit=0",
                   "version=" + self.sha + "&start=1.5",
                   "version=" + self.sha + "&limit=4&start=0&extra=x",
                   "version=" + "x"*2050]
        for query in queries:
            with self.subTest(query=query[:90]):
                self.assertEqual(self.request(query)[0], 400)
        self.assertEqual(self.calls, [])
        self.assertEqual(self.request(uid="bad%2Fuid")[0], 400)

    def test_method_unknown_route_and_out_of_range(self):
        self.assertEqual(self.request(method="POST")[0], 405)
        self.assertEqual(self.request(path="/api/v1/documento/uid")[0], 404)
        self.assertEqual(self.request("version=" + self.sha + "&start=99999")[0], 416)

    def test_tampered_text_never_returned(self):
        with sqlite3.connect(self.db) as c:
            c.execute("UPDATE corpus_cleanup_versions SET extraction_json=?", ('{"text":"tampered"}',))
        status, _, body = self.request()
        self.assertEqual(status, 409)
        self.assertNotIn("text", body)

    def test_database_error_redacted(self):
        self.app.uri = (Path(self.tmp.name) / "missing.db").as_uri() + "?mode=ro"
        self.assertEqual(self.request()[::2], (503, {"error": "DATABASE_UNAVAILABLE"}))

    def test_constructor_requires_existing_file_and_callable_policy(self):
        with self.assertRaises(FileNotFoundError):
            exact_http.ExactReaderApp(Path(self.tmp.name) / "absent.db")
        with self.assertRaises(ValueError):
            exact_http.ExactReaderApp(self.tmp.name)
        with self.assertRaises(TypeError):
            exact_http.ExactReaderApp(self.db, True)

    def test_unexpected_failure_is_redacted(self):
        with patch.object(exact_http, "read_version", side_effect=RuntimeError("private-content")):
            self.assertEqual(self.request()[::2], (500, {"error": "INTERNAL_ERROR"}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
