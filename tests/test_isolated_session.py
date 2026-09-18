"""tests/test_isolated_session.py: real loopback logout with fictional fixtures."""
from contextlib import closing
import hashlib
import io
import sqlite3
import unittest
import test_isolated_login as base
from isolated_session import IsolatedSessionApp


class SessionTests(unittest.TestCase):
    setUpClass = classmethod(base.LoginTests.setUpClass.__func__)
    stop = base.LoginTests.stop
    sql = base.LoginTests.sql
    count = base.LoginTests.count
    request = base.LoginTests.request
    read = base.LoginTests.read
    grant = base.LoginTests.grant

    def setUp(self):
        base.LoginTests.setUp(self)
        self.app = IsolatedSessionApp(self.candidate, self.store, "c",
                                     enable_test_login=True, clock=lambda: self.now)
        self.server.set_app(self.app)

    def token(self):
        status, _, body = self.request()
        self.assertEqual(status, 200)
        return body["access_token"]

    def logout(self, token, **kwargs):
        return self.request("POST", "", {"Authorization": "Bearer " + token},
                            "/api/v2/logout", **kwargs)

    def revoked(self, token):
        with closing(sqlite3.connect(self.store)) as db:
            return db.execute("SELECT revoked_at FROM access_sessions WHERE token_sha256=?",
                              (hashlib.sha256(token.encode()).hexdigest(),)).fetchone()[0]

    def test_logout_blocks_next_page_persistently_without_changing_candidate(self):
        token = self.token()
        self.grant()
        before = hashlib.sha256(self.candidate.read_bytes()).hexdigest()
        first = self.read(token)
        self.assertEqual(first[0], 200)
        status, headers, body = self.logout(token)
        self.assertEqual((status, body["logged_out"]), (200, True))
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertNotIn("Set-Cookie", headers)
        self.assertNotIn("Access-Control-Allow-Origin", headers)
        self.assertEqual(self.revoked(token), 1000)
        self.assertEqual(self.read(token, first[2]["next"]["start"])[0], 403)
        self.server.set_app(IsolatedSessionApp(self.candidate, self.store, "c",
                            enable_test_login=True, clock=lambda: self.now))
        self.assertEqual(self.read(token)[0], 403)
        self.assertEqual(before, hashlib.sha256(self.candidate.read_bytes()).hexdigest())

    def test_other_session_same_user_and_other_user_survive(self):
        first, second = self.token(), self.token()
        self.grant()
        other = "Z" * 43
        self.sql("INSERT INTO access_users VALUES('fixture-other',1)")
        self.sql("INSERT INTO access_sessions VALUES(?,'fixture-other',900,3000,NULL)",
                 (hashlib.sha256(other.encode()).hexdigest(),))
        self.sql("INSERT INTO access_memberships VALUES('fixture-other','g',1)")
        self.sql("INSERT INTO access_grants VALUES('other','fixture-other','g','c','pilot',900,3000,NULL,'fixture','fixture')")
        self.assertEqual(self.logout(first)[0], 200)
        self.assertEqual(self.read(first)[0], 403)
        self.assertEqual(self.read(second)[0], 200)
        self.assertEqual(self.read(other)[0], 200)

    def test_repeat_and_unknown_do_not_change_first_revocation_or_create_session(self):
        token = self.token()
        expected = self.logout(token)[2]
        self.now += 10
        self.assertEqual(self.logout(token)[2], expected)
        self.assertEqual(self.logout("Q" * 43)[2], expected)
        self.assertEqual(self.revoked(token), 1000)
        self.assertEqual(self.count("access_sessions"), 1)
        self.assertEqual(self.count("access_grants"), 0)

    def test_expired_disabled_and_grantless_session_can_logout(self):
        token = self.token()
        self.now = 2000
        self.sql("UPDATE access_users SET enabled=0")
        self.assertEqual(self.logout(token)[0], 200)
        self.assertEqual(self.revoked(token), 2000)

    def test_malformed_requests_do_not_revoke(self):
        token = self.token()
        auth = {"Authorization": "Bearer " + token}
        cases = [
            ("GET", "", auth, "/api/v2/logout", 405),
            ("POST", "x", auth, "/api/v2/logout", 400),
            ("POST", "", auth, "/api/v2/logout?token=x", 400),
            ("POST", "", {**auth, "Origin": "https://example.org"}, "/api/v2/logout", 403),
            ("POST", "", {"Authorization": "Bearer bad"}, "/api/v2/logout", 401),
            ("POST", "", {"Content-Type": "application/json"}, "/api/v2/logout", 401),
        ]
        for method, body, headers, path, status in cases:
            with self.subTest(status=status, path=path, method=method):
                self.assertEqual(self.request(method, body, headers, path)[0], status)
                self.assertIsNone(self.revoked(token))

    def test_marker_pause_and_remote_guard_prevent_logout(self):
        token = self.token()
        self.sql("DELETE FROM login_environment")
        self.assertEqual(self.logout(token)[0], 403)
        self.assertIsNone(self.revoked(token))
        self.sql("INSERT INTO login_environment VALUES(1,'isolated_test')")
        statuses = []
        self.app({"REMOTE_ADDR": "192.0.2.1", "PATH_INFO": "/api/v2/logout"},
                 lambda status, headers: statuses.append(status))
        self.assertTrue(statuses[0].startswith("403"))
        self.assertIsNone(self.revoked(token))
        self.app.enabled = False
        self.assertEqual(self.logout(token)[0], 403)

    def test_invalid_clock_and_missing_table_return_no_false_success(self):
        token = self.token()
        for value in (float("nan"), -1, True):
            self.now = value
            self.assertEqual(self.logout(token)[0], 503)
            self.assertIsNone(self.revoked(token))
        self.now = 1000
        self.sql("DROP TABLE access_sessions")
        self.assertEqual(self.logout(token)[0], 503)

    def test_backward_clock_cannot_resurrect_revoked_session(self):
        token = self.token()
        self.grant()
        self.now = 999
        self.assertEqual(self.logout(token)[0], 200)
        self.now = 1000
        self.assertEqual(self.read(token)[0], 403)

    def test_direct_wsgi_rejects_empty_origin_transfer_and_ambiguous_auth(self):
        token = self.token()
        valid = {"REMOTE_ADDR": "127.0.0.1", "PATH_INFO": "/api/v2/logout",
                 "REQUEST_METHOD": "POST", "CONTENT_LENGTH": "0",
                 "HTTP_AUTHORIZATION": "Bearer " + token, "wsgi.input": io.BytesIO()}
        for field, value, expected in [("HTTP_ORIGIN", "", 403),
                ("HTTP_TRANSFER_ENCODING", "", 403),
                ("HTTP_AUTHORIZATION", ["Bearer " + token], 401),
                ("CONTENT_LENGTH", "00", 400)]:
            statuses = []
            self.app({**valid, field: value}, lambda status, headers: statuses.append(status))
            self.assertTrue(statuses[0].startswith(str(expected)))
            self.assertIsNone(self.revoked(token))

    def test_nonfixture_session_not_modified(self):
        token = "R" * 43
        self.sql("INSERT INTO access_users VALUES('nonfixture',1)")
        self.sql("INSERT INTO access_sessions VALUES(?,'nonfixture',900,3000,NULL)",
                 (hashlib.sha256(token.encode()).hexdigest(),))
        self.assertEqual(self.logout(token)[0], 200)
        self.assertIsNone(self.revoked(token))


if __name__ == "__main__":
    unittest.main(verbosity=2)
