"""sistema/api/access_policy.py: persistent, read-only access decisions for PR9.

No account, session, grant or approval issuance; no listener or production DB.
The trusted host provisions this separate store and binds one collection.
Bearer sessions must be generated with >=256 bits of entropy by the issuer;
only their SHA256 digests belong in this schema, never plaintext credentials.
"""
from __future__ import annotations

from contextlib import closing
import hashlib
import math
from pathlib import Path
import re
import sqlite3
import time
from typing import Callable

from exact_http import ExactReaderApp

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE access_users (
 id TEXT PRIMARY KEY, enabled INTEGER NOT NULL CHECK(enabled IN (0,1))
) STRICT;
CREATE TABLE access_sessions (
 token_sha256 TEXT PRIMARY KEY CHECK(length(token_sha256)=64 AND token_sha256 NOT GLOB '*[^0-9a-f]*'),
 user_id TEXT NOT NULL REFERENCES access_users(id),
 valid_from INTEGER NOT NULL, valid_until INTEGER NOT NULL,
 revoked_at INTEGER, CHECK(valid_until>valid_from)
) STRICT;
CREATE TABLE access_collections (
 id TEXT PRIMARY KEY, enabled INTEGER NOT NULL CHECK(enabled IN (0,1)),
 approval_evidence TEXT NOT NULL CHECK(length(trim(approval_evidence))>0)
) STRICT;
CREATE TABLE access_memberships (
 user_id TEXT NOT NULL REFERENCES access_users(id), group_id TEXT NOT NULL,
 enabled INTEGER NOT NULL CHECK(enabled IN (0,1)), PRIMARY KEY(user_id,group_id)
) STRICT;
CREATE TABLE access_grants (
 id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES access_users(id),
 group_id TEXT NOT NULL, collection_id TEXT NOT NULL REFERENCES access_collections(id),
 origin TEXT NOT NULL CHECK(origin IN ('pilot','paid')),
 valid_from INTEGER NOT NULL, valid_until INTEGER NOT NULL, revoked_at INTEGER,
 issued_by TEXT NOT NULL CHECK(length(trim(issued_by))>0),
 evidence_id TEXT NOT NULL CHECK(length(trim(evidence_id))>0),
 CHECK(valid_until>valid_from)
) STRICT;
CREATE TABLE access_documents (
 collection_id TEXT NOT NULL REFERENCES access_collections(id),
 uid TEXT NOT NULL, version TEXT NOT NULL CHECK(length(version)=64 AND version NOT GLOB '*[^0-9a-f]*'),
 withdrawn_at INTEGER, PRIMARY KEY(collection_id,uid,version)
) STRICT;
CREATE INDEX access_grants_lookup ON access_grants(user_id,collection_id);
"""

DECISION_SQL = """
SELECT 1
FROM access_sessions s
JOIN access_users u ON u.id=s.user_id
JOIN access_grants g ON g.user_id=u.id
JOIN access_memberships m ON m.user_id=u.id AND m.group_id=g.group_id
JOIN access_collections c ON c.id=g.collection_id
JOIN access_documents d ON d.collection_id=c.id
WHERE s.token_sha256=? AND c.id=? AND d.uid=? AND d.version=?
 AND u.enabled=1 AND m.enabled=1 AND c.enabled=1
 AND s.revoked_at IS NULL AND g.revoked_at IS NULL AND d.withdrawn_at IS NULL
 AND s.valid_from<=? AND ?<s.valid_until
 AND g.valid_from<=? AND ?<g.valid_until
LIMIT 1
"""


class SQLiteAccessPolicy:
    """Resolve a bearer session and scoped grant on every HTTP page.

    Collection comes from server configuration, never from client headers.
    The single SELECT observes one SQLite snapshot of all access conditions.
    Missing identity returns False; store/clock errors raise so PR9 returns503.
    Approval references are administrative records, not proof of legal review.
    """

    def __init__(self, store: str | Path, collection: str,
                 clock: Callable[[], float] = time.time):
        path = Path(store).resolve(strict=True)
        if not path.is_file():
            raise ValueError("POLICY_STORE_NOT_REGULAR")
        if not isinstance(collection, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", collection):
            raise ValueError("INVALID_COLLECTION")
        if not callable(clock):
            raise TypeError("INVALID_CLOCK")
        self.uri = path.as_uri() + "?mode=ro"
        self.collection = collection
        self.clock = clock

    def __call__(self, environ: dict, uid: str, version: str) -> bool:
        """Return literal True only for a currently eligible persisted grant."""
        authorization = environ.get("HTTP_AUTHORIZATION", "")
        if not isinstance(authorization, str):
            return False
        match = re.fullmatch(r"Bearer ([A-Za-z0-9_-]{43,128})", authorization)
        if match is None:
            return False
        if not isinstance(uid, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", uid):
            return False
        if not isinstance(version, str) or not re.fullmatch(r"[0-9a-f]{64}", version):
            return False
        now = self.clock()
        if isinstance(now, bool) or not isinstance(now, (int, float)) or not math.isfinite(now) or now < 0:
            raise ValueError("INVALID_CLOCK")
        digest = hashlib.sha256(match[1].encode("ascii")).hexdigest()
        with closing(sqlite3.connect(self.uri, uri=True, timeout=1)) as db:
            db.execute("PRAGMA query_only=ON")
            row = db.execute(DECISION_SQL, (digest, self.collection, uid, version,
                                            now, now, now, now)).fetchone()
        return row is not None



def make_app(candidate: str | Path, policy_store: str | Path,
             collection: str, clock: Callable[[], float] = time.time) -> ExactReaderApp:
    """Wire persisted access into PR9, without starting HTTP or writing files."""
    if Path(candidate).resolve(strict=True) == Path(policy_store).resolve(strict=True):
        raise ValueError("SEPARATE_POLICY_STORE_REQUIRED")
    return ExactReaderApp(candidate, SQLiteAccessPolicy(policy_store, collection, clock))
