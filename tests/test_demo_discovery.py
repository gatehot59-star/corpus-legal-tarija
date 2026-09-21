"""tests/test_demo_discovery.py: real raw-wire boundary and CLI lifecycle."""
from contextlib import closing
import json
from pathlib import Path
import select
import socket
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlsplit

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"sistema/api"))
from demo_discovery import CATALOG, TEXTS, initialize, validate

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT/"sistema/api/demo_discovery.py"


class WireTests(unittest.TestCase):
    """Actual wire assertions, not a client HEAD accessor that hides body bytes."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)/"fixture"
        initialize(self.directory)
        self.proc = subprocess.Popen([sys.executable,str(CLI),"serve","--isolated-demo",
            "--directory",str(self.directory)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.addCleanup(self.stop)
        self.assertTrue(select.select([self.proc.stdout],[],[],10)[0],"server startup")
        self.ready = json.loads(self.proc.stdout.readline())
        self.url = self.ready["url"]
        self.port = urlsplit(self.url).port

    def stop(self):
        if self.proc.poll() is None:
            self.proc.terminate()
        stdout,stderr = self.proc.communicate(timeout=5)
        self.assertEqual(self.proc.returncode,0,(stdout,stderr))
        with socket.socket() as sock:
            self.assertNotEqual(sock.connect_ex(("127.0.0.1",self.port)),0,"listener closed")

    def wire(self, method="GET", target="/api/v2/buscar?q=derecho", headers=(), body=b""):
        request = f"{method} {target} HTTP/1.0\r\nHost: 127.0.0.1:{self.port}\r\n"
        request += "Origin: "+self.url+"\r\n"
        request += "".join(k+": "+v+"\r\n" for k,v in headers)
        raw = bytearray()
        with socket.create_connection(("127.0.0.1",self.port),timeout=3) as sock:
            sock.sendall(request.encode("ascii")+b"\r\n"+body)
            while True:
                part = sock.recv(65536)
                if not part:
                    break
                raw.extend(part)
        head,content = bytes(raw).split(b"\r\n\r\n",1)
        lines = head.decode().split("\r\n")
        return int(lines[0].split()[1]),dict(x.split(": ",1) for x in lines[1:]),content

    def sql(self, statement):
        with closing(sqlite3.connect(self.directory/"sessions.db")) as db,db:
            db.execute(statement)

    def login(self, person="ana"):
        body = json.dumps({"username":person,"password":"solo-demo-ficticia"}).encode()
        status,_,data = self.wire("POST","/api/v2/login",
            (("Content-Type","application/json"),("Content-Length",str(len(body)))),body)
        self.assertEqual(status,200)
        return json.loads(data)["access_token"]

    def assert_search(self, result, status, head=False):
        actual,headers,body = result
        self.assertEqual(actual,status)
        for name,value in (("Content-Type","application/json; charset=utf-8"),
                           ("Cache-Control","no-store"),("X-Content-Type-Options","nosniff"),
                           ("Referrer-Policy","no-referrer")):
            self.assertEqual(headers.get(name),value,"required search header "+name)
        if head:
            self.assertEqual(body,b"","HEAD wire content must be absent")
            self.assertNotIn("Content-Length",headers,"HEAD must omit length")
            self.assertNotIn("Transfer-Encoding",headers)
        else:
            self.assertEqual(int(headers["Content-Length"]),len(body))
        self.assertNotIn("Set-Cookie",headers)
        self.assertNotIn("Access-Control-Allow-Origin",headers)

    def test_head_wire_method_isolation_and_predispatch(self):
        result = self.wire("HEAD")
        self.assert_search(result,405,True)
        self.assertEqual(result[1]["Allow"],"GET")
        self.assert_search(self.wire("HEAD",headers=(("Authorization","a"),("Authorization","b"))),403,True)
        self.sql("DELETE FROM login_environment")
        self.assert_search(self.wire("HEAD"),403,True)
        self.sql("DROP TABLE login_environment")
        self.assert_search(self.wire("HEAD"),503,True)

    def test_duplicate_and_host_guards_before_application(self):
        for header in ("Host","Origin","Authorization","Content-Length","Content-Type",
                       "Transfer-Encoding","Sec-Fetch-Site"):
            extra = ((header,"x"),) if header in ("Host","Origin") else ((header,"x"),(header,"y"))
            with self.subTest(header=header):
                self.assert_search(self.wire(headers=extra),403)
                self.assert_search(self.wire("HEAD",headers=extra),403,True)

    def test_login_search_read_save_recheck_and_logout(self):
        token = self.login()
        auth = (("Authorization","Bearer "+token),)
        result = self.wire(headers=auth)
        self.assert_search(result,200)
        data = json.loads(result[2])
        self.assertEqual(data["total"],2)
        self.assertEqual([r["uid"] for r in data["results"]],["fixture-a1","fixture-a2"])
        c = CATALOG[0]
        path = f"/api/v2/documento/{c.uid}/texto?version={c.version}&start=0&limit=1000"
        self.assertEqual(json.loads(self.wire(target=path,headers=auth)[2])["text"],TEXTS[c.uid])
        denied = CATALOG[2]
        self.assertEqual(self.wire(target=f"/api/v2/documento/{denied.uid}/texto?version={denied.version}",headers=auth)[0],403)
        self.sql("UPDATE access_documents SET withdrawn_at=1 WHERE uid='fixture-a1'")
        self.assertEqual(self.wire(target=path,headers=auth)[0],403)
        self.assertEqual(json.loads(self.wire(headers=auth)[2])["total"],1)
        self.assertEqual(self.wire("POST","/api/v2/logout",auth)[0],200)
        self.assert_search(self.wire(headers=auth),403)
        ben = self.login("ben")
        self.assertEqual([r["uid"] for r in json.loads(self.wire(headers=(("Authorization","Bearer "+ben),))[2])["results"]],
                         ["fixture-b1","fixture-b2"])

    def test_framing_methods_and_legacy_allow_unchanged(self):
        self.assert_search(self.wire("OPTIONS"),405)
        self.assertEqual(self.wire("OPTIONS")[1]["Allow"],"GET")
        for route in ("/api/v2/login","/api/v2/logout"):
            status,headers,_ = self.wire("GET",route)
            self.assertEqual(status,405)
            self.assertEqual(headers["Allow"],"POST")
        for h in (("Content-Length","00"),("Content-Length","1"),("Transfer-Encoding","identity")):
            self.assert_search(self.wire(headers=(h,),body=b"x" if h[1]=="1" else b""),400)
        self.assertEqual(self.wire(target="/api/v1/buscar?q=derecho")[0],404)

    def test_page_no_protected_catalog_and_strict_csp(self):
        status,headers,data = self.wire(target="/")
        self.assertEqual(status,200)
        self.assertIn("default-src 'none'",headers["Content-Security-Policy"])
        for c in CATALOG:
            self.assertNotIn(c.uid.encode(),data)
            self.assertNotIn(c.version.encode(),data)
        self.assertNotIn(b"localStorage",data)


class PreflightTests(unittest.TestCase):
    """Exclusive init and source-file protections are independent of HTTP tests."""
    def test_optin_nonoverwrite_and_private_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/"fixture"
            result = subprocess.run([sys.executable,str(CLI),"init","--directory",str(root)],
                                    capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertFalse(root.exists())
            initialize(root)
            self.assertEqual(root.stat().st_mode & 0o777,0o700)
            for name in ("candidate.db","sessions.db"):
                self.assertEqual((root/name).stat().st_mode & 0o777,0o600)
            with self.assertRaises(FileExistsError):
                initialize(root)
            (root/"extra").touch()
            with self.assertRaises(ValueError):
                validate(root)

    def test_manifest_marker_symlink_and_size_rejection(self):
        for variant in ("manifest","marker","symlink","size","permissions"):
            with self.subTest(variant=variant),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)/"fixture";initialize(root)
                if variant in ("manifest","marker"):
                    with closing(sqlite3.connect(root/"sessions.db")) as db,db:
                        db.execute("DELETE FROM "+("discovery_identity" if variant=="manifest" else "login_environment"))
                elif variant=="symlink":
                    original=root/"candidate.db";other=Path(tmp)/"other";original.rename(other);original.symlink_to(other)
                elif variant=="size":
                    with (root/"candidate.db").open("ab") as f:f.write(b"x"*1048576)
                else:
                    (root/"sessions.db").chmod(0o644)
                with self.assertRaises(ValueError):
                    validate(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
