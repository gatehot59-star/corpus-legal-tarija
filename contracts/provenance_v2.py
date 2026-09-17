"""B01/I05 isolated contracts: identity, typed provenance and byte integrity.

This module does not migrate the legacy database or authorize publication.
IDs are assigned once by the catalog, never inferred from a legal number.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass
from datetime import date
from enum import Enum
from urllib.parse import urlsplit
from uuid import UUID


class ContractError(ValueError):
    """A supplied value violates the versioned contract."""


class Authority(str, Enum):
    """Publisher authority is independent of extraction method."""
    OFFICIAL = "official"
    SECONDARY = "secondary"
    UNKNOWN = "unknown"


class Method(str, Enum):
    """How text was obtained, without asserting legal correctness."""
    OCR = "ocr"
    PDF_TEXT = "pdf_text"
    HTML = "html"


class LegalStatus(str, Enum):
    """Unknown must not silently become current."""
    UNKNOWN = "unknown"
    HISTORICAL = "historical"
    PARTIAL = "partial"
    VERIFIED = "verified"


def require_id(value: str) -> str:
    """Validate a canonical, non-nil UUID; raise ContractError otherwise."""
    try:
        parsed = UUID(value)
    except (TypeError, ValueError, AttributeError) as exc:
        raise ContractError("invalid identity") from exc
    if not isinstance(value, str) or str(parsed) != value or parsed.int == 0:
        raise ContractError("identity must be canonical and non-nil")
    return value


def require_text(value: str, field: str, limit: int = 2048) -> str:
    """Reject blank, oversized or control-character-bearing metadata."""
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ContractError(f"invalid {field}")
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ContractError(f"control character in {field}")
    return value


def require_url(value: str) -> str:
    """Validate provenance URL syntax, not SSRF safety or publisher authority.

    No network call is made. B06 must separately check DNS and redirects.
    """
    require_text(value, "source_url", 4096)
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise ContractError("invalid URL") from exc
    if (parsed.scheme not in ("http", "https") or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or parsed.fragment or any(c.isspace() for c in value)):
        raise ContractError("invalid provenance URL")
    if port is not None and not 1 <= port <= 65535:
        raise ContractError("invalid URL port")
    return value


def verify_bytes(payload: bytes, expected_sha256: str) -> str:
    """Require a full lowercase SHA256 matching the exact supplied bytes.

    A matching digest establishes byte identity, not state authenticity,
    OCR fidelity, legal validity or permission to distribute.
    """
    if not isinstance(payload, bytes):
        raise ContractError("payload must be bytes")
    if not isinstance(expected_sha256, str) or re.fullmatch(
        r"[0-9a-f]{64}", expected_sha256
    ) is None:
        raise ContractError("full SHA256 required")
    actual = hashlib.sha256(payload).hexdigest()
    if not hmac.compare_digest(actual, expected_sha256):
        raise ContractError("byte digest mismatch")
    return actual


@dataclass(frozen=True)
class Work:
    """Stable legal work identity; equal numbers never imply equal works."""
    work_id: str
    issuer_id: str
    jurisdiction: str
    kind: str
    number: str

    def __post_init__(self) -> None:
        require_id(self.work_id)
        for field in ("issuer_id", "jurisdiction", "kind", "number"):
            require_text(getattr(self, field), field)


@dataclass(frozen=True)
class Version:
    """An edition belongs to one work and defaults to unknown legal status."""
    version_id: str
    work_id: str
    edition: str
    status: LegalStatus = LegalStatus.UNKNOWN
    legal_review_id: str | None = None

    def __post_init__(self) -> None:
        require_id(self.version_id)
        require_id(self.work_id)
        require_text(self.edition, "edition")
        if not isinstance(self.status, LegalStatus):
            raise ContractError("invalid legal status")
        if self.legal_review_id is not None:
            require_id(self.legal_review_id)
        if self.status != LegalStatus.UNKNOWN and self.legal_review_id is None:
            raise ContractError("legal assessment requires review evidence")


@dataclass(frozen=True)
class DatedEvidence:
    """Keep promulgation, sanction, session and edition dates distinct."""
    kind: str
    iso_date: str
    source_url: str
    locator: str

    def __post_init__(self) -> None:
        if self.kind not in {"promulgation", "sanction", "session", "edition"}:
            raise ContractError("unknown date semantics")
        if not isinstance(self.iso_date, str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}", self.iso_date
        ):
            raise ContractError("date must be ISO calendar date")
        try:
            date.fromisoformat(self.iso_date)
        except ValueError as exc:
            raise ContractError("invalid calendar date") from exc
        require_url(self.source_url)
        require_text(self.locator, "locator")


@dataclass(frozen=True)
class Extraction:
    """Two scoped digests and independent publisher/extraction metadata."""
    version_id: str
    source_url: str
    authority: Authority
    method: Method
    original_sha256: str
    text_sha256: str
    engine: str
    engine_version: str
    language: str
    fidelity_review_id: str | None = None

    def __post_init__(self) -> None:
        require_id(self.version_id)
        require_url(self.source_url)
        if not isinstance(self.authority, Authority) or not isinstance(self.method, Method):
            raise ContractError("authority and method must be explicit enums")
        for field in ("original_sha256", "text_sha256"):
            if not isinstance(getattr(self, field), str) or re.fullmatch(
                r"[0-9a-f]{64}", getattr(self, field)
            ) is None:
                raise ContractError("full scoped digest required")
        for field in ("engine", "engine_version", "language"):
            require_text(getattr(self, field), field)
        if self.fidelity_review_id is not None:
            require_id(self.fidelity_review_id)

    def verify(self, original: bytes, text_utf8: bytes) -> None:
        """Check original and derived bytes separately; raise on either mismatch."""
        verify_bytes(original, self.original_sha256)
        verify_bytes(text_utf8, self.text_sha256)
        try:
            text_utf8.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise ContractError("text must be strict UTF-8") from exc


def manifest_bytes(extractions: tuple[Extraction, ...]) -> bytes:
    """Serialize immutable artifact metadata using the corpus-manifest-v1 profile.

    Profile: UTF-8, ASCII-escaped JSON strings, sorted keys and artifact records,
    compact separators, no floats, LF terminator. It is not RFC8785 or a signature.
    Exact duplicate source records are rejected; alternative sources are retained.
    """
    if not isinstance(extractions, tuple) or not extractions:
        raise ContractError("nonempty tuple required")
    records: list[dict[str, str | None]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for item in extractions:
        if not isinstance(item, Extraction):
            raise ContractError("Extraction required")
        key = (item.version_id, item.source_url, item.original_sha256, item.text_sha256)
        if key in seen:
            raise ContractError("duplicate source record")
        seen.add(key)
        records.append({
            "version_id": item.version_id, "source_url": item.source_url,
            "authority": item.authority.value, "method": item.method.value,
            "original_sha256": item.original_sha256, "text_sha256": item.text_sha256,
            "engine": item.engine, "engine_version": item.engine_version,
            "language": item.language, "fidelity_review_id": item.fidelity_review_id,
        })
    records.sort(key=lambda r: (
        r["version_id"], r["source_url"], r["original_sha256"], r["text_sha256"]
    ))
    return (json.dumps({"profile": "corpus-manifest-v1", "artifacts": records},
                       sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8")
