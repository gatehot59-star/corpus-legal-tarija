"""sistema/api/demo_restore.py: cold synthetic restore, quarantined only.

No production, hot backup, overwrite, repair or reopen mode. The operator must
stop the source first. Owner/root is trusted; this is not a hostile-UID sandbox.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys

from demo_aislada import checked_file, checked_root, validate

NAMES = ("candidate.db", "sessions.db")
MANIFEST = "RESTORE-QUARANTINE.json"
MAX_BYTES = 8 * 1024 * 1024


def _images(root: Path) -> dict[str, bytes]:
    result = {}
    if {p.name for p in root.iterdir()} != set(NAMES):
        raise ValueError("SOURCE_EXTRA_FILES")
    for name in NAMES:
        path = checked_file(root, name)
        if not 0 < path.stat().st_size <= MAX_BYTES:
            raise ValueError("SOURCE_SIZE_LIMIT")
        with path.open("rb") as stream:
            value = stream.read(MAX_BYTES + 1)
        if not 0 < len(value) <= MAX_BYTES:
            raise ValueError("SOURCE_SIZE_LIMIT")
        result[name] = value
    return result


def _write_new(path: Path, content: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def _inventory(db: sqlite3.Connection) -> dict[str, int]:
    # Fixed identifiers, no user-supplied SQL.
    return {table: db.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
            for table in ("access_sessions", "access_grants", "access_documents",
                          "login_budget", "login_clock")}


def restore(source: str | Path, destination: str | Path, *,
            isolated_demo: bool, source_stopped: bool) -> dict:
    """Copy a stopped synthetic fixture to a new, unservable private directory.

    Requires both explicit flags. Returns an integrity/inventory manifest, not
    permission to serve. Raises OSError, ValueError or sqlite3.Error on failure.
    Partial output is retained in quarantine, never silently deleted or retried.
    The cold-source assertion is operational, not a measured process lock.
    """
    if isolated_demo is not True or source_stopped is not True or os.name != "posix":
        raise ValueError("COLD_SYNTHETIC_OPT_IN_REQUIRED")
    root = checked_root(source)
    target = Path(os.path.abspath(destination))
    parent = target.parent.resolve(strict=True)
    if parent != target.parent or target == root or root in target.parents:
        raise ValueError("DESTINATION_MUST_BE_SEPARATE")
    if target.exists() or target.is_symlink():
        raise ValueError("DESTINATION_EXISTS")
    images = _images(root)
    validate(root)
    if _images(root) != images:
        raise ValueError("SOURCE_CHANGED")
    source_hashes = {n: hashlib.sha256(v).hexdigest() for n, v in images.items()}
    target.mkdir(mode=0o700, exist_ok=False)
    checked_root(target)
    # FIRST file is an independent barrier: the existing launcher rejects any
    # third file before binding, including during partial copy or sanitization.
    _write_new(target / MANIFEST, b'{"status":"incomplete","serve_authorized":false}\n')
    for name in NAMES:
        _write_new(target / name, images[name])
        checked_file(target, name)
        if (target / name).read_bytes() != images[name]:
            raise ValueError("COPY_MISMATCH")
    if _images(root) != images:
        raise ValueError("SOURCE_CHANGED")
    store = target / "sessions.db"
    with closing(sqlite3.connect(store, timeout=2)) as db:
        with db:
            db.execute("BEGIN IMMEDIATE")
            before = _inventory(db)
            db.execute("DELETE FROM login_environment")
            db.execute("DELETE FROM access_sessions")
            db.execute("UPDATE access_collections SET enabled=0")
            if (db.execute("SELECT COUNT(*) FROM login_environment").fetchone()[0]
                    or db.execute("SELECT COUNT(*) FROM access_sessions").fetchone()[0]
                    or db.execute("SELECT COUNT(*) FROM access_collections WHERE enabled!=0").fetchone()[0]):
                raise ValueError("QUARANTINE_NOT_ESTABLISHED")
            if db.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
                raise ValueError("RESTORED_STORE_INVALID")
            after = _inventory(db)
    if (target / "candidate.db").read_bytes() != images["candidate.db"]:
        raise ValueError("CANDIDATE_CHANGED")
    result = {
        "format": "corpus-synthetic-quarantine-v1",
        "status": "quarantined",
        "synthetic": True,
        "serve_authorized": False,
        "source_stopped": "operator_asserted_not_measured",
        "source_sha256": source_hashes,
        "restored_sha256": {n: hashlib.sha256((target / n).read_bytes()).hexdigest()
                            for n in NAMES},
        "source_counts": before,
        "restored_counts": after,
        "actions": ["remove_environment_marker", "purge_sessions", "disable_collections"],
        "preserved_but_not_current": ["grants", "withdrawals", "password_verifiers",
                                     "clock_high_water", "login_budget"],
        "reopen": "NOT_IMPLEMENTED_RECONCILIATION_REQUIRED",
    }
    # Keep the barrier file present even if final serialization/write fails.
    with (target / MANIFEST).open("r+b") as stream:
        stream.seek(0)
        stream.write((json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode())
        stream.truncate()
        stream.flush()
        os.fsync(stream.fileno())
    return result


def main(argv: list[str] | None = None) -> int:
    """CLI: opt-in cold source, new target, redacted errors, no listener."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--isolated-demo", action="store_true")
    parser.add_argument("--source-stopped", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = restore(args.source, args.destination, isolated_demo=args.isolated_demo,
                         source_stopped=args.source_stopped)
        print(json.dumps(result, ensure_ascii=False), flush=True)
        return 0
    except (OSError, ValueError, sqlite3.Error) as exc:
        print("DEMO_RESTORE_FAILED: " + type(exc).__name__, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
