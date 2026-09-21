"""sistema/django_app/corpus/reader.py: bounded immutable SQLite adapter."""
import hashlib
import os
import sqlite3
import stat
from contextlib import closing
from pathlib import Path
from contracts.corpus_django import ErrorCode
from sistema.api.version_text import read_version, VersionReadError
from .access import CorpusError
from .models import Locator

MAX_SNAPSHOT = 64 * 1024 * 1024


def read_exact(row: Locator, start: int, limit: int) -> dict:
    """Verify snapshot and exact text; refuse symlinks, mutation and oversize."""
    path = Path(row.collection.snapshot_path)
    if not path.is_absolute():
        raise CorpusError(ErrorCode.INTEGRITY_FAILED)
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as source:
            before = os.fstat(source.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_SNAPSHOT:
                raise CorpusError(ErrorCode.INTEGRITY_FAILED)
            data = source.read(MAX_SNAPSHOT + 1)
            if hashlib.sha256(data).hexdigest() != row.collection.snapshot_digest:
                raise CorpusError(ErrorCode.INTEGRITY_FAILED)
        # Deserialize verified bytes: path replacement after hash cannot change input.
        with closing(sqlite3.connect(":memory:")) as db:
            db.deserialize(data)
            db.execute("PRAGMA query_only=ON")
            db.execute("PRAGMA trusted_schema=OFF")
            db.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 4 * 1024 * 1024)
            result = read_version(db, row.uid, row.version_sha256, start, limit)
            if (len(result["source_sha256"]) != 64 or
                    not result["source_url"].startswith("https://")):
                raise CorpusError(ErrorCode.INTEGRITY_FAILED)
            return result
    except (OSError, sqlite3.Error, VersionReadError, ValueError, TypeError) as exc:
        raise CorpusError(ErrorCode.INTEGRITY_FAILED) from exc
