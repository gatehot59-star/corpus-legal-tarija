"""tests/test_protected_search.py: contract oracles with explicit SQLite closure."""
from contextlib import closing
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"sistema/api"))
from access_policy import SCHEMA
from isolated_login import LOGIN_SCHEMA
from protected_search import Candidate, ProtectedSearchApp, parse_query, search_reply

NOW = 1000
TOKEN = "A"*43
TEXT_A = "Árbol ficticio\r\nStraße e\u0301 😀. derecho.\r\n"
TEXT_B = "SECRETO derecho jamás visible"


class SearchTests(unittest.TestCase):
    """Independent literal expectations, fake sessions only in the unit fixture."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.candidate = Path(self.tmp.name)/"candidate.db"
        self.store = Path(self.tmp.name)/"policy.db"
        self.a = hashlib.sha256(TEXT_A.encode()).hexdigest()
        self.b = hashlib.sha256(TEXT_B.encode()).hexdigest()
        with closing(sqlite3.connect(self.candidate)) as db, db:
            db.executescript("CREATE TABLE documentos(uid,sha256,fuente_id,fuente_url);"
                            "CREATE TABLE corpus_cleanup_versions(uid,version_sha256,extraction_json);")
            for uid, text, version in (("fixture-a",TEXT_A,self.a),("fixture-b",TEXT_B,self.b)):
                db.execute("INSERT INTO documentos VALUES(?,?,?,?)",
                           (uid,version,"lexivox_nacional","https://example.invalid"))
                db.execute("INSERT INTO corpus_cleanup_versions VALUES(?,?,?)",(uid,version,json.dumps(
                    dict(text=text,text_sha256=version,source_sha256="f"*64,authority="secondary"))))
        with closing(sqlite3.connect(self.store)) as db, db:
            db.executescript(SCHEMA+LOGIN_SCHEMA)
            db.execute("INSERT INTO login_environment VALUES(1,'isolated_test')")
            db.execute("INSERT INTO access_users VALUES('fixture-ana',1)")
            db.execute("INSERT INTO access_sessions VALUES(?,'fixture-ana',900,1100,NULL)",
                       (hashlib.sha256(TOKEN.encode()).hexdigest(),))
            for scope, uid, version in (("scope-a","fixture-a",self.a),("scope-b","fixture-b",self.b)):
                db.execute("INSERT INTO access_collections VALUES(?,1,'fixture')",(scope,))
                db.execute("INSERT INTO access_documents VALUES(?,?,?,NULL)",(scope,uid,version))
            db.execute("INSERT INTO access_memberships VALUES('fixture-ana','group-a',1)")
            db.execute("INSERT INTO access_grants VALUES('g','fixture-ana','group-a','scope-a',"
                       "'pilot',900,1100,NULL,'fixture','fixture')")
        self.catalog = (Candidate("fixture-a",self.a,"scope-a"),Candidate("fixture-b",self.b,"scope-b"))
        self.app = ProtectedSearchApp(self.candidate,self.store,self.catalog,
                                     clock=lambda:NOW,enable_test_login=True)

    def sql(self, sql, args=(), candidate=False):
        with closing(sqlite3.connect(self.candidate if candidate else self.store)) as db, db:
            db.execute(sql,args)

    def call(self, query="q=derecho", **env):
        environ = dict(PATH_INFO="/api/v2/buscar",REQUEST_METHOD="GET",REMOTE_ADDR="127.0.0.1",
                       QUERY_STRING=query,HTTP_AUTHORIZATION="Bearer "+TOKEN, **{})
        environ.update(env)
        captured = []
        body = b"".join(self.app(environ,lambda s,h:captured.append((int(s.split()[0]),dict(h)))))
        return captured[0][0],captured[0][1],json.loads(body) if body else None

    def test_authorization_before_matching_and_no_denied_metadata(self):
        status,headers,body = self.call()
        self.assertEqual(status,200)
        self.assertEqual(set(body),{"schema","environment","total","offset","limit","next_offset","results"})
        self.assertEqual(body["total"],1)
        self.assertEqual(body["results"],[dict(uid="fixture-a",version=self.a,title="Árbol ficticio",
            snippet=TEXT_A,authority="secondary",oficial=False,legal_validity="NOT_MEASURED",
            source_url_scope="current_document")])
        self.assertNotIn("SECRETO",json.dumps(body))
        self.assertEqual(headers["Content-Type"],"application/json; charset=utf-8")

    def test_forbidden_perturbation_invariant(self):
        before = self.call()[2]
        changed = "Texto ficticio reemplazado, derecho derecho"
        version = hashlib.sha256(changed.encode()).hexdigest()
        self.sql("UPDATE documentos SET sha256=? WHERE uid='fixture-b'",(version,),True)
        self.sql("UPDATE corpus_cleanup_versions SET version_sha256=?,extraction_json=? WHERE uid='fixture-b'",
                 (version,json.dumps(dict(text=changed,text_sha256=version,source_sha256="f"*64,authority="secondary"))),True)
        self.sql("UPDATE access_documents SET version=? WHERE uid='fixture-b'",(version,))
        self.app.catalog = (self.catalog[0],Candidate("fixture-b",version,"scope-b"))
        self.assertEqual(before,self.call()[2],"valid denied perturbation cannot change count/order/page")
        self.sql("UPDATE documentos SET fuente_url='changed',fuente_id='bad' WHERE uid='fixture-b'",candidate=True)
        self.sql("UPDATE corpus_cleanup_versions SET extraction_json='not json' WHERE uid='fixture-b'",candidate=True)
        self.assertEqual(before,self.call()[2])

    def test_explicit_version_not_current_fallback(self):
        self.sql("UPDATE documentos SET sha256=? WHERE uid='fixture-a'",("c"*64,),True)
        status, headers, body = self.call()
        self.assertEqual(status,200,"explicit pinned version must survive a current-row change")
        self.assertEqual(body["results"][0]["version"],self.a)
        self.sql("DELETE FROM corpus_cleanup_versions WHERE uid='fixture-a'",candidate=True)
        self.assertEqual(self.call()[::2],(503,{"error":"SEARCH_UNAVAILABLE"}))

    def test_normalization_preserves_original(self):
        for q in ("STRASSE","é","a\u0301rbol","😀"):
            with self.subTest(q=q):
                self.assertEqual(self.call("q="+quote(q))[2]["results"][0]["snippet"],TEXT_A)
        self.assertEqual(self.call("q=missing")[2]["total"],0)
        self.assertEqual(self.call("q=%20derecho%20")[2]["total"],0)

    def test_query_boundaries_and_exact_witnesses(self):
        for q in ("a"*128,"é"*128,"😀"*64,"a"*127+"é"):
            self.assertEqual(parse_query("q="+quote(q))[0],q)
        for q in ("a"*129,"é"*127+"€","😀"*65,""," ","x\n","x\x7f"):
            with self.subTest(invalid=repr(q)),self.assertRaises(ValueError):
                parse_query("q="+quote(q))
        for raw in ("q=%","q=%gg","q=%ff","q=%C3%28","q=x&%71=y","q=x&&limit=1",
                    "q=x&collection=a","q=x&offset=09","q=x&offset=9","q=x&offset=-1",
                    "q=x&limit=0","q=x&limit=6","q=x&limit=01","q=x&offset=1.0",
                    "q=x&offset=+1","q=x&offset=1e0","q=x&limit=1&offset=0&x=y","q=é"):
            with self.subTest(raw=raw):
                self.assertEqual(self.call(raw,HTTP_AUTHORIZATION="")[::2],(400,{"error":"INVALID_QUERY"}))
        for offset in (0,8):
            for limit in (1,5):
                self.assertEqual(parse_query(f"q=x&offset={offset}&limit={limit}")[1:],(offset,limit))
        enc = lambda s:"".join("%"+format(b,"02X") for b in s.encode())
        witness = enc("q")+"="+enc("é"*128)+"&"+enc("offset")+"="+enc("8")+"&"+enc("limit")+"="+enc("5")
        self.assertEqual(len(witness),815)
        self.assertEqual(parse_query(witness),("é"*128,8,5))
        self.assertEqual(self.call("q="+"x"*2046)[::2],(400,{"error":"INVALID_QUERY"}))
        self.assertEqual(self.call("q="+"x"*2047)[::2],(414,{"error":"QUERY_TOO_LONG"}))

    def test_first_error_precedence_and_no_double_decoding(self):
        self.assertEqual(parse_query("q=%2520")[0],"%20")
        self.assertEqual(parse_query("q=a=b")[0],"a=b")
        self.assertEqual(self.call("bad",REQUEST_METHOD="POST",CONTENT_LENGTH="1")[0],405)
        self.assertEqual(self.call("bad",CONTENT_LENGTH="1")[2],{"error":"EMPTY_REQUEST_REQUIRED"})
        self.assertEqual(self.call("q=x",HTTP_TRANSFER_ENCODING="")[2],{"error":"EMPTY_REQUEST_REQUIRED"})
        self.assertEqual(self.call("bad",HTTP_AUTHORIZATION="")[0],400)

    def test_session_and_policy_denials_match_reader(self):
        mutations = [
            "UPDATE access_users SET enabled=0",
            "UPDATE access_sessions SET revoked_at=1000",
            "UPDATE access_sessions SET valid_until=1000",
            "UPDATE access_sessions SET valid_from=1001",
            "UPDATE access_memberships SET enabled=0",
            "UPDATE access_grants SET group_id='wrong'",
            "UPDATE access_grants SET collection_id='unconfigured-scope'",
            "UPDATE access_grants SET valid_until=1000",
            "UPDATE access_grants SET revoked_at=1000",
            "UPDATE access_collections SET enabled=0",
            "UPDATE access_documents SET withdrawn_at=1000",
        ]
        with closing(sqlite3.connect(self.store)) as db:
            original = "\n".join(db.iterdump())
        for statement in mutations:
            with self.subTest(statement=statement):
                self.sql(statement)
                self.assertEqual(self.call()[::2],(403,{"error":"ACCESS_DENIED"}))
                self.assertEqual(self.call("version="+self.a,PATH_INFO="/api/v2/documento/fixture-a/texto")[0],403)
                self.store.unlink()
                with closing(sqlite3.connect(self.store)) as db:
                    db.executescript(original)

    def test_empty_catalog_still_authenticates_and_generic_denial(self):
        self.app.catalog = ()
        for auth in ("","bearer "+TOKEN,"Bearer unknown","Bearer "+"B"*43,"Bearer "+TOKEN):
            self.assertEqual(self.call(HTTP_AUTHORIZATION=auth)[::2],(403,{"error":"ACCESS_DENIED"}))
        self.app.clock = lambda:float("nan")
        self.assertEqual(self.call()[::2],(503,{"error":"ACCESS_POLICY_UNAVAILABLE"}))

    def test_exception_after_allowed_policy_returns_no_partial_content(self):
        def broken(*args):
            raise sqlite3.OperationalError("secret")
        self.app.policies["scope-b"] = broken
        with patch("protected_search.read_version",side_effect=AssertionError("must not read")) as reader:
            self.assertEqual(self.call()[::2],(503,{"error":"ACCESS_POLICY_UNAVAILABLE"}))
            reader.assert_not_called()

    def test_literal_true_only(self):
        self.app.policies["scope-a"] = lambda *args:1
        self.assertEqual(self.call()[0],403)

    def test_integrity_provenance_and_oversize_fail_whole_response(self):
        self.sql("UPDATE corpus_cleanup_versions SET extraction_json='{}' WHERE uid='fixture-a'",candidate=True)
        self.assertEqual(self.call()[::2],(503,{"error":"SEARCH_UNAVAILABLE"}))
        with patch("protected_search.read_version",return_value={"text":"a"*4097,"total_characters":4097,"next":None}):
            self.assertEqual(self.call()[0],503)

    def test_pagination_and_source_scope(self):
        self.assertEqual(self.call("q=derecho&offset=8&limit=1")[2]["results"],[])
        self.assertIsNone(self.call("q=derecho&offset=8&limit=1")[2]["next_offset"])
        self.sql("INSERT INTO access_grants VALUES('g2','fixture-ana','group-a','scope-b','pilot',900,1100,NULL,'fixture','fixture')")
        body = self.call("q=derecho&limit=1")[2]
        self.assertEqual((body["total"],body["next_offset"]),(2,1))
        self.assertEqual(self.call("q=derecho&limit=1&offset=1")[2]["results"][0]["uid"],"fixture-b")

    def test_headers_head_guards_and_bounded_serializer(self):
        for update,status in (({},405),({"REMOTE_ADDR":"203.0.113.5"},403)):
            s,h,b = self.call(REQUEST_METHOD="HEAD",**update)
            self.assertEqual(s,status)
            self.assertIsNone(b)
            self.assertNotIn("Content-Length",h)
            self.assertNotIn("Transfer-Encoding",h)
            self.assertEqual(h["Referrer-Policy"],"no-referrer")
        captured = []
        out = search_reply({},lambda s,h:captured.append((s,dict(h))),200,{"x":"a"*16384})
        self.assertEqual(b"".join(out),b'{"error":"RESPONSE_LIMIT_EXCEEDED"}')
        self.assertTrue(captured[0][0].startswith("503"))
        self.sql("DELETE FROM login_environment")
        self.assertEqual(self.call()[::2],(403,{"error":"ISOLATED_LOGIN_DISABLED"}))

    def test_store_failure_and_unknown_path(self):
        self.assertEqual(self.call(PATH_INFO="/api/v2/buscar/")[0],404)
        self.sql("DROP TABLE login_environment")
        self.assertEqual(self.call()[::2],(503,{"error":"ISOLATION_UNAVAILABLE"}))
        self.assertEqual(self.call(REQUEST_METHOD="HEAD")[0],503)

    def test_catalog_validation(self):
        for catalog in ([self.catalog[0]],self.catalog*5,(self.catalog[0],self.catalog[0]),
                        (Candidate("bad/uid",self.a,"scope-a"),)):
            with self.assertRaises(ValueError):
                ProtectedSearchApp(self.candidate,self.store,catalog)


if __name__ == "__main__":
    unittest.main(verbosity=2)
