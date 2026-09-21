"""Corpus Django application boundaries, not an implemented authorization service.

Values describe the approved architecture. They do not validate untrusted input,
issue accounts, prove legal approval, or authorize a deployment.
"""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Literal, Protocol
from uuid import UUID


class ErrorCode(StrEnum):
    """Public failures; responses must not reveal document or account existence."""

    INVALID_INPUT = "INVALID_INPUT"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    ACCESS_DENIED = "ACCESS_DENIED"
    INTEGRITY_FAILED = "INTEGRITY_FAILED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    RATE_LIMITED = "RATE_LIMITED"
    RESTORE_QUARANTINED = "RESTORE_QUARANTINED"


@dataclass(frozen=True)
class DocumentLocator:
    """Server-approved collection, stable legacy UID and exact text digest."""

    collection_id: UUID
    uid: str
    version_sha256: str


@dataclass(frozen=True)
class Principal:
    """Identity resolved from Django's server-side session, never client headers."""

    user_id: int
    session_epoch: int


@dataclass(frozen=True)
class AccessDecision:
    """A request-local decision, not a reusable bearer capability."""

    allowed: bool
    policy_revision: int
    checked_at: datetime


@dataclass(frozen=True)
class TextSlice:
    """Exact text plus provenance; authority is not inferred from extraction."""

    locator: DocumentLocator
    text: str
    start: int
    end: int
    total_characters: int
    next_start: int | None
    source_url: str
    source_sha256: str
    authority: Literal["secondary"]
    legal_validity: Literal["NOT_MEASURED"]


@dataclass(frozen=True)
class SearchHit:
    """Metadata emitted only after the locator passes the current access policy."""

    locator: DocumentLocator
    title: str
    snippet: str
    authority: Literal["secondary"]
    legal_validity: Literal["NOT_MEASURED"]


@dataclass(frozen=True)
class SearchPage:
    """Stable authorized ordering; offset is not an authorization token."""

    results: tuple[SearchHit, ...]
    offset: int
    next_offset: int | None


@dataclass(frozen=True)
class SavedReference:
    """Private owned locator, not a copy of protected document text."""

    id: UUID
    owner_id: int
    locator: DocumentLocator
    created_at: datetime


@dataclass(frozen=True)
class FeedbackReceipt:
    """Private acknowledgement; no public issue or third-party notification."""

    id: UUID
    created_at: datetime
    status: Literal["received"]


@dataclass(frozen=True)
class RecoveryReceipt:
    """Recovery remains quarantined until a separately authorized reconciliation."""

    id: UUID
    snapshot_sha256: str
    policy_revision: int
    session_epoch: int
    quarantined: Literal[True]
    serve_authorized: Literal[False]


class CorpusApplication(Protocol):
    """Authenticated application boundary shared by views and operator tooling."""

    @abstractmethod
    def authorize(self, principal: Principal, locator: DocumentLocator) -> AccessDecision:
        """Check active user, current session, grant, group, collection and withdrawal."""
        raise NotImplementedError

    @abstractmethod
    def search(self, principal: Principal, query: str, offset: int, limit: int) -> SearchPage:
        """Restrict eligible documents before reading text or constructing snippets."""
        raise NotImplementedError

    @abstractmethod
    def read(self, principal: Principal, locator: DocumentLocator,
             start: int, limit: int) -> TextSlice:
        """Reauthorize this request, then call the existing exact-version reader."""
        raise NotImplementedError

    @abstractmethod
    def save_reference(self, principal: Principal, locator: DocumentLocator) -> SavedReference:
        """Reauthorize and persist only an owned locator and creation timestamp."""
        raise NotImplementedError

    @abstractmethod
    def list_references(self, principal: Principal) -> tuple[SavedReference, ...]:
        """Return this owner's references, hiding metadata for newly denied locators."""
        raise NotImplementedError

    @abstractmethod
    def report_error(self, principal: Principal, locator: DocumentLocator,
                     category: str, description: str) -> FeedbackReceipt:
        """Reauthorize, validate bounded plain text and persist a private report."""
        raise NotImplementedError


class RecoveryService(Protocol):
    """Offline operation; never start a listener or reuse backed-up sessions."""

    @abstractmethod
    def restore_quarantined(self, backup_id: UUID, current_policy_revision: int) -> RecoveryReceipt:
        """Reject stale/missing policy authority and produce a new quarantined target."""
        raise NotImplementedError
