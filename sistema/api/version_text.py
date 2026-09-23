"""Read exact cleanup versions. No heuristic chunk overlap or implicit fallback.

Internal adapter only, not an authenticated HTTP service. Caller must enforce
access/withdrawal policy before calling. The adapter accepts only the three
measured public source families imported by the real-corpus staging command,
while retaining the existing synthetic fixture contract.
"""
from __future__ import annotations
import hashlib
import json
import re
import sqlite3

SUPPORTED_SOURCE_IDS = frozenset({"lexivox_nacional", "tsj_genesis", "tarija_gaceta"})


class VersionReadError(ValueError):
    """Machine-readable failure without document contents."""
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def read_version(db: sqlite3.Connection, uid: str, version: str | None = None,
                 start: int = 0, limit: int = 2600) -> dict:
    """Return a bounded exact slice and versioned next locator."""
    if not isinstance(uid, str) or not 1 <= len(uid) <= 200:
        raise VersionReadError("INVALID_UID")
    if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 10000:
        raise VersionReadError("INVALID_RANGE")
    if version is None and start:
        raise VersionReadError("VERSION_REQUIRED_FOR_OFFSET")
    if version is not None and (not isinstance(version, str) or not re.fullmatch("[0-9a-f]{64}", version)):
        raise VersionReadError("INVALID_VERSION")
    row = db.execute("SELECT sha256,fuente_id,fuente_url FROM documentos WHERE uid=?", (uid,)).fetchone()
    if row is None:
        raise VersionReadError("NOT_FOUND")
    selected = version or row[0]
    try:
        record = db.execute(
            "SELECT extraction_json FROM corpus_cleanup_versions WHERE uid=? AND version_sha256=?",
            (uid, selected)).fetchone()
    except sqlite3.OperationalError as exc:
        raise VersionReadError("EXACT_VERSION_UNAVAILABLE") from exc
    if record is None:
        raise VersionReadError("EXACT_VERSION_UNAVAILABLE")
    try:
        extraction = json.loads(record[0])
        text = extraction["text"]
        source_sha256 = extraction["source_sha256"]
        source_url = extraction.get("source_url", row[2])
        if (not isinstance(text, str)
                or hashlib.sha256(text.encode("utf-8")).hexdigest() != selected
                or extraction["text_sha256"] != selected
                or source_sha256 is None
                or not isinstance(source_sha256, str)
                or not re.fullmatch("[0-9a-f]{64}", source_sha256)
                or not isinstance(source_url, str)
                or source_url != row[2]
                or row[1] not in SUPPORTED_SOURCE_IDS
                or extraction["authority"] != "secondary"):
            raise VersionReadError("VERSION_INTEGRITY_FAILED")
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise VersionReadError("VERSION_INTEGRITY_FAILED") from exc
    if start > len(text):
        raise VersionReadError("OFFSET_OUT_OF_RANGE")
    end = min(len(text), start + limit)
    return {"uid": uid, "version": selected, "is_current": True,
            "text": text[start:end], "start": start, "end": end,
            "total_characters": len(text), "text_sha256": selected,
            "next": None if end == len(text) else {"uid": uid, "version": selected, "start": end},
            "authority": "secondary", "oficial": False,
            "extraction_method": extraction.get("extraction_method", "real-corpus-adapter"),
            "legal_validity": "NOT_MEASURED", "source_url": source_url,
            "source_sha256": source_sha256, "hash_scope": "text_utf8"}
