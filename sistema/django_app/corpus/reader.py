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
    if digest.hexdigest() != expected:
        raise CorpusError(ErrorCode.INTEGRITY_FAILED)
    _VERIFIED[key] = (*identity, expected)


def _open_verified(row: Locator):
    """Open the approved regular snapshot and verify its digest."""
    path = Path(row.collection.snapshot_path)
    if not path.is_absolute():
        raise CorpusError(ErrorCode.INTEGRITY_FAILED)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    metadata = os.fstat(fd)
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_SNAPSHOT:
        os.close(fd)
        raise CorpusError(ErrorCode.INTEGRITY_FAILED)
    _verified_digest(path, fd, metadata, row.collection.snapshot_digest)
    return fd


def read_exact(row: Locator, start: int, limit: int) -> dict:
    """Verify and read an exact version from an immutable read-only SQLite file."""
    fd = -1
    try:
        fd = _open_verified(row)
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


def search_snapshot(row: Locator, query: str, allowed_uids: set[str]) -> dict[str, str] | None:
    """Search the adapted FTS index, or signal that the fixture has no FTS table."""
    fd = -1
    try:
        fd = _open_verified(row)
        with closing(sqlite3.connect(f"/proc/self/fd/{fd}")) as db:
            db.execute("PRAGMA query_only=ON")
            db.execute("PRAGMA trusted_schema=OFF")
            if db.execute("SELECT 1 FROM sqlite_master WHERE name='chunks'").fetchone() is None:
                return None
            phrase = '"' + query.replace('"', '""') + '"'
            found: dict[str, str] = {}
            for uid, snippet in db.execute(
                    "SELECT uid, snippet(chunks, 0, '<mark>', '</mark>', '...', 12) "
                    "FROM chunks WHERE chunks MATCH ? LIMIT 20000", (phrase,)):
                if uid in allowed_uids and uid not in found:
                    found[uid] = snippet or ""
            pattern = "%" + query.casefold() + "%"
            for uid, title in db.execute(
                    "SELECT uid, titulo FROM documentos "
                    "WHERE lower(titulo) LIKE ? LIMIT 20000", (pattern,)):
                if uid in allowed_uids and uid not in found:
                    found[uid] = title or ""
            return found
    except (OSError, sqlite3.Error, ValueError, TypeError) as exc:
        raise CorpusError(ErrorCode.INTEGRITY_FAILED) from exc
    finally:
        if fd >= 0:
            os.close(fd)


def browse_snapshot(row: Locator, allowed_uids: set[str], source: str = "",
                    rubro: str = "", tipo: str = "", offset: int = 0,
                    limit: int = 20) -> dict:
    """Return authorized document metadata and facets for source/rubro navigation."""
    if type(offset) is not int or offset < 0 or type(limit) is not int or not 1 <= limit <= 50:
        raise CorpusError(ErrorCode.INVALID_INPUT)
    fd = -1
    try:
        fd = _open_verified(row)
        with closing(sqlite3.connect(f"/proc/self/fd/{fd}")) as db:
            db.execute("PRAGMA query_only=ON")
            db.execute("PRAGMA trusted_schema=OFF")
            tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "fuentes" not in tables:
                return {"items": (), "sources": (), "rubros": (), "tipos": (), "next_offset": None}
            rows = db.execute(
                "SELECT d.uid, d.titulo, d.fuente_id, f.nombre, d.jurisdiccion, "
                "d.departamento, d.organo, d.tipo_norma, d.materia, d.fuente_url "
                "FROM documentos d JOIN fuentes f ON f.fuente_id=d.fuente_id "
                "ORDER BY d.fuente_id, COALESCE(d.materia,''), COALESCE(d.tipo_norma,''), d.titulo, d.uid"
            ).fetchall()
            allowed = set(allowed_uids)
            source_key, rubro_key, tipo_key = source.casefold(), rubro.casefold(), tipo.casefold()
            sources, rubros, tipos = {}, set(), set()
            matches = []
            for values in rows:
                uid, title, source_id, source_name, jurisdiction, department, organ, norm_type, matter, url = values
                if uid not in allowed:
                    continue
                source_label = source_name or source_id
                if source_id:
                    sources[source_id] = source_label
                if matter:
                    rubros.add(matter)
                if norm_type:
                    tipos.add(norm_type)
                if source_key and source_id.casefold() != source_key:
                    continue
                if rubro_key and (not matter or matter.casefold() != rubro_key):
                    continue
                if tipo_key and (not norm_type or norm_type.casefold() != tipo_key):
                    continue
                matches.append({"uid": uid, "collection_id": str(row.collection_id),
                                "version_sha256": row.version_sha256, "title": title or uid,
                                "source_id": source_id, "source_name": source_label,
                                "jurisdiction": jurisdiction or "", "department": department or "",
                                "organ": organ or "", "type": norm_type or "", "matter": matter or "",
                                "source_url": url or ""})
            page = matches[offset:offset + limit]
            next_offset = offset + limit if offset + limit < len(matches) else None
            return {"items": tuple(page), "sources": tuple(sorted(sources.items(), key=lambda x: x[1].casefold())),
                    "rubros": tuple(sorted(rubros, key=str.casefold)),
                    "tipos": tuple(sorted(tipos, key=str.casefold)), "next_offset": next_offset}
    except (OSError, sqlite3.Error, ValueError, TypeError) as exc:
        raise CorpusError(ErrorCode.INTEGRITY_FAILED) from exc
    finally:
        if fd >= 0:
            os.close(fd)
