"""sistema/django_app/corpus/tests/test_recovery.py: stale policy/session adversaries."""
import hashlib
import sqlite3
from pathlib import Path
from contextlib import closing
from django.db import connection
from django.core.management.base import CommandError
from corpus.management.commands.recover_snapshot import recover, database
from .test_access import FixtureBase


class RecoveryTests(FixtureBase):
    """Use real serialized operational databases, not mocked success receipts."""
    def setUp(self):
        super().setUp()
        self.login()
        self.app.save_reference(self.p, self.locator)
        self.backup = Path(self.temp.name) / "backup.sqlite3"
        self.backup.write_bytes(connection.connection.serialize())
        self.digest = hashlib.sha256(self.backup.read_bytes()).hexdigest()
        self.target = Path(self.temp.name) / "restored.sqlite3"

    def test_quarantine_purges_sessions_and_disables_stale_authority(self):
        receipt = recover(self.backup, self.digest, self.target, 2)
        self.assertTrue(receipt["quarantined"])
        self.assertFalse(receipt["serve_authorized"])
        with closing(sqlite3.connect(self.target)) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM django_session").fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT enabled FROM corpus_collection").fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT enabled FROM corpus_membership").fetchone()[0], 0)
            self.assertIsNotNone(db.execute("SELECT revoked_at FROM corpus_accessgrant").fetchone()[0])
            self.assertEqual(db.execute("SELECT session_epoch FROM corpus_policystate").fetchone()[0], 2)
        self.assertEqual(hashlib.sha256(self.backup.read_bytes()).hexdigest(), self.digest)

    def test_current_policy_reconciliation_preserves_withdrawal_and_revocation(self):
        authority = Path(self.temp.name) / "current.sqlite3"
        with closing(database(self.backup.read_bytes())) as db:
            db.execute("UPDATE corpus_policystate SET revision=2")
            db.execute("UPDATE corpus_accessgrant SET revoked_at=CURRENT_TIMESTAMP")
            db.execute("UPDATE corpus_locator SET withdrawn_at=CURRENT_TIMESTAMP")
            db.execute("DELETE FROM corpus_savedreference")
            db.commit()
            authority.write_bytes(db.serialize())
        authority_digest = hashlib.sha256(authority.read_bytes()).hexdigest()
        receipt = recover(self.backup, self.digest, self.target, 2, authority, authority_digest)
        self.assertFalse(receipt["quarantined"])
        self.assertEqual(receipt["imported"], 1)
        with closing(sqlite3.connect(self.target)) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM django_session").fetchone()[0], 0)
            self.assertIsNotNone(db.execute("SELECT revoked_at FROM corpus_accessgrant").fetchone()[0])
            self.assertIsNotNone(db.execute("SELECT withdrawn_at FROM corpus_locator").fetchone()[0])
            self.assertEqual(db.execute("SELECT session_epoch FROM corpus_policystate").fetchone()[0], 2)
        self.assertEqual(hashlib.sha256(authority.read_bytes()).hexdigest(), authority_digest)

    def test_missing_stale_or_self_authority_never_reopens(self):
        with self.assertRaises(CommandError):
            recover(self.backup, self.digest, self.target, 1)
        with self.assertRaises(CommandError):
            recover(self.backup, self.digest, self.target, 2, self.backup, self.digest)
        self.assertFalse(self.target.exists())

    def test_bad_hash_and_existing_target_rejected(self):
        with self.assertRaises(CommandError):
            recover(self.backup, "0" * 64, self.target, 2)
        self.target.write_text("keep")
        with self.assertRaises(CommandError):
            recover(self.backup, self.digest, self.target, 2)
        self.assertEqual(self.target.read_text(), "keep")

    def test_symlink_and_foreign_schema_rejected(self):
        link = Path(self.temp.name) / "symlink"
        link.symlink_to(self.backup)
        with self.assertRaises(OSError):
            recover(link, self.digest, self.target, 2)
        foreign = Path(self.temp.name) / "foreign.sqlite3"
        with closing(sqlite3.connect(foreign)) as db:
            db.execute("CREATE TABLE unrelated(id INTEGER)")
            db.commit()
        with self.assertRaises(sqlite3.Error):
            recover(foreign, hashlib.sha256(foreign.read_bytes()).hexdigest(), self.target, 2)
