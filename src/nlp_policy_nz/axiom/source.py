"""Axiom-style source-section records and source hash checks."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from typing import Literal, get_args

from nlp_policy_nz.storage.serialization import PipelineRecord

DocumentType = Literal[
    "act",
    "bill",
    "regulation",
    "hansard",
    "guidance",
    "select_committee_report",
    "parliament_submission",
    "regulations_review",
]
DOCUMENT_TYPES: tuple[str, ...] = get_args(DocumentType)


@dataclass(frozen=True)
class SourceSectionMetadata:
    """Metadata for one authoritative source-section text artifact."""

    citation_path: str
    jurisdiction: str
    document_type: DocumentType
    source_url: str
    retrieved_at: str
    checksum_sha256: str
    title: str | None = None
    version_id: str | None = None
    effective_date: str | None = None
    rights: str | None = None
    extra: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate source identity fields used by downstream provenance checks."""
        _require_nonempty("citation_path", self.citation_path)
        _require_nonempty("jurisdiction", self.jurisdiction)
        _validate_document_type(self.document_type)
        _require_nonempty("source_url", self.source_url)
        _require_nonempty("retrieved_at", self.retrieved_at)
        _validate_sha256(self.checksum_sha256)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON/YAML-compatible metadata mapping."""
        return asdict(self)


@dataclass(frozen=True)
class SourceSection:
    """Paired source text plus metadata before NLP pipeline conversion."""

    text: str
    metadata: SourceSectionMetadata

    @classmethod
    def from_text(
        cls,
        text: str,
        *,
        citation_path: str,
        jurisdiction: str,
        document_type: DocumentType,
        source_url: str,
        retrieved_at: str,
        title: str | None = None,
        version_id: str | None = None,
        effective_date: str | None = None,
        rights: str | None = None,
        extra: Mapping[str, object] | None = None,
    ) -> SourceSection:
        """Build a source section and stamp the checksum from exact text."""
        normalised = normalize_source_text(text)
        metadata = SourceSectionMetadata(
            citation_path=_require_nonempty("citation_path", citation_path),
            jurisdiction=_require_nonempty("jurisdiction", jurisdiction),
            document_type=_validate_document_type(document_type),
            source_url=_require_nonempty("source_url", source_url),
            retrieved_at=_require_nonempty("retrieved_at", retrieved_at),
            checksum_sha256=source_sha256(normalised),
            title=title,
            version_id=version_id,
            effective_date=effective_date,
            rights=rights,
            extra=extra or {},
        )
        return cls(text=normalised, metadata=metadata)


@dataclass(frozen=True)
class StalenessReport:
    """Non-mutating source hash comparison result."""

    citation_path: str
    status: Literal["current", "stale", "missing"]
    pinned_sha256: str
    current_sha256: str | None = None

    @property
    def is_stale(self) -> bool:
        """Return whether the current source no longer matches the pin."""
        return self.status != "current"

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-compatible staleness report."""
        return asdict(self)


def normalize_source_text(text: str) -> str:
    """Normalize source text without changing legally meaningful content."""
    lines = [re.sub(r"[ \t\r\f\v]+", " ", line).strip() for line in text.splitlines()]
    collapsed = "\n".join(line for line in lines if line)
    return collapsed.strip()


def source_sha256(text: str) -> str:
    """Return the SHA-256 hash of exact normalized source text."""
    return hashlib.sha256(normalize_source_text(text).encode("utf-8")).hexdigest()


def compare_source_staleness(
    pinned: SourceSectionMetadata,
    current_sources: Mapping[str, str],
) -> StalenessReport:
    """Compare a stored source hash against current corpus text."""
    current_text = current_sources.get(pinned.citation_path)
    if current_text is None:
        return StalenessReport(
            citation_path=pinned.citation_path,
            status="missing",
            pinned_sha256=pinned.checksum_sha256,
        )
    current_sha = source_sha256(current_text)
    return StalenessReport(
        citation_path=pinned.citation_path,
        status="current" if current_sha == pinned.checksum_sha256 else "stale",
        pinned_sha256=pinned.checksum_sha256,
        current_sha256=current_sha,
    )


def source_section_to_pipeline_record(
    section: SourceSection,
    *,
    doc_id: str | None = None,
    corpus_source: str | None = None,
) -> PipelineRecord:
    """Convert a source section into the existing pipeline schema."""
    tokens = re.findall(r"\b[\w\u0100-\u017F]+\b", section.text, flags=re.UNICODE)
    te_reo_terms = [token for token in tokens if any(char in token for char in "āēīōūĀĒĪŌŪ")]
    return PipelineRecord(
        doc_id=doc_id or section.metadata.citation_path,
        corpus_source=corpus_source or section.metadata.document_type,
        raw_text=section.text,
        cleaned_tokens=tokens,
        nz_act_citations=[section.metadata.citation_path],
        te_reo_terms=te_reo_terms,
        report_title=section.metadata.title,
    )


def _require_nonempty(name: str, value: str) -> str:
    """Return a stripped required value or raise a contract error."""
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{name} is required")
    return stripped


def _validate_document_type(value: str) -> DocumentType:
    """Return a supported source document type or raise a contract error."""
    stripped = value.strip()
    if stripped not in DOCUMENT_TYPES:
        allowed = ", ".join(DOCUMENT_TYPES)
        raise ValueError(f"document_type must be one of: {allowed}")
    return stripped  # type: ignore[return-value]


def _validate_sha256(value: str) -> str:
    """Return a valid lowercase SHA-256 hex digest or raise a contract error."""
    stripped = value.strip()
    if not re.fullmatch(r"[0-9a-f]{64}", stripped):
        raise ValueError("checksum_sha256 must be a lowercase 64-character SHA-256 hex digest")
    return stripped
