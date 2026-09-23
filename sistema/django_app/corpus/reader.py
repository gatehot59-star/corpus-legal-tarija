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

MAX_SNAPSHOT = 512 * 1024 * 1024
_HASH_CHUNK = 1024 * 1024
_VERIFIED: dict[str, tuple[int, int, int, int, str]] = {}


def _verified_digest(path: Path, fd: int, metadata: os.stat_result, expected: str) -> None:
    """Verify a stable open file once per process and reject changed files."""
    key = str(path)
    identity = (metadata.st_dev, metadata.st_ino, metadata.st_size, metadata.st_mtime_ns)
    cached = _VERIFIED.get(key)
    if cached is not None and cached[:4] == identity and cached[4] == expected:
        return
    digest = hashlib.sha256()
    os.lseek(fd, 0, os.SEEK_SET)
    while True:
        block = os.read(fd, _HASH_CHUNK)
        if not block:
            break
        digest.update(block)
    actual = digest.hexdigest()
    if actual != expected:
        raise CorpusError(ErrorCode.INTEGRITY_FAILED)
    _VERIFIED[key] = (*identity, actual)


def read_exact(row: Locator, start: int, limit: int) -> dict:
    """Verify and read an exact version from an immutable read-only SQLite file."""
    path = Path(row.collection.snapshot_path)
    if not path.is_absolute():
        raise CorpusError(ErrorCode.INTEGRITY_FAILED)
    fd = -1
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_SNAPSHOT:
            raise CorpusError(ErrorCode.INTEGRITY_FAILED)
        _verified_digest(path, fd, before, row.collection.snapshot_digest)
        with closing(sqlite3.connect(f"/proc/self/fd/{fd}")) as db:
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
    finally:
        if fd >= 0:
            os.close(fd)
