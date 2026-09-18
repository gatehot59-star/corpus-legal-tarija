"""End-to-end isolated login: temporary fictional accounts only; no token logs."""
from http.client import HTTPConnection
import hashlib
import io
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

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"sistema/api"))
from access_policy import SCHEMA
from isolated_login import LOGIN_SCHEMA, IsolatedLoginApp, password_digest


class QuietHandler(WSGIRequestHandler):
    def log_message(self, *args):
        """No password, token, or request logging in test output."""


class LoginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password = "fictional-test-password-never-used-in-production"
        cls.salt = b"fictional-salt01"
        cls.digest = password_digest(cls.password, cls.salt)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = Path(self.tmp.name)/"fixture-store.db"
        self.candidate = Path(self.tmp.name)/"fixture-candidate.db"
        self.text = "Fictional legal text.\n"*150
        self.sha = hashlib.sha256(self.text.encode()).hexdigest()
        self.now = 1000
        with sqlite3.connect(self.store) as db:
            db.executescript(SCHEMA+LOGIN_SCHEMA)
            db.execute("INSERT INTO login_environment VALUES(1,'isolated_test')")
            db.execute("INSERT INTO access_users VALUES('fixture-user',1)")
            db.execute("INSERT INTO login_passwords VALUES(?,?,?,?)",
                       ("fixture-user","fixture-user",self.salt,self.digest))
            db.execute("INSERT INTO access_collections VALUES('c',1,'fictional-approval')")
            db.execute("INSERT INTO access_memberships VALUES('fixture-user','g',1)")
            db.execute("INSERT INTO access_documents VALUES('c','uid',?,NULL)",(self.sha,))
        with sqlite3.connect(self.candidate) as db:
            db.executescript("CREATE TABLE documentos(uid,sha256,fuente_id,fuente_url);"
                            "CREATE TABLE corpus_cleanup_versions(uid,version_sha256,extraction_json);")
            db.execute("INSERT INTO documentos VALUES(?,?,?,?)",("uid",self.sha,"lexivox_nacional","https://example.org/fixture"))
            db.execute("INSERT INTO corpus_cleanup_versions VALUES(?,?,?)",("uid",self.sha,json.dumps({
                "text":self.text,"text_sha256":self.sha,"source_sha256":"a"*64,"authority":"secondary"})))
        self.app = IsolatedLoginApp(self.candidate,self.store,"c",enable_test_login=True,clock=lambda:self.now)
        self.server = make_server("127.0.0.1",0,self.app,handler_class=QuietHandler)
        self.thread = threading.Thread(target=self.server.serve_forever,kwargs={"poll_interval":0.01})
        self.thread.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=2)
        self.assertFalse(self.thread.is_alive())

    def sql(self, statement, params=()):
        with sqlite3.connect(self.store) as db:
            db.execute(statement,params)

    def count(self, table):
        with sqlite3.connect(self.store) as db:
            return db.execute("SELECT COUNT(*) FROM "+table).fetchone()[0]

    def request(self, method="POST", body=None, headers=None, path="/api/v2/login"):
        conn = HTTPConnection("127.0.0.1",self.server.server_port,timeout=5)
        if body is None:
            body = json.dumps({"username":"fixture-user","password":self.password})
        try:
            conn.request(method,path,body,headers or {"Content-Type":"application/json"})
            response = conn.getresponse()
            return response.status,dict(response.getheaders()),json.loads(response.read())
        finally:
            conn.close()

    def read(self, token, start=0):
        return self.request("GET","",{"Authorization":"Bearer "+token},
                            "/api/v2/documento/uid/texto?"+urlencode({"version":self.sha,"start":start}))

    def grant(self):
        self.sql("INSERT INTO access_grants VALUES('grant','fixture-user','g','c','pilot',900,3000,NULL,'fictional-issuer','fictional-evidence')")

    def test_login_is_not_a_grant_and_token_reads_only_after_explicit_fixture_grant(self):
        before = hashlib.sha256(self.candidate.read_bytes()).hexdigest()
        status,headers,body = self.request()
        self.assertEqual(status,200)
        self.assertEqual(headers["Cache-Control"],"no-store")
        self.assertNotIn("Set-Cookie",headers)
        self.assertNotIn("Access-Control-Allow-Origin",headers)
        token=body["access_token"]
        self.assertTrue(len(token)==43)
        self.assertEqual(self.count("access_grants"),0)
        self.assertEqual(self.read(token)[0],403)
        self.grant()
        first=self.read(token)
        self.assertEqual(first[0],200)
        rest=self.read(token,first[2]["next"]["start"])
        self.assertTrue(first[2]["text"]+rest[2]["text"]==self.text)
        with sqlite3.connect(self.store) as db:
            row=db.execute("SELECT token_sha256,valid_until FROM access_sessions").fetchone()
        self.assertTrue(row[0]==hashlib.sha256(token.encode()).hexdigest())
        self.assertEqual(row[1],1900)
        self.assertTrue(token.encode() not in self.store.read_bytes())
        self.assertTrue(self.password.encode() not in self.store.read_bytes())
        self.assertEqual(before,hashlib.sha256(self.candidate.read_bytes()).hexdigest())

    def test_wrong_unknown_and_disabled_have_same_generic_error_and_no_sessions(self):
        for username,password,disabled in [("fixture-user","wrong",False),("absent","wrong",False),
                                           ("fixture-user",self.password,True)]:
            if disabled:self.sql("UPDATE access_users SET enabled=0")
            response=self.request(body=json.dumps({"username":username,"password":password}))
            self.assertEqual(response[0],401)
            self.assertEqual(response[2],{"error":"INVALID_CREDENTIALS"})
            self.assertEqual(self.count("access_sessions"),0)

    def test_default_disabled_and_missing_marker_issue_nothing(self):
        self.app.enabled=False
        self.assertEqual(self.request()[0],403)
        self.app.enabled=True
        self.sql("DELETE FROM login_environment")
        self.assertEqual(self.request()[0],403)
        self.assertEqual(self.count("access_sessions"),0)
        disabled=IsolatedLoginApp(self.candidate,self.store,"c")
        self.assertFalse(disabled.enabled)

    def test_nonloopback_and_forwarded_headers_cannot_enable_login(self):
        for remote in ["203.0.113.4","", "not-an-ip"]:
            env={"REMOTE_ADDR":remote,"PATH_INFO":"/api/v2/login","HTTP_X_FORWARDED_FOR":"127.0.0.1"}
            status=[]
            self.app(env,lambda s,h:status.append(s))
            self.assertTrue(status[0].startswith("403"))
        self.assertEqual(self.count("access_sessions"),0)

    def test_malformed_requests_do_not_create_sessions(self):
        cases=[("GET","{}",None,405),("POST","{}",None,400),
               ("POST",'{"username":"a","username":"b","password":"x"}',None,400),
               ("POST",'{"username":"fixture-user","password":7}',None,400),
               ("POST",'{"username":"../user","password":"x"}',None,400),
               ("POST",'{"username":"fixture-user","password":""}',None,400),
               ("POST","null",None,400),("POST","{",None,400),
               ("POST","{}",{"Content-Type":"text/plain"},415),
               ("POST","{}",{"Content-Type":"application/json","Origin":"https://example.org"},403),
               ("POST","x"*4097,None,400)]
        for method,body,headers,expected in cases:
            with self.subTest(expected=expected,method=method,length=len(body)):
                self.assertEqual(self.request(method,body,headers)[0],expected)
        self.assertEqual(self.count("access_sessions"),0)

    def test_persistent_global_budget_blocks_sixth_and_expires(self):
        self.sql("INSERT INTO login_budget VALUES(1,1000,4)")
        self.assertEqual(self.request(body=json.dumps({"username":"absent","password":"wrong"}))[0],401)
        with patch("isolated_login.password_digest",side_effect=AssertionError("must throttle before KDF")):
            self.assertEqual(self.request()[0],429)
        self.now=1060
        self.assertEqual(self.request()[0],200)

    def test_clock_rollback_or_nonfinite_fails_closed(self):
        self.sql("INSERT INTO login_budget VALUES(1,1001,0)")
        self.assertEqual(self.request()[0],503)
        self.now=float("nan")
        self.assertEqual(self.request()[0],503)
        self.assertEqual(self.count("access_sessions"),0)

    def test_session_expires_and_revocation_blocks_subsequent_reads(self):
        token=self.request()[2]["access_token"]
        self.grant()
        self.assertEqual(self.read(token)[0],200)
        self.now=1900
        self.assertEqual(self.read(token)[0],403)
        self.now=1000
        self.sql("UPDATE access_sessions SET revoked_at=1000")
        self.assertEqual(self.read(token)[0],403)

    def test_new_login_uses_new_token_and_never_reuses_supplied_one(self):
        first=self.request()[2]["access_token"]
        second=self.request(headers={"Content-Type":"application/json","Authorization":"Bearer "+first})[2]["access_token"]
        self.assertFalse(first==second)
        self.assertEqual(self.count("access_sessions"),2)

    def test_store_failure_does_not_leak_details_or_create_session(self):
        self.sql("DROP TABLE login_passwords")
        self.assertEqual(self.request()[::2],(503,{"error":"LOGIN_UNAVAILABLE"}))
        self.assertEqual(self.count("access_sessions"),0)

    def test_kdf_and_parser_bounds(self):
        for password,salt in [("",self.salt),("x"*1025,self.salt),(None,self.salt),("x",b"bad")]:
            with self.assertRaises(ValueError):password_digest(password,salt)
        self.assertFalse(password_digest(self.password,b"another-salt0001")==self.digest)
        base={"REQUEST_METHOD":"POST","CONTENT_TYPE":"application/json","CONTENT_LENGTH":"4",
              "wsgi.input":io.BytesIO(b"{}")}
        self.assertEqual(self.app.login_request(base)[0],400)
        base["HTTP_TRANSFER_ENCODING"]="chunked"
        self.assertEqual(self.app.login_request(base)[0],403)

    def test_only_fixture_identities_can_be_provisioned(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.sql("INSERT INTO login_passwords VALUES(?,?,?,?)",("real","real-user",self.salt,self.digest))


if __name__=="__main__":unittest.main(verbosity=2)
