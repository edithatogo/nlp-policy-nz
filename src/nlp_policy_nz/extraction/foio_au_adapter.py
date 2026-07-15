"""Profile-isolated Australian FOI-O archive extraction.

The pilot deliberately supports only Commonwealth and NSW profiles.  Routing
is fail-closed and the output remains a review-bound candidate bundle; this
module does not make legal assertions or promote labels.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from enum import StrEnum
from pathlib import Path
from typing import Literal

import orjson
from pydantic import BaseModel, ConfigDict, Field

from nlp_policy_nz.extraction.foio_adapter import (
    FoioLabelMetrics,
    evaluate_foio_candidates,
)
from nlp_policy_nz.extraction.schemas import (
    ExtractionManifest,
    ExtractionRecord,
    extraction_manifest_from_records,
)


class AustralianJurisdiction(StrEnum):
    """Jurisdiction profiles enabled by the Australian pilot."""

    COMMONWEALTH = "Cth"
    NSW = "NSW"


class AustralianRoutingDecision(BaseModel):
    """Deterministic route or abstention decision for one source record."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: Literal["routed", "abstained"]
    jurisdiction: AustralianJurisdiction | None = None
    reason: str = Field(min_length=1)
    evidence: tuple[str, ...] = Field(default_factory=tuple)


class FoioAustralianProfileSnapshot(BaseModel):
    """Immutable archive, legal-profile, ontology, and model identities."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    jurisdiction: AustralianJurisdiction
    profile_id: str = Field(min_length=1)
    archive_repository: str = Field(min_length=1)
    archive_revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    archive_content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    legal_source_revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    legal_source_url: str = Field(min_length=1)
    ontology_version: str = Field(min_length=1)
    model_revision: str = Field(min_length=1)
    schema_version: str = Field(min_length=1)
    extraction_contract_version: str = Field(min_length=1)
    pipeline_version: str = Field(min_length=1)
    retrieved_at: str = Field(min_length=1)


class FoioAustralianArchiveBundle(BaseModel):
    """Candidate-only output for exactly one Australian profile."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    producer: str = "nlp-policy-nz"
    review_status: Literal["candidate"] = "candidate"
    snapshot: FoioAustralianProfileSnapshot
    manifest: ExtractionManifest


class FoioAustralianJurisdictionEvaluation(BaseModel):
    """Metrics and abstention evidence for one Australian jurisdiction."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    jurisdiction: AustralianJurisdiction
    reference_records: int = Field(ge=0)
    candidate_records: int = Field(ge=0)
    metrics: tuple[FoioLabelMetrics, ...]
    disagreement_count: int = Field(ge=0)
    abstention_count: int = Field(ge=0)


class FoioAustralianEvaluationReport(BaseModel):
    """Deterministic per-profile evaluation report."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    jurisdictions: tuple[FoioAustralianJurisdictionEvaluation, ...]


class FoioAustralianEvaluationFixture(BaseModel):
    """Bounded profile-isolated fixture for Commonwealth and NSW."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    snapshots: tuple[FoioAustralianProfileSnapshot, ...]
    reference_records: tuple[ExtractionRecord, ...]
    candidate_records: tuple[ExtractionRecord, ...]
    abstained_record_ids: tuple[str, ...] = Field(default_factory=tuple)


_COMMONWEALTH_MARKERS = (
    "commonwealth",
    "federal",
    "cth",
    "comlaw",
    "legislation.gov.au",
    "(cth)",
)
_NSW_MARKERS = (
    "new south wales",
    "nsw",
    "legislation.nsw.gov.au",
    "(nsw)",
)


def route_australian_jurisdiction(
    record: ExtractionRecord,
    *,
    explicit_jurisdiction: str | None = None,
) -> AustralianRoutingDecision:
    """Route a source to Cth/NSW or abstain when evidence is insufficient.

    The function intentionally treats ``AU`` and generic Australian language
    as insufficient: a Commonwealth-versus-state distinction is required.
    """
    attributes = record.attributes
    explicit = explicit_jurisdiction or _attribute_jurisdiction(attributes)
    if explicit is not None:
        normalized = explicit.strip().lower()
        aliases = {
            "cth": AustralianJurisdiction.COMMONWEALTH,
            "commonwealth": AustralianJurisdiction.COMMONWEALTH,
            "federal": AustralianJurisdiction.COMMONWEALTH,
            "nsw": AustralianJurisdiction.NSW,
            "new south wales": AustralianJurisdiction.NSW,
        }
        jurisdiction = aliases.get(normalized)
        if jurisdiction is None:
            return AustralianRoutingDecision(
                status="abstained",
                reason="unsupported explicit jurisdiction",
                evidence=(explicit,),
            )
        return AustralianRoutingDecision(
            status="routed",
            jurisdiction=jurisdiction,
            reason="explicit jurisdiction attribute",
            evidence=(explicit,),
        )

    haystack = " ".join(
        (
            record.source_trace.citation_path,
            record.source_trace.source_url,
            str(attributes.get("title", "")),
            str(attributes.get("source_name", "")),
        )
    ).lower()
    matches: list[tuple[AustralianJurisdiction, str]] = []
    matches.extend(
        (AustralianJurisdiction.COMMONWEALTH, marker)
        for marker in _COMMONWEALTH_MARKERS
        if marker in haystack
    )
    matches.extend(
        (AustralianJurisdiction.NSW, marker)
        for marker in _NSW_MARKERS
        if marker in haystack
    )
    distinct = {jurisdiction for jurisdiction, _ in matches}
    if len(distinct) == 1:
        jurisdiction = next(iter(distinct))
        evidence = tuple(sorted({marker for _, marker in matches}))
        return AustralianRoutingDecision(
            status="routed",
            jurisdiction=jurisdiction,
            reason="unambiguous source marker",
            evidence=evidence,
        )
    if len(distinct) > 1:
        return AustralianRoutingDecision(
            status="abstained",
            reason="conflicting jurisdiction markers",
            evidence=tuple(sorted({marker for _, marker in matches})),
        )
    return AustralianRoutingDecision(
        status="abstained",
        reason="no supported Australian jurisdiction marker",
    )


def build_australian_archive_bundle(
    records: Iterable[ExtractionRecord],
    snapshot: FoioAustralianProfileSnapshot,
) -> FoioAustralianArchiveBundle:
    """Build a candidate bundle while enforcing profile isolation."""
    enriched: list[ExtractionRecord] = []
    for record in sorted(records, key=lambda item: item.record_id):
        decision = route_australian_jurisdiction(record)
        if decision.status == "abstained":
            raise ValueError(f"record {record.record_id} cannot be routed: {decision.reason}")
        if decision.jurisdiction != snapshot.jurisdiction:
            raise ValueError("cross-profile contamination: record jurisdiction does not match snapshot")
        if record.source_trace.source_sha256 != snapshot.archive_content_sha256:
            raise ValueError("source digest does not match pinned Australian archive snapshot")
        attributes = dict(record.attributes)
        attributes.update(
            {
                "foio_au_provenance": snapshot.model_dump(mode="json"),
                "foio_au_jurisdiction": snapshot.jurisdiction.value,
                "foio_au_routing_evidence": decision.evidence,
                "review_status": "candidate",
            }
        )
        enriched.append(record.model_copy(update={"attributes": attributes}))
    return FoioAustralianArchiveBundle(
        snapshot=snapshot,
        manifest=extraction_manifest_from_records(enriched),
    )


def render_australian_archive_bundle_json(bundle: FoioAustralianArchiveBundle) -> str:
    """Render stable JSON for downstream fyi-archive handoff."""
    return orjson.dumps(bundle.model_dump(mode="json"), option=orjson.OPT_SORT_KEYS).decode() + "\n"


def evaluate_australian_candidates(
    reference: Iterable[ExtractionRecord],
    candidate: Iterable[ExtractionRecord],
    *,
    abstained_record_ids: Iterable[str] = (),
) -> FoioAustralianEvaluationReport:
    """Evaluate Cth/NSW candidates independently, including abstentions."""
    reference_records = tuple(reference)
    candidate_records = tuple(candidate)
    grouped_reference: dict[AustralianJurisdiction, list[ExtractionRecord]] = defaultdict(list)
    grouped_candidate: dict[AustralianJurisdiction, list[ExtractionRecord]] = defaultdict(list)
    for collection, grouped in (
        (reference_records, grouped_reference),
        (candidate_records, grouped_candidate),
    ):
        for record in collection:
            decision = route_australian_jurisdiction(record)
            if decision.jurisdiction is not None:
                grouped[decision.jurisdiction].append(record)
    abstentions = set(abstained_record_ids)
    results: list[FoioAustralianJurisdictionEvaluation] = []
    for jurisdiction in AustralianJurisdiction:
        reference_group = grouped_reference[jurisdiction]
        candidate_group = grouped_candidate[jurisdiction]
        reference_by_id = {record.record_id: record for record in reference_group}
        disagreements = sum(
            1
            for record in candidate_group
            if (reference_record := reference_by_id.get(record.record_id)) is not None
            and (reference_record.family != record.family or reference_record.label != record.label)
        )
        report = evaluate_foio_candidates(reference_group, candidate_group)
        results.append(
            FoioAustralianJurisdictionEvaluation(
                jurisdiction=jurisdiction,
                reference_records=len(reference_group),
                candidate_records=len(candidate_group),
                metrics=report.metrics,
                disagreement_count=disagreements,
                abstention_count=sum(
                    1
                    for record_id in abstentions
                    if record_id.startswith(f"{jurisdiction.value}:")
                ),
            )
        )
    return FoioAustralianEvaluationReport(jurisdictions=tuple(results))


def render_australian_evaluation_json(report: FoioAustralianEvaluationReport) -> str:
    """Render a stable per-jurisdiction evaluation report."""
    return orjson.dumps(report.model_dump(mode="json"), option=orjson.OPT_SORT_KEYS).decode() + "\n"


def load_australian_evaluation_fixture(path: str | Path) -> FoioAustralianEvaluationFixture:
    """Load and validate a bounded Australian evaluation fixture."""
    return FoioAustralianEvaluationFixture.model_validate(orjson.loads(Path(path).read_bytes()))


def evaluate_australian_fixture(path: str | Path) -> FoioAustralianEvaluationReport:
    """Evaluate one bounded Australian fixture."""
    fixture = load_australian_evaluation_fixture(path)
    return evaluate_australian_candidates(
        fixture.reference_records,
        fixture.candidate_records,
        abstained_record_ids=fixture.abstained_record_ids,
    )


def _attribute_jurisdiction(attributes: dict[str, object]) -> str | None:
    value = attributes.get("foio_au_jurisdiction", attributes.get("jurisdiction"))
    return value if isinstance(value, str) else None
