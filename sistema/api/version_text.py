"""Read exact cleanup versions. No heuristic chunk overlap or implicit fallback.

Internal adapter only, not an authenticated HTTP service. Caller must enforce
access/withdrawal policy before calling. Only versioned national cleanup records
are supported; unversioned legacy material is rejected instead of guessed.
"""
from __future__ import annotations
import hashlib
import json
import re
import sqlite3


class VersionReadError(ValueError):
    """Machine-readable failure without document contents."""
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def read_version(db: sqlite3.Connection, uid: str, version: str | None = None,
                 start: int = 0, limit: int = 2600) -> dict:
    """Return a bounded exact slice and versioned next locator.

    A nonzero offset requires an explicit version. No fallback to current text
    for an unknown version. The exact text archived by the extractor is the
    source, checked against its version digest, never guessed from chunks.
    """
    if not isinstance(uid, str) or not 1 <= len(uid) <= 200:
        raise VersionReadError('INVALID_UID')
    if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 10000:
        raise VersionReadError('INVALID_RANGE')
    if version is None and start:
        raise VersionReadError('VERSION_REQUIRED_FOR_OFFSET')
    if version is not None and (not isinstance(version, str) or not re.fullmatch('[0-9a-f]{64}', version)):
        raise VersionReadError('INVALID_VERSION')
    row = db.execute('SELECT sha256,fuente_id,fuente_url FROM documentos WHERE uid=?', (uid,)).fetchone()
    if row is None:
        raise VersionReadError('NOT_FOUND')
    selected = version or row[0]
    try:
        record = db.execute('SELECT extraction_json FROM corpus_cleanup_versions WHERE uid=? AND version_sha256=?', (uid, selected)).fetchone()
    except sqlite3.OperationalError as exc:
        raise VersionReadError('EXACT_VERSION_UNAVAILABLE') from exc
    if record is None:
        raise VersionReadError('EXACT_VERSION_UNAVAILABLE')
    try:
        extraction = json.loads(record[0])
        text = extraction['text']
        if not isinstance(text, str) or hashlib.sha256(text.encode('utf-8')).hexdigest() != selected or extraction['text_sha256'] != selected:
            raise VersionReadError('VERSION_INTEGRITY_FAILED')
        if extraction['authority'] != 'secondary' or row[1] != 'lexivox_nacional':
            raise VersionReadError('UNSUPPORTED_PROVENANCE')
    except (KeyError,TypeError,json.JSONDecodeError) as exc:
        raise VersionReadError('VERSION_INTEGRITY_FAILED') from exc
    if start > len(text):
        raise VersionReadError('OFFSET_OUT_OF_RANGE')
    end = min(len(text), start + limit)
    return {'uid': uid, 'version': selected, 'is_current': selected == row[0],
            'text': text[start:end], 'start': start, 'end': end,
            'total_characters': len(text), 'text_sha256': selected,
            'next': None if end == len(text) else {'uid': uid,'version':selected,'start':end},
            'authority': 'secondary', 'oficial': False, 'extraction_method': 'html',
            'legal_validity': 'NOT_MEASURED', 'source_url': row[2],
            'source_sha256': extraction['source_sha256'], 'hash_scope': 'text_utf8'}
