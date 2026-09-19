"""Exercise the actual CLI in subprocesses, HTTP and direct SQLite oracles."""
from contextlib import closing, contextmanager
import hashlib
from http.client import HTTPConnection
import json
import os
from pathlib import Path
import select
import signal
import socket
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "sistema/api/demo_aislada.py"
sys.path.insert(0, str(CLI.parent))
import demo_aislada as demo

# Expected content is written independently of launcher constants.
EXPECTED = "DEMO FICTICIA, SIN VALOR JURIDICO\nArtículo único: Ñ, ⚖ y e\u0301.\r\n"
VERSION = hashlib.sha256(EXPECTED.encode("utf-8")).hexdigest()


class DemoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="corpus-demo-test-")
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.directory = self.home / "demo"

    def cli(self, action, *extra, opt=True, directory=None):
        cmd = [sys.executable, str(CLI), action, "--directory",
               str(directory or self.directory), *extra]
        if opt:
            cmd.append("--isolated-demo")
        return subprocess.run(cmd, capture_output=True, text=True, timeout=15)

    def init(self):
        result = self.cli("init")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["version"], VERSION)

    def sql(self, statement, args=()):
        with closing(sqlite3.connect(self.directory / "sessions.db")) as db, db:
            return db.execute(statement, args).fetchall()

    @contextmanager
    def server(self, *extra):
        command = [sys.executable, str(CLI), "serve", "--directory",
                   str(self.directory), "--isolated-demo", *extra]
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True)
        port = None
        try:
            self.assertTrue(select.select([p.stdout], [], [], 10)[0], "startup timeout")
            line = p.stdout.readline()
            self.assertTrue(line, "no ready event")
            ready = json.loads(line)
            self.assertEqual(ready["event"], "ready")
            url = urlsplit(ready["url"])
            self.assertEqual(url.hostname, "127.0.0.1")
            self.assertEqual(ready["pid"], p.pid)
            port = url.port
            yield p, port
        finally:
            if p.poll() is None:
                p.send_signal(signal.SIGTERM)
            try:
                out, err = p.communicate(timeout=8)
            except subprocess.TimeoutExpired:
                p.kill()
                out, err = p.communicate(timeout=3)
                self.fail("launcher did not terminate: " + err)
            self.assertEqual(p.returncode, 0, err)
            self.assertNotIn("solo-demo-ficticia", out + err)
            self.assertNotIn("Bearer ", out + err)
            if port:
                with closing(socket.socket()) as sock:
                    self.assertNotEqual(sock.connect_ex(("127.0.0.1", port)), 0)

    def request(self, port, method, path, token=None, body=None, headers=None):
        hs = dict(headers or {})
        if token:
            hs["Authorization"] = "Bearer " + token
        if body is not None:
            hs["Content-Type"] = "application/json"
        conn = HTTPConnection("127.0.0.1", port, timeout=5)
        try:
            conn.request(method, path, json.dumps(body) if body is not None else "", hs)
            response = conn.getresponse()
            status = response.status
            data = json.loads(response.read())
            self.assertEqual(response.getheader("Cache-Control"), "no-store")
            return status, data
        finally:
            conn.close()

    def login(self, port, user="ana"):
        status, data = self.request(port, "POST", "/api/v2/login",
                                   body={"username": user, "password": "solo-demo-ficticia"})
        self.assertEqual(status, 200, data)
        return data["access_token"]

    def read(self, port, token, start=0):
        return self.request(port, "GET", "/api/v2/documento/fixture-demo/texto"
                            "?version=" + VERSION + "&limit=13&start=" + str(start), token)

    def test_cli_lifecycle_pagination_selective_logout_restart(self):
        self.init()
        before = (self.directory / "candidate.db").read_bytes()
        with self.server() as (first, port):
            token = self.login(port)
            other = self.login(port)
            second_user = self.login(port, "ben")
            text, start = "", 0
            for _ in range(30):
                status, data = self.read(port, token, start)
                self.assertEqual(status, 200, data)
                text += data["text"]
                if data["next"] is None:
                    break
                start = data["next"]["start"]
            else:
                self.fail("pagination did not end")
            self.assertEqual(text, EXPECTED)
            self.assertEqual(self.request(port, "POST", "/api/v2/logout", token)[0], 200)
            self.assertEqual(self.read(port, token)[0], 403)
            self.assertEqual(self.read(port, other)[0], 200)
            self.assertEqual(self.read(port, second_user)[0], 200)
            row = self.sql("SELECT revoked_at FROM access_sessions WHERE token_sha256=?",
                           (hashlib.sha256(token.encode()).hexdigest(),))
            self.assertIsNotNone(row[0][0])
            self.assertEqual(self.request(port, "POST", "/api/v2/logout", token)[0], 200)
            self.assertEqual(self.sql("SELECT revoked_at FROM access_sessions WHERE token_sha256=?",
                             (hashlib.sha256(token.encode()).hexdigest(),)), row)
        with self.server() as (second, port):
            self.assertNotEqual(first.pid, second.pid)
            self.assertEqual(self.read(port, token)[0], 403)
            self.assertEqual(self.read(port, other)[0], 200)
            self.assertEqual(self.read(port, second_user)[0], 200)
        self.assertEqual((self.directory / "candidate.db").read_bytes(), before)

    def test_login_does_not_restore_removed_grant(self):
        self.init()
        self.sql("UPDATE access_grants SET revoked_at=1 WHERE id='ana'")
        with self.server() as (_, port):
            self.assertEqual(self.read(port, self.login(port))[0], 403)
            self.assertEqual(self.read(port, self.login(port, "ben"))[0], 200)

    def test_origin_host_and_marker_fail_closed(self):
        self.init()
        with self.server() as (_, port):
            token = self.login(port)
            for headers in ({"Origin": "http://evil.invalid"}, {"Origin": ""},
                            {"Host": "evil.invalid"}, {"Host": "localhost:" + str(port)}):
                self.assertEqual(self.request(port, "POST", "/api/v2/logout",
                                             token, headers=headers)[0], 403)
            self.assertEqual(self.read(port, token)[0], 200)
            self.sql("DELETE FROM login_environment")
            self.assertEqual(self.read(port, token)[0], 403)
            self.assertEqual(self.request(port, "POST", "/api/v2/logout", token)[0], 403)
            self.assertEqual(self.sql("SELECT revoked_at FROM access_sessions"), [(None,)])

    def test_init_requires_opt_in_without_writes(self):
        result = self.cli("init", opt=False)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.directory.exists())

    def test_serve_requires_opt_in_without_mutation(self):
        self.init()
        before = {p.name: p.read_bytes() for p in self.directory.iterdir()}
        self.assertEqual(self.cli("serve", opt=False).returncode, 2)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.directory.iterdir()})

    def test_init_never_overwrites_existing_directory(self):
        self.init()
        before = {p.name: p.read_bytes() for p in self.directory.iterdir()}
        self.assertEqual(self.cli("init").returncode, 2)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.directory.iterdir()})

    def test_missing_store_does_not_create_it(self):
        self.directory.mkdir(mode=0o700)
        self.assertEqual(self.cli("serve").returncode, 2)
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_symlink_root_and_parent_rejected(self):
        self.init()
        alias = self.home / "alias"
        alias.symlink_to(self.directory, target_is_directory=True)
        self.assertEqual(self.cli("serve", directory=alias).returncode, 2)
        self.assertEqual(self.cli("init", directory=alias / "child").returncode, 2)
        self.assertFalse((self.directory / "child").exists())

    def test_linked_and_nonregular_files_rejected(self):
        self.init()
        candidate = self.directory / "candidate.db"
        original = self.home / "original.db"
        candidate.rename(original)
        candidate.symlink_to(original)
        self.assertEqual(self.cli("serve").returncode, 2)
        candidate.unlink()
        os.link(original, candidate)
        self.assertEqual(self.cli("serve").returncode, 2)
        candidate.unlink()
        os.mkfifo(candidate, 0o600)
        self.assertEqual(self.cli("serve").returncode, 2)

    def test_private_permissions_required(self):
        self.init()
        self.assertEqual(self.directory.stat().st_mode & 0o777, 0o700)
        self.directory.chmod(0o755)
        self.assertEqual(self.cli("serve").returncode, 2)
        self.directory.chmod(0o700)
        (self.directory / "sessions.db").chmod(0o644)
        self.assertEqual(self.cli("serve").returncode, 2)

    def test_missing_clock_no_automatic_migration(self):
        self.init()
        self.sql("DROP TABLE login_clock")
        before = (self.directory / "sessions.db").read_bytes()
        self.assertEqual(self.cli("serve").returncode, 2)
        self.assertEqual((self.directory / "sessions.db").read_bytes(), before)

    def test_foreign_candidate_rejected_without_writes(self):
        self.init()
        path = self.directory / "candidate.db"
        with closing(sqlite3.connect(path)) as db, db:
            db.execute("UPDATE documentos SET fuente_url='https://real.invalid/not-demo'")
        before = path.read_bytes()
        self.assertEqual(self.cli("serve").returncode, 2)
        self.assertEqual(path.read_bytes(), before)

    def test_tampered_text_rejected(self):
        self.init()
        with closing(sqlite3.connect(self.directory / "candidate.db")) as db, db:
            db.execute("UPDATE corpus_cleanup_versions SET extraction_json='{}'")
        self.assertEqual(self.cli("serve").returncode, 2)

    def test_unmarked_store_rejected(self):
        self.init()
        self.sql("DELETE FROM demo_identity")
        self.assertEqual(self.cli("serve").returncode, 2)

    def test_unexpected_sidecar_rejected(self):
        self.init()
        (self.directory / "candidate.db-wal").write_text("not a live journal")
        self.assertEqual(self.cli("serve").returncode, 2)

    def test_external_host_option_and_invalid_ports_rejected(self):
        for flags in (("--host", "0.0.0.0"), ("--port", "-1"), ("--port", "65536")):
            self.assertEqual(self.cli("serve", *flags).returncode, 2)
            self.assertFalse(self.directory.exists())

    def test_occupied_port_fails_without_state_reset(self):
        self.init()
        self.sql("UPDATE access_grants SET revoked_at=1 WHERE id='ana'")
        before = (self.directory / "sessions.db").read_bytes()
        with closing(socket.socket()) as sock:
            sock.bind(("127.0.0.1", 0))
            sock.listen()
            self.assertEqual(self.cli("serve", "--port", str(sock.getsockname()[1])).returncode, 2)
        self.assertEqual((self.directory / "sessions.db").read_bytes(), before)

    def test_help_executes(self):
        result = subprocess.run([sys.executable, str(CLI), "--help"],
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--isolated-demo", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
