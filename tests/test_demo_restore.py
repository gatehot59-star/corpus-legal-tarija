"""tests/test_demo_restore.py: actual CLI and failure-injection quarantine tests."""
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sistema/api"))
sys.path.insert(0, str(ROOT / "tests"))
import demo_restore as restore
import test_demo_aislada as harness


class RestoreTests(unittest.TestCase):
    def setUp(self):
        self.h = harness.DemoTests()
        self.h.setUp()
        self.addCleanup(self.h.doCleanups)
        self.h.init()
        self.source = self.h.directory
        self.target = self.h.home / "restored"

    def command(self, *extra, flags=True):
        cmd = [sys.executable, str(ROOT / "sistema/api/demo_restore.py"),
               "--source", str(self.source), "--destination", str(self.target)]
        if flags:
            cmd += ["--isolated-demo", "--source-stopped"]
        return subprocess.run(cmd + list(extra), capture_output=True, text=True, timeout=15)

    def invoke(self):
        return restore.restore(self.source, self.target, isolated_demo=True,
                               source_stopped=True)

    def sql(self, folder, query):
        with closing(sqlite3.connect(folder / "sessions.db")) as db:
            return db.execute(query).fetchall()

    def test_stale_backup_restores_only_to_quarantine_and_preserves_source(self):
        with self.h.server() as (_, port):
            token = self.h.login(port)
            self.assertEqual(self.h.read(port, token)[0], 200)
        backup = self.h.home / "old-backup"
        shutil.copytree(self.source, backup)
        with self.h.server() as (_, port):
            self.assertEqual(self.h.request(port, "POST", "/api/v2/logout", token)[0], 200)
            self.assertEqual(self.h.read(port, token)[0], 403)
        self.h.sql("UPDATE access_grants SET revoked_at=1 WHERE id='ana'")
        self.h.sql("UPDATE access_documents SET withdrawn_at=1")
        current = {p.name: p.read_bytes() for p in self.source.iterdir()}
        self.source = backup
        original = {p.name: p.read_bytes() for p in backup.iterdir()}
        result = self.command()
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads(result.stdout)
        self.assertEqual(manifest, json.loads((self.target / restore.MANIFEST).read_text()))
        self.assertFalse(manifest["serve_authorized"])
        self.assertEqual(manifest["source_counts"]["access_sessions"], 1)
        self.assertEqual(manifest["restored_counts"]["access_sessions"], 0)
        self.assertEqual(self.sql(self.target, "SELECT * FROM login_environment"), [])
        self.assertEqual(self.sql(self.target, "SELECT enabled FROM access_collections"), [(0,)])
        for table in ("access_grants", "access_documents", "login_clock",
                      "login_budget", "login_passwords"):
            self.assertEqual(self.sql(backup, "SELECT * FROM " + table),
                             self.sql(self.target, "SELECT * FROM " + table))
        self.assertEqual(original, {p.name: p.read_bytes() for p in backup.iterdir()})
        self.assertEqual(current, {p.name: p.read_bytes() for p in self.h.directory.iterdir()})
        self.assertEqual((self.target / "candidate.db").read_bytes(), original["candidate.db"])
        for name in restore.NAMES:
            self.assertEqual(manifest["source_sha256"][name], hashlib.sha256(original[name]).hexdigest())
            self.assertEqual(manifest["restored_sha256"][name],
                             hashlib.sha256((self.target / name).read_bytes()).hexdigest())
        for name in (*restore.NAMES, restore.MANIFEST):
            self.assertEqual((self.target / name).stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o700)
        self.h.directory = self.target
        self.assertEqual(self.h.cli("serve").returncode, 2)
        # Destroy only our test fixture barrier to prove the second gate exists.
        (self.target / restore.MANIFEST).unlink()
        self.assertEqual(self.h.cli("serve").returncode, 2)

    def test_opt_ins_and_no_reopen_switch(self):
        for flags in ((), ("--isolated-demo",), ("--source-stopped",)):
            self.assertEqual(self.command(*flags, flags=False).returncode, 2)
            self.assertFalse(self.target.exists())
        self.assertEqual(self.command("--reopen").returncode, 2)
        self.assertFalse(self.target.exists())

    def test_existing_destination_never_overwritten(self):
        self.target.mkdir()
        marker = self.target / "keep"
        marker.write_text("unchanged")
        self.assertEqual(self.command().returncode, 2)
        self.assertEqual(marker.read_text(), "unchanged")
        self.assertEqual(list(self.target.iterdir()), [marker])

    def test_source_or_nested_destination_rejected(self):
        for target in (self.source, self.source / "child"):
            self.target = target
            self.assertEqual(self.command().returncode, 2)
        self.assertFalse((self.source / "child").exists())

    def test_symlink_root_and_destination_parent_rejected(self):
        alias = self.h.home / "alias"
        alias.symlink_to(self.source, target_is_directory=True)
        actual = self.source
        self.source = alias
        self.assertEqual(self.command().returncode, 2)
        self.source = actual
        self.target = alias / "child"
        self.assertEqual(self.command().returncode, 2)
        self.assertFalse((actual / "child").exists())

    def test_nonregular_and_linked_source_rejected(self):
        path = self.source / "candidate.db"
        saved = self.h.home / "saved.db"
        path.rename(saved)
        for mode in ("symlink", "hardlink", "fifo"):
            if mode == "symlink":
                path.symlink_to(saved)
            elif mode == "hardlink":
                os.link(saved, path)
            else:
                os.mkfifo(path, 0o600)
            self.assertEqual(self.command().returncode, 2)
            self.assertFalse(self.target.exists())
            path.unlink()

    def test_private_modes_and_sidecars_required(self):
        self.source.chmod(0o755)
        self.assertEqual(self.command().returncode, 2)
        self.source.chmod(0o700)
        file = self.source / "sessions.db"
        file.chmod(0o644)
        self.assertEqual(self.command().returncode, 2)
        file.chmod(0o600)
        (self.source / "sessions.db-wal").write_bytes(b"sidecar")
        self.assertEqual(self.command().returncode, 2)
        self.assertFalse(self.target.exists())

    def test_foreign_or_corrupt_source_creates_no_destination(self):
        path = self.source / "candidate.db"
        with closing(sqlite3.connect(path)) as db, db:
            db.execute("UPDATE documentos SET fuente_url='https://real.invalid/'")
        self.assertEqual(self.command().returncode, 2)
        path.write_bytes(b"not sqlite")
        self.assertEqual(self.command().returncode, 2)
        self.assertFalse(self.target.exists())

    def test_source_size_bound(self):
        with patch.object(restore, "MAX_BYTES", 1):
            with self.assertRaises(ValueError):
                self.invoke()
        self.assertFalse(self.target.exists())

    def test_source_change_detected_before_creation(self):
        original = restore._images
        calls = [0]
        def changed(root):
            values = original(root)
            calls[0] += 1
            if calls[0] == 2:
                values["sessions.db"] += b"change"
            return values
        with patch.object(restore, "_images", changed):
            with self.assertRaisesRegex(ValueError, "SOURCE_CHANGED"):
                self.invoke()
        self.assertFalse(self.target.exists())

    def test_partial_copy_keeps_first_barrier_and_source_unchanged(self):
        original = restore._write_new
        before = {p.name: p.read_bytes() for p in self.source.iterdir()}
        def interrupted(path, content):
            if path.name == "sessions.db":
                raise OSError("injected write failure")
            return original(path, content)
        with patch.object(restore, "_write_new", interrupted):
            with self.assertRaises(OSError):
                self.invoke()
        self.assertEqual(json.loads((self.target / restore.MANIFEST).read_text())["status"],
                         "incomplete")
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.source.iterdir()})
        self.h.directory = self.target
        self.assertEqual(self.h.cli("serve").returncode, 2)

    def test_sanitization_failure_leaves_complete_copy_blocked(self):
        with patch.object(restore, "_inventory", side_effect=sqlite3.OperationalError("injected")):
            with self.assertRaises(sqlite3.OperationalError):
                self.invoke()
        self.assertEqual({p.name for p in self.target.iterdir()},
                         {*restore.NAMES, restore.MANIFEST})
        self.h.directory = self.target
        self.assertEqual(self.h.cli("serve").returncode, 2)

    def test_post_copy_source_change_leaves_quarantine(self):
        original = restore._images
        calls = [0]
        def changed(root):
            values = original(root)
            calls[0] += 1
            if calls[0] == 3:
                values["sessions.db"] += b"change"
            return values
        with patch.object(restore, "_images", changed):
            with self.assertRaisesRegex(ValueError, "SOURCE_CHANGED"):
                self.invoke()
        self.assertTrue((self.target / restore.MANIFEST).exists())
        self.h.directory = self.target
        self.assertEqual(self.h.cli("serve").returncode, 2)

    def test_manifest_alone_blocks_serve_even_with_original_store(self):
        self.invoke()
        # Fault model: sanitization skipped; filesystem barrier must still deny.
        shutil.copyfile(self.source / "sessions.db", self.target / "sessions.db")
        self.h.directory = self.target
        self.assertEqual(self.h.cli("serve").returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
