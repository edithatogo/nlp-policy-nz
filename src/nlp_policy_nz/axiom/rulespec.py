"""Lightweight RuleSpec identity bridge for NZ source records."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nlp_policy_nz.axiom.source import SourceSectionMetadata
    from nlp_policy_nz.storage.serialization import PipelineRecord


@dataclass(frozen=True)
class RuleSpecReference:
    """Durable RuleSpec concept reference without runtime coupling."""

    jurisdiction: str
    path: str
    concept: str

    def __post_init__(self) -> None:
        """Normalize direct references to the same shape as factory output."""
        object.__setattr__(self, "jurisdiction", _normalise_namespace(self.jurisdiction))
        object.__setattr__(self, "path", _normalise_path(self.path))
        object.__setattr__(self, "concept", _normalise_concept(self.concept))

    @property
    def durable_id(self) -> str:
        """Return the `nz:<path>#<concept>` durable identifier."""
        return f"{self.jurisdiction}:{self.path}#{self.concept}"

    def to_dict(self) -> dict[str, str]:
        """Return a JSON/YAML-compatible representation."""
        payload = asdict(self)
        payload["durable_id"] = self.durable_id
        return payload


def make_rulespec_reference(
    citation_path: str,
    concept: str,
    *,
    jurisdiction: str = "nz",
) -> RuleSpecReference:
    """Create a normalized RuleSpec reference from a corpus citation path."""
    path = _normalise_path(citation_path)
    concept_id = _normalise_concept(concept)
    return RuleSpecReference(
        jurisdiction=_normalise_namespace(jurisdiction),
        path=path,
        concept=concept_id,
    )


def pipeline_record_rulespec_reference(
    record: PipelineRecord,
    *,
    concept: str | None = None,
) -> RuleSpecReference:
    """Map a pipeline record or NZ provision identifier to a RuleSpec reference."""
    citation_path = record.nz_act_citations[0] if record.nz_act_citations else record.doc_id
    return make_rulespec_reference(
        citation_path,
        concept or _infer_concept(record),
        jurisdiction="nz",
    )


def source_verification_metadata(
    metadata: SourceSectionMetadata,
    *,
    concept: str,
) -> dict[str, Any]:
    """Export candidate metadata for a future `rulespec-nz` module."""
    reference = make_rulespec_reference(metadata.citation_path, concept)
    return {
        "rulespec_reference": reference.to_dict(),
        "module": {
            "source_verification": {
                "corpus_citation_path": metadata.citation_path,
                "jurisdiction": metadata.jurisdiction,
                "document_type": metadata.document_type,
            }
        },
        "provenance": {
            "authoritative_source_url": metadata.source_url,
            "retrieved_at": metadata.retrieved_at,
            "source_sha256": metadata.checksum_sha256,
        },
    }


def _infer_concept(record: PipelineRecord) -> str:
    """Infer a stable concept fragment from record annotations."""
    if record.legal_effect:
        return record.legal_effect
    if record.deontic_modality:
        label = record.deontic_modality[0].get("label") or record.deontic_modality[0].get(
            "modality"
        )
        if label:
            return str(label)
    return "source_text"


def _normalise_namespace(value: str) -> str:
    """Normalize a jurisdiction namespace."""
    stripped = value.strip().lower().rstrip(":")
    if not stripped:
        raise ValueError("RuleSpec jurisdiction is required")
    return stripped


def _normalise_path(value: str) -> str:
    """Normalize a citation path for a durable RuleSpec ID."""
    stripped = value.strip()
    if not stripped:
        raise ValueError("RuleSpec citation path is required")
    if ":" in stripped:
        namespace, path = stripped.split(":", 1)
        if namespace.lower() == "nz":
            stripped = path
    if stripped.lower().startswith("nz/"):
        stripped = stripped[3:]
    stripped = stripped.strip("/")
    normalised = re.sub(r"[^a-zA-Z0-9/_\-.]+", "-", stripped).strip("-").lower()
    if not normalised:
        raise ValueError("RuleSpec citation path must contain identifier characters")
    return normalised


def _normalise_concept(value: str) -> str:
    """Normalize a concept fragment for a durable RuleSpec ID."""
    stripped = value.strip().lower()
    if not stripped:
        raise ValueError("RuleSpec concept is required")
    normalised = re.sub(r"[^a-z0-9_]+", "_", stripped).strip("_")
    if not normalised:
        raise ValueError("RuleSpec concept must contain identifier characters")
    return normalised
