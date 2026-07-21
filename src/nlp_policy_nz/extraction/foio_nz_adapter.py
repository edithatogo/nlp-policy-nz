"""Candidate-only New Zealand FOI-O profile adapter.

The adapter routes only explicit or unambiguous NZ/OIA source signals. It
preserves source digests and emits review-bound output; it does not interpret
the Official Information Act or claim empirical evaluation.
"""

from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from pathlib import Path
from typing import Literal

import orjson
from pydantic import BaseModel, ConfigDict, Field

from nlp_policy_nz.extraction.foio_adapter import FoioEvaluationReport, evaluate_foio_candidates
from nlp_policy_nz.extraction.schemas import (
    ExtractionManifest,
    ExtractionRecord,
    extraction_manifest_from_records,
)


class NewZealandJurisdiction(StrEnum):
    """Jurisdiction profile enabled by the NZ candidate adapter."""

    NZ = "NZ"


class NewZealandRoutingDecision(BaseModel):
    """Deterministic route or abstention decision for one source record."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: Literal["routed", "abstained"]
    jurisdiction: NewZealandJurisdiction | None = None
    reason: str = Field(min_length=1)
    evidence: tuple[str, ...] = Field(default_factory=tuple)


class FoioNewZealandProfileSnapshot(BaseModel):
    """Immutable identities for one candidate NZ source snapshot."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    jurisdiction: NewZealandJurisdiction = NewZealandJurisdiction.NZ
    profile_id: str = Field(min_length=1)
    archive_repository: str = Field(min_length=1)
    archive_revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    archive_content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_pack_revision: str = Field(min_length=1)
    source_pack_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    legal_source_url: str = Field(min_length=1)
    ontology_version: str = Field(min_length=1)
    schema_version: str = Field(min_length=1)
    extraction_contract_version: str = Field(min_length=1)
    pipeline_version: str = Field(min_length=1)
    retrieved_at: str = Field(min_length=1)


class FoioNewZealandArchiveBundle(BaseModel):
    """Candidate-only output for the NZ OIA profile."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    producer: str = "nlp-policy-nz"
    review_status: Literal["candidate"] = "candidate"
    snapshot: FoioNewZealandProfileSnapshot
    manifest: ExtractionManifest


class FoioNewZealandEvaluationFixture(BaseModel):
    """Contract-only fixture covering required NZ evaluation dimensions."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    fixture_status: Literal["contract-only"] = "contract-only"
    fixture_families: tuple[Literal["positive", "negative", "temporal", "non-equivalence"], ...]
    snapshot: FoioNewZealandProfileSnapshot
    reference_records: tuple[ExtractionRecord, ...]
    candidate_records: tuple[ExtractionRecord, ...]
    abstained_record_ids: tuple[str, ...] = Field(default_factory=tuple)


_NZ_MARKERS = ("new zealand", "nz", "oia", "official-information-act", "legislation.govt.nz", "fyi.org.nz")


def route_new_zealand_jurisdiction(
    record: ExtractionRecord,
    *,
    explicit_jurisdiction: str | None = None,
) -> NewZealandRoutingDecision:
    """Route an unambiguous NZ/OIA record or abstain."""
    explicit = explicit_jurisdiction or record.attributes.get("jurisdiction")
    if isinstance(explicit, str) and explicit.strip().lower() in {"nz", "new zealand", "aotearoa"}:
        return NewZealandRoutingDecision(
            status="routed",
            jurisdiction=NewZealandJurisdiction.NZ,
            reason="explicit jurisdiction attribute",
            evidence=(explicit,),
        )
    if explicit is not None:
        return NewZealandRoutingDecision(status="abstained", reason="unsupported explicit jurisdiction", evidence=(str(explicit),))
    haystack = " ".join(
        (record.source_trace.citation_path, record.source_trace.source_url, str(record.attributes.get("source_name", "")))
    ).lower()
    matches = tuple(marker for marker in _NZ_MARKERS if marker in haystack)
    if matches:
        return NewZealandRoutingDecision(
            status="routed", jurisdiction=NewZealandJurisdiction.NZ, reason="unambiguous NZ source marker", evidence=matches
        )
    return NewZealandRoutingDecision(status="abstained", reason="no supported NZ jurisdiction marker")


def build_new_zealand_archive_bundle(
    records: Iterable[ExtractionRecord], snapshot: FoioNewZealandProfileSnapshot
) -> FoioNewZealandArchiveBundle:
    """Build a candidate bundle while enforcing NZ profile and digest isolation."""
    enriched: list[ExtractionRecord] = []
    for record in sorted(records, key=lambda item: item.record_id):
        decision = route_new_zealand_jurisdiction(record)
        if decision.status == "abstained":
            raise ValueError(f"record {record.record_id} cannot be routed: {decision.reason}")
        if record.source_trace.source_sha256 != snapshot.archive_content_sha256:
            raise ValueError("source digest does not match pinned NZ archive snapshot")
        attributes = dict(record.attributes)
        attributes.update({"foio_nz_provenance": snapshot.model_dump(mode="json"), "review_status": "candidate"})
        enriched.append(record.model_copy(update={"attributes": attributes}))
    return FoioNewZealandArchiveBundle(snapshot=snapshot, manifest=extraction_manifest_from_records(enriched))


def render_new_zealand_archive_bundle_json(bundle: FoioNewZealandArchiveBundle) -> str:
    """Render stable JSON for downstream review handoff."""
    return orjson.dumps(bundle.model_dump(mode="json"), option=orjson.OPT_SORT_KEYS).decode() + "\n"


def evaluate_new_zealand_candidates(
    reference: Iterable[ExtractionRecord], candidate: Iterable[ExtractionRecord]
) -> FoioEvaluationReport:
    """Evaluate candidate labels without treating the result as promotion evidence."""
    return evaluate_foio_candidates(tuple(reference), tuple(candidate))


def load_new_zealand_evaluation_fixture(path: Path) -> FoioNewZealandEvaluationFixture:
    """Load a pinned contract-only NZ fixture."""
    return FoioNewZealandEvaluationFixture.model_validate_json(path.read_text(encoding="utf-8"))
