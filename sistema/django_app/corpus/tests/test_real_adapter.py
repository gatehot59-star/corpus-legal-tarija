"""Acceptance tests for the copied-real-corpus adapter."""
import hashlib
import json
import os
import sqlite3
import tempfile
from pathlib import Path
from unittest import TestCase

from django.core.management.base import CommandError

from corpus.management.commands.adapt_real_corpus import Command


class RealAdapterTests(TestCase):
    """Verify the adapter preserves source identity and refuses unsafe inputs."""

    def make_source(self, root: Path, source_id: str = "tarija_gaceta") -> Path:
        """Create a minimal measured-shape source database for the adapter."""
        path = root / "source.sqlite3"
        text = "Texto real de prueba."
        source_sha = hashlib.sha256(b"source").hexdigest()
        with sqlite3.connect(path) as db:
            db.executescript(
                "CREATE TABLE fuentes(fuente_id TEXT PRIMARY KEY,nombre TEXT NOT NULL,"
                "jurisdiccion TEXT NOT NULL);"
                "CREATE TABLE documentos(doc_id INTEGER PRIMARY KEY,uid TEXT UNIQUE NOT NULL,"
                "fuente_id TEXT NOT NULL,jurisdiccion TEXT NOT NULL,fuente_url TEXT NOT NULL,"
                "sha256 TEXT NOT NULL,titulo TEXT);"
                "CREATE TABLE chunks(cuerpo TEXT,uid TEXT,doc_id INTEGER,nro INTEGER);"
            )
            db.execute("INSERT INTO fuentes VALUES(?,?,?)", (source_id, "Fuente", "departamental"))
            db.execute("INSERT INTO documentos VALUES(?,?,?,?,?,?,?)", (
                1, "real-1", source_id, "departamental", "https://example.invalid/doc", source_sha, "Título"))
            db.execute("INSERT INTO chunks VALUES(?,?,?,?)", (text, "real-1", 1, 1))
            db.commit()
        return path

    def test_adapts_ordered_chunks_and_records_exact_version(self):
        """Copying the source creates one verified exact-version record."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_source(root)
            target = root / "adapted.sqlite3"
            Command().handle(source=source, target=target)
            with sqlite3.connect(target) as db:
                row = db.execute("SELECT uid,version_sha256,extraction_json "
                                 "FROM corpus_cleanup_versions").fetchone()
            self.assertEqual(row[0], "real-1")
            payload = json.loads(row[2])
            self.assertEqual(payload["text_sha256"], row[1])
            self.assertEqual(payload["source_url"], "https://example.invalid/doc")
            self.assertEqual(target.stat().st_mode & 0o777, 0o400)

    def test_rejects_unsupported_source_family_without_target(self):
        """Unknown provenance is rejected before a target is written."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_source(root, "unknown")
            target = root / "adapted.sqlite3"
            with self.assertRaises(CommandError):
                Command().handle(source=source, target=target)
            self.assertFalse(target.exists())

    def test_rejects_symlink_source(self):
        """The adapter refuses a symlink even when its target is regular."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_source(root)
            link = root / "source-link.sqlite3"
            link.symlink_to(source)
            with self.assertRaises(CommandError):
                Command._validate_paths(link, root / "out.sqlite3")

    def test_rejects_existing_target(self):
        """The adapter never overwrites an existing destination."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_source(root)
            target = root / "out.sqlite3"
            target.touch()
            with self.assertRaises(CommandError):
                Command._validate_paths(source, target)
