"""sistema/django_app/corpus/management/commands/provision_fixture.py: synthetic only."""
import hashlib
import json
import sqlite3
from pathlib import Path
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from corpus.models import PolicyState, Collection, Membership, Locator, AccessGrant

FIXTURE_PASSWORD = "Synthetic-Corpus-Only-2026!"
FIXTURE_TEXT = "Artículo 1. Documento sintético de prueba. No es legislación.\n" * 4


def provision(snapshot: Path) -> dict:
    """Create two fictional accounts and one immutable fictional source; refuse reuse."""
    if not settings.TESTING or not snapshot.is_absolute() or snapshot.exists():
        raise CommandError("Only synthetic profile and a new absolute snapshot path are permitted")
    if get_user_model().objects.exists() or PolicyState.objects.exists():
        raise CommandError("Fixture requires an empty operational database")
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(FIXTURE_TEXT.encode()).hexdigest()
    with snapshot.open("xb"):
        pass
    db = sqlite3.connect(snapshot)
    try:
        db.executescript("CREATE TABLE documentos(uid TEXT PRIMARY KEY,sha256 TEXT,fuente_id TEXT,fuente_url TEXT);"
                         "CREATE TABLE corpus_cleanup_versions(uid TEXT,version_sha256 TEXT,extraction_json TEXT);")
        db.execute("INSERT INTO documentos VALUES(?,?,?,?)",
                   ("fixture-1", digest, "lexivox_nacional", "https://example.invalid/synthetic"))
        db.execute("INSERT INTO corpus_cleanup_versions VALUES(?,?,?)", ("fixture-1", digest, json.dumps({
            "text": FIXTURE_TEXT, "text_sha256": digest, "authority": "secondary",
            "source_sha256": hashlib.sha256(b"synthetic-source").hexdigest()})))
        db.commit()
    finally:
        db.close()
    with transaction.atomic():
        User = get_user_model()
        ana = User.objects.create_user("fixture-ana", "ana@example.invalid", FIXTURE_PASSWORD)
        User.objects.create_user("fixture-ben", "ben@example.invalid", FIXTURE_PASSWORD)
        group = Group.objects.create(name="synthetic-readers")
        Membership.objects.create(user=ana, group=group)
        collection = Collection.objects.create(name="Colección sintética", enabled=True,
            approval_evidence="synthetic-only", snapshot_path=str(snapshot),
            snapshot_digest=hashlib.sha256(snapshot.read_bytes()).hexdigest())
        row = Locator.objects.create(collection=collection, uid="fixture-1", version_sha256=digest,
                                     title="Documento sintético, sin valor jurídico")
        AccessGrant.objects.create(user=ana, group=group, collection=collection, origin="synthetic",
            valid_from=timezone.now() - timedelta(minutes=1), valid_until=timezone.now() + timedelta(days=1),
            issued_by=ana, evidence_id="synthetic-only")
        PolicyState.objects.create(quarantined=False)
    snapshot.chmod(0o400)
    return {"collection": str(collection.pk), "uid": row.uid, "version": digest}


class Command(BaseCommand):
    """Create an explicit disposable fictional workspace, never real accounts."""
    help = "Provision synthetic fixtures into an empty test-profile database"

    def add_arguments(self, parser) -> None:
        """Require a new immutable snapshot destination."""
        parser.add_argument("--snapshot", required=True)

    def handle(self, *args, **options) -> None:
        """Run provisioning without starting any listener."""
        self.stdout.write(json.dumps(provision(Path(options["snapshot"]))))
