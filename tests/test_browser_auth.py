"""Real CLI/HTTP tests for the opt-in synthetic browser boundary."""
from contextlib import closing
from http.client import HTTPConnection
from pathlib import Path
import hashlib
import json
import selectors
import socket
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sistema/api"))
from isolated_session import IsolatedSessionApp
from isolated_login import IsolatedLoginApp
TEXT = "DEMO FICTICIA, SIN VALOR JURIDICO\nArtículo único: Ñ, ⚖ y e\u0301.\r\n"
VERSION = hashlib.sha256(TEXT.encode()).hexdigest()
PATH = "/api/v2/documento/fixture-demo/texto?version=" + VERSION
CLI = [sys.executable, str(ROOT / "sistema/api/demo_aislada.py")]

class BrowserAuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name) / "fixture"
        r = subprocess.run(CLI + ["init", "--directory", str(cls.root), "--isolated-demo"], capture_output=True, text=True, timeout=15)
        assert r.returncode == 0, r.stderr
        cls.proc = subprocess.Popen(CLI + ["serve", "--directory", str(cls.root), "--isolated-demo", "--browser-spike"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cls.addClassCleanup(cls.stop)
        with selectors.DefaultSelector() as poll:
            poll.register(cls.proc.stdout, selectors.EVENT_READ)
            assert poll.select(15), "CLI readiness timeout"
        cls.ready = json.loads(cls.proc.stdout.readline())
        cls.url = cls.ready["url"]
        cls.port = int(cls.url.rsplit(":", 1)[1])

    @classmethod
    def stop(cls):
        cls.proc.terminate()
        out, err = cls.proc.communicate(timeout=8)
        assert cls.proc.returncode == 0, (out, err)
        with socket.socket() as s:
            assert s.connect_ex(("127.0.0.1", cls.port)) != 0, "listener still open"

    def req(self, method, path, body=None, headers=None):
        h = dict(headers or {})
        if body is not None:
            body = json.dumps(body)
            h["Content-Type"] = "application/json"
        with closing(HTTPConnection("127.0.0.1", self.port, timeout=5)) as c:
            c.request(method, path, body, h)
            r = c.getresponse()
            return r.status, r.read(), dict(r.getheaders())

    def test_01_page_policy(self):
        status, body, h = self.req("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(VERSION.encode(), body)
        self.assertNotIn(b"__FIXTURE_VERSION__", body)
        self.assertEqual(h["Cache-Control"], "no-store")
        self.assertIn("frame-ancestors", h["Content-Security-Policy"])
        self.assertNotIn("unsafe-inline", h["Content-Security-Policy"])
        self.assertNotIn("Access-Control-Allow-Origin", h)
        self.assertEqual(self.req("GET", "/?anything=1")[0], 400)

    def test_02_negative_origin_matrix(self):
        for origin in ("null", "", "http://evil.invalid", self.url + "/", self.url + ".evil", "https://" + self.url[7:], self.url.replace("127.0.0.1", "localhost")):
            for path, method in (("/", "GET"), ("/api/v2/login", "POST"), ("/api/v2/logout", "POST"), (PATH, "GET")):
                with self.subTest(origin=origin, path=path):
                    self.assertEqual(self.req(method, path, headers={"Origin": origin})[0], 403)
        for path in ("/api/v2/login", "/api/v2/logout"):
            self.assertEqual(self.req("POST", path)[0], 403)
        self.assertEqual(self.req("GET", "/", headers={"Host": "evil.invalid", "Origin": self.url})[0], 403)
        self.assertEqual(self.req("GET", "/", headers={"Sec-Fetch-Site": "cross-site"})[0], 403)
        self.assertEqual(self.req("OPTIONS", "/api/v2/login", headers={"Origin": "http://evil.invalid"})[0], 403)
        self.assertEqual(self.req("GET", PATH)[0], 403)

    def test_03_lifecycle(self):
        status, body, _ = self.req("POST", "/api/v2/login", {"username": "ana", "password": "solo-demo-ficticia"}, {"Origin": self.url})
        self.assertEqual(status, 200)
        token = json.loads(body)["access_token"]
        h = {"Authorization": "Bearer " + token, "Origin": self.url}
        self.assertEqual(json.loads(self.req("GET", PATH, headers=h)[1])["text"], TEXT)
        status, body, _ = self.req("POST", "/api/v2/logout", headers=h)
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)["logged_out"])
        self.assertEqual(self.req("GET", PATH, headers=h)[0], 403)
        with closing(sqlite3.connect(self.root / "sessions.db")) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM access_sessions WHERE revoked_at IS NOT NULL").fetchone(), (1,))

    def test_04_default_app_unchanged(self):
        app = IsolatedSessionApp(self.root / "candidate.db", self.root / "sessions.db", "fixture-demo", enable_test_login=True)
        self.assertIsNone(app.browser_origin)
        self.assertEqual(app.login_request({"REQUEST_METHOD": "POST", "HTTP_ORIGIN": self.url})[0], 403)
        self.assertEqual(app.logout_request({"REQUEST_METHOD": "POST", "HTTP_ORIGIN": self.url})[0], 403)

    def test_05_invalid_configuration(self):
        for origin in ("http://localhost:80", "https://127.0.0.1:80", "http://127.0.0.1:0", "http://127.0.0.1:65536", "http://127.0.0.1:80/", "http://127.0.0.1:080", "null"):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                IsolatedLoginApp(self.root / "candidate.db", self.root / "sessions.db", "fixture-demo", enable_test_login=True, browser_origin=origin)
        with self.assertRaises(ValueError):
            IsolatedLoginApp(self.root / "candidate.db", self.root / "sessions.db", "fixture-demo", browser_origin=self.url)

    def test_06_duplicate_headers(self):
        for name, value in (("Host", "127.0.0.1:" + str(self.port)), ("Origin", self.url)):
            with self.subTest(name=name), closing(HTTPConnection("127.0.0.1", self.port, timeout=5)) as c:
                c.putrequest("GET", "/", skip_host=True)
                c.putheader("Host", "127.0.0.1:" + str(self.port))
                if name == "Origin":
                    c.putheader(name, value)
                c.putheader(name, value)
                c.endheaders()
                r=c.getresponse()
                self.assertEqual(r.status, 403)
                r.read()

    def test_07_init_optin_rejected(self):
        target = Path(self.tmp.name) / "not-created"
        r = subprocess.run(CLI + ["init", "--directory", str(target), "--isolated-demo", "--browser-spike"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertFalse(target.exists())

if __name__ == "__main__":
    unittest.main(verbosity=2)
