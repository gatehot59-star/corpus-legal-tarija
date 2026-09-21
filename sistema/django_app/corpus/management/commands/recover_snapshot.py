"""sistema/django_app/corpus/management/commands/recover_snapshot.py: offline recovery.

Restore never reopens the backup policy. Reconciliation starts from independently
current authority and imports only references/reports with identical identity and
locator mappings. Source databases are never written and no listener is started.
"""
import hashlib
import os
import sqlite3
import stat
from contextlib import closing
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError

MAX_BACKUP = 64 * 1024 * 1024


def verified_bytes(path: Path, expected: str) -> bytes:
    """Read a regular, single-linked, bounded source without following symlinks."""
    if not path.is_absolute() or len(expected) != 64:
        raise CommandError("Absolute path and full digest required")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as handle:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > MAX_BACKUP:
            raise CommandError("Source is not an eligible backup")
        data = handle.read(MAX_BACKUP + 1)
    if hashlib.sha256(data).hexdigest() != expected:
        raise CommandError("Digest mismatch")
    return data


def database(data: bytes) -> sqlite3.Connection:
    """Load verified bytes in isolation; validate schema/integrity before use."""
    db = sqlite3.connect(":memory:")
    try:
        db.deserialize(data)
        db.execute("PRAGMA trusted_schema=OFF")
        if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise CommandError("Database integrity failed")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise CommandError("Foreign key integrity failed")
        if db.execute("SELECT COUNT(*) FROM corpus_policystate WHERE id=1").fetchone()[0] != 1:
            raise CommandError("Missing policy authority")
        if not db.execute("SELECT 1 FROM django_migrations WHERE app='corpus' AND name='0001_initial'").fetchone():
            raise CommandError("Unsupported schema")
        return db
    except Exception:
        db.close()
        raise


def write_new(db: sqlite3.Connection, target: Path) -> None:
    """Create a new owner-only destination; never overwrite or follow a target."""
    if not target.is_absolute() or target.exists():
        raise CommandError("New absolute target required")
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write(db.serialize())
        output.flush()
        os.fsync(output.fileno())


def recover(backup: Path, digest: str, target: Path, revision: int,
            authority: Path | None = None, authority_digest: str | None = None) -> dict:
    """Quarantine backup or reconcile against independently pinned current policy.

    Reopening requires a second, distinct, newer authority snapshot supplied by
    an authorized offline operator. The caller is responsible for establishing
    that it is current; hashes alone do not establish that provenance.
    """
    with closing(database(verified_bytes(backup, digest))) as old:
        old_revision, old_epoch = old.execute(
            "SELECT revision,session_epoch FROM corpus_policystate WHERE id=1").fetchone()
        if type(revision) is not int or revision <= old_revision:
            raise CommandError("Independent current policy revision must be newer than backup")
        if authority is None:
            old.execute("DELETE FROM django_session")
            old.execute("UPDATE corpus_accessgrant SET revoked_at=CURRENT_TIMESTAMP")
            old.execute("UPDATE corpus_membership SET enabled=0")
            old.execute("UPDATE corpus_collection SET enabled=0")
            old.execute("UPDATE corpus_policystate SET quarantined=1,revision=?,session_epoch=? WHERE id=1",
                        (revision, old_epoch + 1))
            old.commit()
            write_new(old, target)
            return {"quarantined": True, "serve_authorized": False, "imported": 0}
        if authority.resolve() == backup.resolve() or authority_digest == digest:
            raise CommandError("Backup cannot be its own current policy authority")
        with closing(database(verified_bytes(authority, authority_digest or ""))) as current:
            rev, epoch, quarantined = current.execute(
                "SELECT revision,session_epoch,quarantined FROM corpus_policystate WHERE id=1").fetchone()
            if rev != revision or epoch < old_epoch or quarantined:
                raise CommandError("Current policy receipt does not match")
            imported = 0
            # Current authority owns users, passwords, grants, withdrawals and catalog.
            # Never import those tables from the older backup.
            for table in ("corpus_savedreference", "corpus_privatefeedback"):
                columns = [r[1] for r in old.execute(f"PRAGMA table_info({table})")]
                if columns != [r[1] for r in current.execute(f"PRAGMA table_info({table})")]:
                    raise CommandError("Schema mismatch")
                for row in old.execute(f"SELECT * FROM {table}"):
                    item = dict(zip(columns, row))
                    owner = item["owner_id"]
                    loc = item["locator_id"]
                    identity_sql = "SELECT id,username,date_joined FROM auth_user WHERE id=?"
                    locator_sql = "SELECT id,collection_id,uid,version_sha256 FROM corpus_locator WHERE id=?"
                    old_user = old.execute(identity_sql, (owner,)).fetchone()
                    new_user = current.execute(identity_sql, (owner,)).fetchone()
                    old_loc = old.execute(locator_sql, (loc,)).fetchone()
                    new_loc = current.execute(locator_sql, (loc,)).fetchone()
                    if not old_user or old_user != new_user or not old_loc or old_loc != new_loc:
                        continue
                    marks = ",".join("?" for _ in columns)
                    result = current.execute(f"INSERT OR IGNORE INTO {table} ({','.join(columns)}) VALUES ({marks})", row)
                    imported += result.rowcount
            current.execute("DELETE FROM django_session")
            current.execute("UPDATE corpus_policystate SET session_epoch=? WHERE id=1",
                            (max(epoch, old_epoch) + 1,))
            if current.execute("PRAGMA foreign_key_check").fetchall():
                raise CommandError("Reconciled foreign key integrity failed")
            current.commit()
            write_new(current, target)
            return {"quarantined": False, "serve_authorized": True, "imported": imported,
                    "policy_revision": rev, "session_epoch": max(epoch, old_epoch) + 1}


class Command(BaseCommand):
    """Recover offline; reconciliation is a separate explicit operator decision."""
    help = "Restore to a new target without starting a server"

    def add_arguments(self, parser) -> None:
        """Require backup custody and independently current policy revision."""
        parser.add_argument("--backup", required=True)
        parser.add_argument("--sha256", required=True)
        parser.add_argument("--target", required=True)
        parser.add_argument("--current-policy-revision", type=int, required=True)
        parser.add_argument("--reconcile-from")
        parser.add_argument("--authority-sha256")

    def handle(self, *args, **options) -> None:
        """Execute only the explicit offline command; sanitize operational errors."""
        try:
            result = recover(Path(options["backup"]), options["sha256"], Path(options["target"]),
                options["current_policy_revision"],
                Path(options["reconcile_from"]) if options["reconcile_from"] else None,
                options["authority_sha256"])
        except (OSError, sqlite3.Error, ValueError) as exc:
            raise CommandError("Recovery failed; source left unchanged") from exc
        self.stdout.write(str(result))
