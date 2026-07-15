"""FOI-O candidate adapter for pinned fyi-archive snapshots.

The adapter deliberately wraps the shared extraction manifest rather than
defining a second ontology.  Its output is a review-bound candidate bundle;
it cannot certify or promote legal findings.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import orjson
from pydantic import BaseModel, ConfigDict, Field

from nlp_policy_nz.extraction.schemas import (
    ExtractionFamily,
    ExtractionManifest,
    ExtractionRecord,
    extraction_manifest_from_records,
)


class FoioArchiveSnapshot(BaseModel):
    """Immutable identities required to reproduce one archive extraction."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    archive_repository: str = Field(min_length=1)
    archive_revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    archive_record_id: str = Field(min_length=1)
    archive_content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    ontology_version: str = Field(min_length=1)
    schema_version: str = Field(min_length=1)
    extraction_contract_version: str = Field(min_length=1)
    pipeline_version: str = Field(min_length=1)
    source_url: str = Field(default="https://huggingface.co/datasets/edithatogo/fyi-archive-nz")
    retrieved_at: str = Field(default="not-recorded", min_length=1)


class FoioArchiveBundle(BaseModel):
    """Portable candidate output handed to fyi-archive for review."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    producer: str = "nlp-policy-nz"
    review_status: Literal["candidate"] = "candidate"
    snapshot: FoioArchiveSnapshot
    manifest: ExtractionManifest


class FoioLabelMetrics(BaseModel):
    """Evaluation metrics for one FOI-O label family."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    family: ExtractionFamily
    true_positives: int = Field(ge=0)
    false_positives: int = Field(ge=0)
    false_negatives: int = Field(ge=0)
    precision: float = Field(ge=0.0, le=1.0)
    recall: float = Field(ge=0.0, le=1.0)
    f1: float = Field(ge=0.0, le=1.0)
    calibration_error: float = Field(ge=0.0, le=1.0)
    coverage: float = Field(ge=0.0, le=1.0)


class FoioEvaluationReport(BaseModel):
    """Deterministic evaluation report for candidate versus reviewed records."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    reference_records: int = Field(ge=0)
    candidate_records: int = Field(ge=0)
    metrics: tuple[FoioLabelMetrics, ...]


class FoioEvaluationFixture(BaseModel):
    """Pinned bounded fixture used for adapter evaluation and handoff."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    snapshot: FoioArchiveSnapshot
    reference_records: tuple[ExtractionRecord, ...]
    candidate_records: tuple[ExtractionRecord, ...]


def build_foio_archive_bundle(
    records: list[ExtractionRecord] | tuple[ExtractionRecord, ...],
    snapshot: FoioArchiveSnapshot,
) -> FoioArchiveBundle:
    """Build a sorted, provenance-enriched candidate bundle.

    Records are required to point at the pinned archive content digest.  The
    check prevents accidental mixing of source revisions in one derived layer.
    """
    enriched: list[ExtractionRecord] = []
    for record in sorted(records, key=lambda item: item.record_id):
        if record.source_trace.source_sha256 != snapshot.archive_content_sha256:
            raise ValueError("source digest does not match pinned archive snapshot")
        attributes = dict(record.attributes)
        attributes["foio_provenance"] = snapshot.model_dump(mode="json")
        enriched.append(record.model_copy(update={"attributes": attributes}))
    return FoioArchiveBundle(
        snapshot=snapshot,
        manifest=extraction_manifest_from_records(enriched),
    )


def render_foio_archive_bundle_json(bundle: FoioArchiveBundle) -> str:
    """Render a stable JSON handoff suitable for a derived manifest."""
    return (
        orjson.dumps(bundle.model_dump(mode="json"), option=orjson.OPT_SORT_KEYS).decode("utf-8")
        + "\n"
    )


def compare_foio_baseline(
    baseline: list[ExtractionRecord] | tuple[ExtractionRecord, ...],
    candidate: list[ExtractionRecord] | tuple[ExtractionRecord, ...],
) -> dict[str, tuple[str, ...]]:
    """Report stable added, removed, relabelled, and shifted record IDs."""
    before = {record.record_id: record for record in baseline}
    after = {record.record_id: record for record in candidate}
    common = before.keys() & after.keys()
    return {
        "added": tuple(sorted(after.keys() - before.keys())),
        "removed": tuple(sorted(before.keys() - after.keys())),
        "relabelled": tuple(
            sorted(
                record_id
                for record_id in common
                if before[record_id].label != after[record_id].label
            )
        ),
        "shifted": tuple(
            sorted(
                record_id
                for record_id in common
                if before[record_id].source_trace.spans != after[record_id].source_trace.spans
            )
        ),
    }


def evaluate_foio_candidates(
    reference: list[ExtractionRecord] | tuple[ExtractionRecord, ...],
    candidate: list[ExtractionRecord] | tuple[ExtractionRecord, ...],
) -> FoioEvaluationReport:
    """Evaluate exact family/label matches with confidence and coverage signals."""
    reference_by_id = {record.record_id: record for record in reference}
    families = sorted(
        {record.family for record in reference} | {record.family for record in candidate},
        key=str,
    )
    metrics: list[FoioLabelMetrics] = []
    for family in families:
        family_reference = [record for record in reference if record.family == family]
        family_candidate = [record for record in candidate if record.family == family]
        family_reference_ids = {record.record_id for record in family_reference}
        family_candidate_ids = {record.record_id for record in family_candidate}
        true_positives = sum(
            1
            for record in family_candidate
            if (reference_record := reference_by_id.get(record.record_id)) is not None
            and reference_record.family == record.family
            and reference_record.label == record.label
        )
        false_positives = len(family_candidate) - true_positives
        false_negatives = len(family_reference) - true_positives
        precision = _ratio(true_positives, len(family_candidate))
        recall = _ratio(true_positives, len(family_reference))
        f1 = _f1(precision, recall)
        calibration_error = _calibration_error(
            family_candidate,
            reference_by_id,
        )
        coverage = _ratio(len(family_reference_ids & family_candidate_ids), len(family_reference))
        metrics.append(
            FoioLabelMetrics(
                family=family,
                true_positives=true_positives,
                false_positives=false_positives,
                false_negatives=false_negatives,
                precision=precision,
                recall=recall,
                f1=f1,
                calibration_error=calibration_error,
                coverage=coverage,
            )
        )
    return FoioEvaluationReport(
        reference_records=len(reference),
        candidate_records=len(candidate),
        metrics=tuple(metrics),
    )


def render_foio_evaluation_json(report: FoioEvaluationReport) -> str:
    """Render a stable JSON evaluation report."""
    return (
        orjson.dumps(report.model_dump(mode="json"), option=orjson.OPT_SORT_KEYS).decode("utf-8")
        + "\n"
    )


def load_foio_evaluation_fixture(path: str | Path) -> FoioEvaluationFixture:
    """Load and validate a pinned JSON evaluation fixture."""
    fixture_path = Path(path)
    return FoioEvaluationFixture.model_validate(orjson.loads(fixture_path.read_bytes()))


def evaluate_foio_fixture(path: str | Path) -> FoioEvaluationReport:
    """Evaluate the reference and candidate records from one fixture."""
    fixture = load_foio_evaluation_fixture(path)
    return evaluate_foio_candidates(fixture.reference_records, fixture.candidate_records)


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _f1(precision: float, recall: float) -> float:
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _calibration_error(
    candidates: list[ExtractionRecord],
    reference_by_id: dict[str, ExtractionRecord],
) -> float:
    if not candidates:
        return 0.0
    total_error = 0.0
    for record in candidates:
        reference_record = reference_by_id.get(record.record_id)
        target = float(
            reference_record is not None
            and reference_record.family == record.family
            and reference_record.label == record.label
        )
        total_error += abs(record.confidence - target)
    return total_error / len(candidates)
