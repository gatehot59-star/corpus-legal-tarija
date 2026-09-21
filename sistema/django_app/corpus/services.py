"""sistema/django_app/corpus/services.py: authorized application operations."""
import time
from django.db import transaction
from contracts import corpus_django as dto
from . import access
from .reader import read_exact
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
        """Scan authorized versions within explicit budgets; never silently truncate."""
        if (not isinstance(query, str) or not query.strip() or len(query) > 128
                or len(query.encode()) > 256 or type(offset) is not int
                or not 0 <= offset <= 10000 or type(limit) is not int or not 1 <= limit <= 20):
            raise access.CorpusError(dto.ErrorCode.INVALID_INPUT)
        rows = list(access.eligible(principal).order_by("collection_id", "uid", "version_sha256")[:201])
        if len(rows) > 200:
            raise access.CorpusError(dto.ErrorCode.SERVICE_UNAVAILABLE)
        deadline, consumed, hits = time.monotonic() + 5, 0, []
        for row in rows:
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
            position = text.casefold().find(query.casefold())
            if position >= 0 or query.casefold() in row.title.casefold():
                # Matching via casefold can expand characters; snippet is indicative, not a locator.
                snippet = text[max(0, position - 60):max(0, position - 60) + 240]
                hits.append(dto.SearchHit(locator_of(row), row.title, snippet, "secondary", "NOT_MEASURED"))
        end = offset + limit
        return dto.SearchPage(tuple(hits[offset:end]), offset, end if end < len(hits) else None)

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
