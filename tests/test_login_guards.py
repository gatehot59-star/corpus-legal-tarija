"""Regression for SOL marker and Astra clock findings; fictional stores only."""
import json
import unittest
import test_isolated_login as baseline
from isolated_login import IsolatedLoginApp


class GuardTests(baseline.LoginTests):
    def test_marker_removal_blocks_existing_session_without_revoking_it(self):
        token = self.request()[2]["access_token"]
        self.grant()
        self.assertEqual(self.read(token)[0], 200)
        self.sql("DELETE FROM login_environment")
        self.assertEqual(self.read(token)[0], 403)
        self.assertEqual(self.request()[0], 403)
        self.sql("INSERT INTO login_environment VALUES(1,'isolated_test')")
        self.assertEqual(self.read(token)[0], 200)

    def test_missing_marker_table_blocks_read_with_generic_error(self):
        token = self.request()[2]["access_token"]
        self.grant()
        self.assertEqual(self.read(token)[0], 200)
        self.sql("DROP TABLE login_environment")
        result = self.read(token)
        self.assertEqual(result[0], 503)
        self.assertEqual(result[2], {"error": "ISOLATION_UNAVAILABLE"})

    def test_backward_clock_inside_window_does_not_issue_session(self):
        for now, expected, sessions in [(2000,200,1),(2050,200,2),(2049,503,2),(1999,503,2)]:
            with self.subTest(now=now):
                self.now = now
                self.assertEqual(self.request()[0], expected)
                self.assertEqual(self.count("access_sessions"), sessions)

    def test_fractional_rollback_and_restart_keep_high_water_mark(self):
        self.now = 1000.8
        self.assertEqual(self.request()[0], 200)
        self.app.clock = lambda: self.now
        self.server.set_app(IsolatedLoginApp(self.candidate,self.store,"c",
                            enable_test_login=True,clock=lambda:self.now))
        self.now = 1000.7
        self.assertEqual(self.request()[0], 503)
        self.assertEqual(self.count("access_sessions"), 1)
        self.now = 1000.8
        self.assertEqual(self.request()[0], 200)

    def test_failed_password_also_advances_observed_clock(self):
        self.now = 1050
        self.assertEqual(self.request(body=json.dumps({"username":"fixture-user","password":"wrong"}))[0],401)
        self.now = 1049
        self.assertEqual(self.request()[0],503)
        self.assertEqual(self.count("access_sessions"),0)

    def test_missing_clock_table_fails_closed_without_automatic_migration(self):
        self.sql("DROP TABLE login_clock")
        self.assertEqual(self.request()[0],503)
        self.assertEqual(self.count("access_sessions"),0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
