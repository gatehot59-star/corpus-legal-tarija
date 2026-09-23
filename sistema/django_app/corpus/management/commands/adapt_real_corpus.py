"""Build a Django-compatible exact-version snapshot from the copied corpus."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from sistema.api.version_text import SUPPORTED_SOURCE_IDS


class Command(BaseCommand):
    """Adapt documentos plus ordered chunks without modifying the source DB."""

    help = "Create an exact-version staging snapshot from a copied real Corpus DB"

    def add_arguments(self, parser) -> None:
        parser.add_argument("source", type=Path)
        parser.add_argument("target", type=Path)

    def handle(self, *args, **options) -> None:
        source: Path = options["source"]
        target: Path = options["target"]
        self._validate_paths(source, target)
        documents = 0
        total_characters = 0
        with sqlite3.connect(source) as source_db:
            source_db.execute("PRAGMA query_only=ON")
            with sqlite3.connect(target) as target_db:
                source_db.backup(target_db)
                target_db.execute(
                    "CREATE TABLE corpus_cleanup_versions ("
                    "uid TEXT NOT NULL, version_sha256 TEXT NOT NULL, "
                    "extraction_json TEXT NOT NULL, "
                    "PRIMARY KEY(uid, version_sha256))")
                target_db.execute(
                    "CREATE INDEX corpus_cleanup_versions_uid_idx "
                    "ON corpus_cleanup_versions(uid)")
                document_rows = source_db.execute(
                    "SELECT doc_id,uid,fuente_id,fuente_url,sha256 "
                    "FROM documentos ORDER BY doc_id")
                for doc_id, uid, source_id, source_url, source_sha256 in document_rows:
                    self._validate_document(uid, source_id, source_url, source_sha256)
                    pieces = [row[0] or "" for row in source_db.execute(
                        "SELECT cuerpo FROM chunks WHERE doc_id=? ORDER BY nro", (doc_id,))]
                    text = "".join(pieces)
                    version_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
                    extraction = {
                        "text": text,
                        "text_sha256": version_sha256,
                        "source_sha256": source_sha256,
                        "source_url": source_url,
                        "authority": "secondary",
                        "extraction_method": "real-corpus-adapter",
                    }
                    target_db.execute(
                        "INSERT INTO corpus_cleanup_versions "
                        "(uid,version_sha256,extraction_json) VALUES(?,?,?)",
                        (uid, version_sha256, json.dumps(extraction, ensure_ascii=False,
                                                         separators=(",", ":"))))
                    documents += 1
                    total_characters += len(text)
                target_db.commit()
                integrity = target_db.execute("PRAGMA integrity_check").fetchone()[0]
                if integrity != "ok":
                    raise CommandError(f"adapted snapshot integrity failed: {integrity}")
        os.chmod(target, 0o400)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        self.stdout.write(json.dumps({
            "source": str(source),
            "target": str(target),
            "documents": documents,
            "total_characters": total_characters,
            "bytes": target.stat().st_size,
            "sha256": digest,
            "integrity": "ok",
        }, sort_keys=True))

    @staticmethod
    def _validate_paths(source: Path, target: Path) -> None:
        """Reject missing, symlinked, equal, or pre-existing paths."""
        if not source.is_file() or source.is_symlink():
            raise CommandError("source must be a regular file, not a symlink")
        if target.exists() or target.is_symlink():
            raise CommandError("target must not already exist")
        if source.resolve() == target.resolve():
            raise CommandError("source and target must differ")
        target.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _validate_document(uid: str, source_id: str, source_url: str,
                           source_sha256: str) -> None:
        """Fail closed on identity, provenance, and source-integrity fields."""
        if not isinstance(uid, str) or not 1 <= len(uid) <= 200:
            raise CommandError("invalid document uid")
        if source_id not in SUPPORTED_SOURCE_IDS:
            raise CommandError(f"unsupported source family: {source_id}")
        if not isinstance(source_url, str) or not source_url.startswith("https://"):
            raise CommandError(f"invalid source URL for {uid}")
        if not isinstance(source_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", source_sha256):
            raise CommandError(f"invalid source SHA-256 for {uid}")
