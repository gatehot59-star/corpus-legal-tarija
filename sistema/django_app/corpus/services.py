"""sistema/django_app/corpus/services.py: authorized application operations."""
import math
import re
import secrets
import time
from collections import Counter
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.utils import timezone
from contracts import corpus_django as dto
from . import access
from .reader import read_exact, search_snapshot, browse_snapshot
from .models import (SavedReference, PrivateFeedback, Collection, AccessGrant, Membership,
                     PilotAccount, PilotEvent)


def locator_of(row) -> dto.DocumentLocator:
    """Convert a server catalog row into the public exact-version locator."""
    return dto.DocumentLocator(row.collection_id, row.uid, row.version_sha256)


SESSION_GAP = timedelta(minutes=30)
READER_PAGE_CHARS = 4000


def citation_for(title: str, uid: str) -> str:
    """Build a transparent internal citation, not a pretend official citation."""
    clean_title = " ".join((title or uid or "Documento").split()).strip()
    clean_uid = " ".join(str(uid or "sin-uid").split()).strip()
    return f"{clean_title}, Corpus Tarija, documento {clean_uid}."


def usage_for(lawyer) -> dict:
    """Estimate usage from recorded events: visits, minutes, sections and last visit."""
    events = list(PilotEvent.objects.filter(lawyer=lawyer).order_by("at"))
    minutes = 0.0
    sessions = 0
    last = None
    for event in events:
        if last is None or event.at - last > SESSION_GAP:
            sessions += 1
            minutes += 1.0
        else:
            minutes += (event.at - last).total_seconds() / 60
        last = event.at
    sections = Counter(event.section for event in events).most_common(3)
    return {"pages": len(events), "sessions": sessions, "minutes": int(round(minutes)),
            "last_at": last, "sections": sections}


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
        row = access.require(principal, locator)
        result = read_exact(row, start, limit)
        page_total = max(1, math.ceil(result["total_characters"] / READER_PAGE_CHARS))
        page_number = min(page_total, max(1, (result["start"] // READER_PAGE_CHARS) + 1))
        return dto.TextSlice(locator, result["text"], result["start"], result["end"],
                             result["total_characters"],
                             result["next"]["start"] if result["next"] else None,
                             result["source_url"], result["source_sha256"],
                             "secondary", "NOT_MEASURED",
                             citation_for(row.title, row.uid), page_number, page_total)

    @transaction.atomic
    def search(self, principal, query: str, offset: int, limit: int,
               source: str = "", rubro: str = "", tipo: str = "") -> dto.SearchPage:
        """Search authorized versions using verified FTS or exact fixture reads."""
        if (not isinstance(query, str) or not query.strip() or len(query) > 128
                or len(query.encode()) > 256 or type(offset) is not int
                or not 0 <= offset <= 10000 or type(limit) is not int or not 1 <= limit <= 20):
            raise access.CorpusError(dto.ErrorCode.INVALID_INPUT)
        rows = list(access.eligible(principal).select_related("collection").order_by(
            "collection_id", "uid", "version_sha256"))
        if not rows:
            return dto.SearchPage((), offset, None)
        versions = {row.uid: row.version_sha256 for row in rows}
        filtered = browse_snapshot(rows[0], versions, source, rubro, tipo, 0, 50)
        matches_by_uid = {item["uid"]: item for item in filtered["items"]}
        rows = [row for row in rows if row.uid in matches_by_uid]
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
                    meta = matches_by_uid.get(row.uid, {})
                    hits.append(dto.SearchHit(locator_of(row), row.title, snippet,
                                              "secondary", "NOT_MEASURED",
                                              citation_for(row.title, row.uid),
                                              meta.get("source_name", ""), meta.get("matter", ""),
                                              meta.get("type", "")))
        else:
            hits = []
            for row in rows:
                if row.uid not in snippets:
                    continue
                meta = matches_by_uid.get(row.uid, {})
                hits.append(dto.SearchHit(locator_of(row), row.title, snippets[row.uid],
                                          "secondary", "NOT_MEASURED",
                                          citation_for(row.title, row.uid),
                                          meta.get("source_name", ""), meta.get("matter", ""),
                                          meta.get("type", "")))
        end = offset + limit
        return dto.SearchPage(tuple(hits[offset:end]), offset,
                              end if end < len(hits) else None)

    @transaction.atomic
    def browse(self, principal, source: str = "", rubro: str = "", tipo: str = "",
               offset: int = 0, limit: int = 20) -> dict:
        """Browse authorized metadata by source, matter and norm type."""
        if any(not isinstance(value, str) or len(value) > 120 for value in (source, rubro, tipo)):
            raise access.CorpusError(dto.ErrorCode.INVALID_INPUT)
        if type(offset) is not int or not 0 <= offset <= 10000 or type(limit) is not int or not 1 <= limit <= 50:
            raise access.CorpusError(dto.ErrorCode.INVALID_INPUT)
        rows = list(access.eligible(principal).select_related("collection").order_by(
            "collection_id", "uid", "version_sha256"))
        if not rows:
            return {"items": (), "sources": (), "rubros": (), "tipos": (), "next_offset": None}
        versions = {row.uid: row.version_sha256 for row in rows}
        result = browse_snapshot(rows[0], versions, source, rubro, tipo, offset, limit)
        result["items"] = tuple(dict(item, citation=citation_for(item["title"], item["uid"]))
                                for item in result["items"])
        return result

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

    @staticmethod
    def _pilot_username(first: str, last: str) -> str:
        """Build a readable unique pilot username from the lawyer's name."""
        base = re.sub(r"[^a-z0-9]", "", f"{first}.{last}".lower())
        if len(base) < 3:
            raise access.CorpusError(dto.ErrorCode.INVALID_INPUT)
        candidate = base
        suffix = 2
        users = get_user_model()
        while users.objects.filter(username=candidate).exists():
            candidate = f"{base}{suffix}"
            suffix += 1
            if suffix > 200:
                raise access.CorpusError(dto.ErrorCode.SERVICE_UNAVAILABLE)
        return candidate

    @transaction.atomic
    def create_pilot(self, operator: dto.Principal, first_name: str, last_name: str,
                     bar_number: str = "") -> dict:
        """Create a working pilot account: user, membership, grant and receipt."""
        state_for = access.state_for(operator)
        if not (first_name.strip() and last_name.strip()) or len(bar_number) > 40:
            raise access.CorpusError(dto.ErrorCode.INVALID_INPUT)
        users = get_user_model()
        operator_user = users.objects.filter(pk=operator.user_id, is_active=True).first()
        if operator_user is None:
            raise access.CorpusError(dto.ErrorCode.ACCESS_DENIED)
        group = Group.objects.filter(membership__user_id=operator.user_id,
                                     membership__enabled=True).first()
        collection = Collection.objects.filter(enabled=True).order_by("name").first()
        if group is None or collection is None:
            raise access.CorpusError(dto.ErrorCode.SERVICE_UNAVAILABLE)
        now = timezone.now()
        username = self._pilot_username(first_name, last_name)
        password = secrets.token_urlsafe(9)
        lawyer = users.objects.create_user(username=username, password=password,
                                           first_name=first_name.strip(), last_name=last_name.strip())
        Membership.objects.create(user=lawyer, group=group, enabled=True)
        AccessGrant.objects.create(
            user=lawyer, group=group, collection=collection, origin="pilot",
            valid_from=now, valid_until=now + timedelta(days=30),
            issued_by=operator_user, evidence_id=f"pilot:{state_for.revision}")
        PilotAccount.objects.create(lawyer=lawyer, first_name=first_name.strip(),
                                    last_name=last_name.strip(), bar_number=bar_number.strip(),
                                    created_by=operator_user)
        return {"username": username, "password": password}

    @transaction.atomic
    def reissue_pilot_password(self, operator: dto.Principal, account_id) -> dict:
        """Re-issue a lawyer's password: shown once to the employee, stored hashed."""
        access.require_employee(operator)
        account = PilotAccount.objects.select_related("lawyer").filter(pk=account_id).first()
        if account is None or account.status != "activa":
            raise access.CorpusError(dto.ErrorCode.INVALID_INPUT)
        password = secrets.token_urlsafe(9)
        account.lawyer.set_password(password)
        account.lawyer.save(update_fields=["password"])
        return {"username": account.lawyer.username, "password": password}

    @transaction.atomic
    def deactivate_pilot(self, operator: dto.Principal, account_id) -> str:
        """Remove a lawyer's access: account off, grants revoked, history preserved."""
        access.require_employee(operator)
        account = PilotAccount.objects.select_related("lawyer").filter(pk=account_id).first()
        if account is None or account.status != "activa":
            raise access.CorpusError(dto.ErrorCode.INVALID_INPUT)
        now = timezone.now()
        account.status = "eliminada"
        account.save(update_fields=["status"])
        lawyer = account.lawyer
        lawyer.is_active = False
        lawyer.save(update_fields=["is_active"])
        AccessGrant.objects.filter(user=lawyer, revoked_at__isnull=True).update(revoked_at=now)
        Membership.objects.filter(user=lawyer, enabled=True).update(enabled=False)
        return lawyer.username


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
