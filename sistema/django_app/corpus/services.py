"""sistema/django_app/corpus/services.py: authorized application operations."""
import time
from django.db import transaction
from contracts import corpus_django as dto
from . import access
from .reader import read_exact, search_snapshot
from .models import SavedReference, PrivateFeedback


def locator_of(row) -> dto.DocumentLocator:
    """Convert a server catalog row into the public exact-version locator."""
    return dto.DocumentLocator(row.collection_id, row.uid, row.version_sha256)


class Application:
    """Implement the approved application protocol without fixture auth."""

    def authorize(self, principal, locator) -> dto.AccessDecision:
        """Check current policy without reading text."""
        return access.authorize(principal, locator)

    @transaction.atomic
    def read(self, principal, locator, start: int, limit: int) -> dto.TextSlice:
        """Read only after authorization; bounds checked independently of HTTP."""
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 10000:
            raise access.CorpusError(dto.ErrorCode.INVALID_INPUT)
        result = read_exact(access.require(principal, locator), start, limit)
        return dto.TextSlice(locator, result["text"], result["start"], result["end"],
                             result["total_characters"],
                             result["next"]["start"] if result["next"] else None,
                             result["source_url"], result["source_sha256"],
                             "secondary", "NOT_MEASURED")

    @transaction.atomic
    def search(self, principal, query: str, offset: int, limit: int) -> dto.SearchPage:
        """Search all authorized versions using verified FTS or exact fixture reads."""
        if (not isinstance(query, str) or not query.strip() or len(query) > 128
                or len(query.encode()) > 256 or type(offset) is not int
                or not 0 <= offset <= 10000 or type(limit) is not int or not 1 <= limit <= 20):
            raise access.CorpusError(dto.ErrorCode.INVALID_INPUT)
        rows = list(access.eligible(principal).select_related("collection").order_by(
            "collection_id", "uid", "version_sha256"))
        if not rows:
            return dto.SearchPage((), offset, None)
        allowed = {row.uid for row in rows}
        snippets = search_snapshot(rows[0], query.strip(), allowed)
        if snippets is None:
            deadline, consumed, hits = time.monotonic() + 5, 0, []
            needle = query.casefold()
            for row in rows[:201]:
                pieces, start = [], 0
                while True:
                    result = read_exact(row, start, 10000)
                    pieces.append(result["text"])
                    consumed += len(result["text"])
                    if consumed > 2_000_000 or time.monotonic() > deadline:
                        raise access.CorpusError(dto.ErrorCode.SERVICE_UNAVAILABLE)
                    if result["next"] is None:
                        break
                    start = result["next"]["start"]
                text = "".join(pieces)
                position = text.casefold().find(needle)
                if position >= 0 or needle in row.title.casefold():
                    snippet = text[max(0, position - 60):max(0, position - 60) + 240]
                    hits.append(dto.SearchHit(locator_of(row), row.title, snippet,
                                              "secondary", "NOT_MEASURED"))
        else:
            hits = [dto.SearchHit(locator_of(row), row.title, snippets[row.uid],
                                  "secondary", "NOT_MEASURED")
                    for row in rows if row.uid in snippets]
        end = offset + limit
        return dto.SearchPage(tuple(hits[offset:end]), offset,
                              end if end < len(hits) else None)

    @transaction.atomic
    def save_reference(self, principal, locator) -> dto.SavedReference:
        """Persist an owned locator, not content; request is freshly authorized."""
        row = access.require(principal, locator)
        saved, _ = SavedReference.objects.get_or_create(owner_id=principal.user_id, locator=row)
        return dto.SavedReference(saved.id, saved.owner_id, locator, saved.created_at)

    @transaction.atomic
    def list_references(self, principal) -> tuple[dto.SavedReference, ...]:
        """Hide references whose exact locators are no longer authorized."""
        allowed = access.eligible(principal).values("id")
        rows = SavedReference.objects.filter(owner_id=principal.user_id, locator_id__in=allowed
                                              ).select_related("locator").order_by("created_at")
        return tuple(dto.SavedReference(r.id, r.owner_id, locator_of(r.locator), r.created_at) for r in rows)

    @transaction.atomic
    def report_error(self, principal, locator, category: str, description: str) -> dto.FeedbackReceipt:
        """Store bounded private plain text; never send a notification."""
        if (category not in {"extraction", "metadata", "access", "other"}
                or not isinstance(description, str) or not 1 <= len(description.strip()) <= 2000):
            raise access.CorpusError(dto.ErrorCode.INVALID_INPUT)
        row = access.require(principal, locator)
        receipt = PrivateFeedback.objects.create(owner_id=principal.user_id, locator=row,
                                                 category=category, description=description.strip())
        return dto.FeedbackReceipt(receipt.id, receipt.created_at, "received")


class OfflineRecovery:
    """Implement RecoveryService using an injected operator-owned backup registry."""
    def __init__(self, registry: dict) -> None:
        self.registry = dict(registry)

    def restore_quarantined(self, backup_id, current_policy_revision: int) -> dto.RecoveryReceipt:
        """Resolve a registered backup and return the actual quarantined epoch."""
        import sqlite3
        from uuid import UUID, uuid4
        from contextlib import closing
        from pathlib import Path
        from django.core.management.base import CommandError
        from .management.commands.recover_snapshot import recover
        if not isinstance(backup_id, UUID) or backup_id not in self.registry:
            raise access.CorpusError(dto.ErrorCode.INVALID_INPUT)
        source, digest, target = self.registry[backup_id]
        try:
            recover(Path(source), digest, Path(target), current_policy_revision)
            with closing(sqlite3.connect(Path(target).as_uri() + "?mode=ro", uri=True)) as db:
                revision, epoch, quarantined = db.execute(
                    "SELECT revision,session_epoch,quarantined FROM corpus_policystate WHERE id=1").fetchone()
                if not quarantined:
                    raise access.CorpusError(dto.ErrorCode.INTEGRITY_FAILED)
            return dto.RecoveryReceipt(uuid4(), digest, revision, epoch, True, False)
        except (OSError, sqlite3.Error, ValueError, CommandError) as exc:
            raise access.CorpusError(dto.ErrorCode.RESTORE_QUARANTINED) from exc
