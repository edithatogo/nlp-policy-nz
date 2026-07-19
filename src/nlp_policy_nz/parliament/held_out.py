"""Leakage and promotion contracts for historical Parliament evaluation."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any, Literal

Split = Literal["train", "dev", "test"]

REQUIRED_METRICS = (
    "hierarchy_accuracy",
    "speaker_accuracy",
    "link_f1",
    "abstention_recall",
    "span_fidelity",
)
DEFAULT_THRESHOLDS = {
    "hierarchy_accuracy": 0.9,
    "speaker_accuracy": 0.9,
    "link_f1": 0.8,
    "abstention_recall": 0.9,
    "span_fidelity": 0.95,
}


@dataclass(frozen=True, slots=True)
class HistoricalParliamentRecord:
    """Metadata for one page-level split member, without page contents."""

    record_id: str
    source_id: str
    volume_id: str
    page_id: str
    split: Split
    source_sha256: str
    annotation_ref: str | None = None
    annotator_ids: tuple[str, ...] = ()
    adjudicator_ids: tuple[str, ...] = ()
    authority_evidence_ids: tuple[str, ...] = ()
    review_decision_ref: str | None = None


@dataclass(frozen=True, slots=True)
class HistoricalParliamentManifest:
    """Split manifest for a historical Parliament held-out evaluation."""

    schema_version: str
    status: str
    annotation_status: str
    annotation_units: tuple[str, ...]
    records: tuple[HistoricalParliamentRecord, ...]
    thresholds: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready manifest payload."""
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "annotation_status": self.annotation_status,
            "annotation_units": list(self.annotation_units),
            "records": [asdict(record) for record in self.records],
            "thresholds": dict(sorted(self.thresholds.items())),
        }


@dataclass(frozen=True, slots=True)
class HistoricalParliamentReport:
    """Fail-closed evaluation and promotion decision."""

    manifest_valid: bool
    test_record_count: int
    annotations_complete: bool
    authority_evidence_complete: bool
    measured_metrics: dict[str, float]
    promotion_ready: bool
    decision: Literal["no-promotion", "promote"]
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready report payload."""
        return {
            "manifest_valid": self.manifest_valid,
            "test_record_count": self.test_record_count,
            "annotations_complete": self.annotations_complete,
            "authority_evidence_complete": self.authority_evidence_complete,
            "measured_metrics": dict(sorted(self.measured_metrics.items())),
            "promotion_ready": self.promotion_ready,
            "decision": self.decision,
            "reasons": list(self.reasons),
        }


def validate_historical_manifest(
    manifest: HistoricalParliamentManifest,
) -> tuple[bool, tuple[str, ...]]:
    """Validate split isolation and evidence metadata without reading corpus text."""
    errors: list[str] = []
    missing_thresholds = [name for name in REQUIRED_METRICS if name not in manifest.thresholds]
    if missing_thresholds:
        errors.append("missing promotion thresholds: " + ", ".join(missing_thresholds))
    seen_records: set[str] = set()
    seen_pages: set[tuple[str, str]] = set()
    split_by_hash: dict[str, Split] = {}
    split_by_volume: dict[str, Split] = {}
    split_by_source: dict[str, Split] = {}
    for record in manifest.records:
        if record.split not in {"train", "dev", "test"}:
            errors.append(f"invalid split: {record.record_id}")
            continue
        if record.record_id in seen_records:
            errors.append(f"duplicate record id: {record.record_id}")
        seen_records.add(record.record_id)
        page_key = (record.source_id, record.page_id)
        if page_key in seen_pages:
            errors.append(f"duplicate source page: {record.source_id}/{record.page_id}")
        seen_pages.add(page_key)
        if record.source_sha256:
            previous_split = split_by_hash.setdefault(record.source_sha256, record.split)
            if previous_split != record.split:
                errors.append(f"hash leakage across splits: {record.record_id}")
        for key, value, label in (
            (split_by_volume, record.volume_id, "volume"),
            (split_by_source, record.source_id, "source"),
        ):
            previous_split = key.setdefault(value, record.split)
            if previous_split != record.split:
                errors.append(f"{label} leakage across splits: {value}")
        overlap = set(record.annotator_ids) & set(record.adjudicator_ids)
        if overlap:
            errors.append(f"annotator/adjudicator role overlap: {record.record_id}")
        if record.split == "test":
            if not record.annotation_ref:
                errors.append(f"missing held-out annotation: {record.record_id}")
            if not record.authority_evidence_ids:
                errors.append(f"missing authority evidence: {record.record_id}")
            if not record.review_decision_ref:
                errors.append(f"missing signed review decision: {record.record_id}")
    return (not errors, tuple(errors))


def evaluate_historical_manifest(
    manifest: HistoricalParliamentManifest,
    measured_metrics: Mapping[str, float] | None = None,
) -> HistoricalParliamentReport:
    """Produce a report that cannot promote absent real evidence and metrics."""
    manifest_valid, validation_errors = validate_historical_manifest(manifest)
    test_records = tuple(record for record in manifest.records if record.split == "test")
    annotations_complete = bool(test_records) and all(
        record.annotation_ref and record.review_decision_ref for record in test_records
    )
    authority_complete = bool(test_records) and all(
        record.authority_evidence_ids for record in test_records
    )
    metrics = dict(measured_metrics or {})
    reasons = list(validation_errors)
    if not test_records:
        reasons.append("no held-out test records are present")
    if not annotations_complete:
        reasons.append("held-out annotations and signed review decisions are incomplete")
    if not authority_complete:
        reasons.append("authority evidence is incomplete")
    missing_metrics = [name for name in REQUIRED_METRICS if name not in metrics]
    if missing_metrics:
        reasons.append("missing measured metrics: " + ", ".join(missing_metrics))
    for name in REQUIRED_METRICS:
        threshold = manifest.thresholds.get(name, DEFAULT_THRESHOLDS[name])
        if name in metrics and metrics[name] < threshold:
            reasons.append(f"metric below threshold: {name}")
    promotion_ready = not reasons and all(
        name in metrics and metrics[name] >= manifest.thresholds.get(name, DEFAULT_THRESHOLDS[name])
        for name in REQUIRED_METRICS
    )
    return HistoricalParliamentReport(
        manifest_valid=manifest_valid,
        test_record_count=len(test_records),
        annotations_complete=annotations_complete,
        authority_evidence_complete=authority_complete,
        measured_metrics=metrics,
        promotion_ready=promotion_ready,
        decision="promote" if promotion_ready else "no-promotion",
        reasons=tuple(dict.fromkeys(reasons)),
    )


def default_historical_manifest() -> HistoricalParliamentManifest:
    """Return the metadata-only Track 132 scaffold."""
    return HistoricalParliamentManifest(
        schema_version="track132-historical-parliament-v1",
        status="scaffold",
        annotation_status="not-present",
        annotation_units=(
            "hierarchy",
            "speaker_attribution",
            "semantic_link",
            "abstention",
            "source_span",
        ),
        records=(),
        thresholds=dict(DEFAULT_THRESHOLDS),
    )


def render_historical_manifest_json(
    manifest: HistoricalParliamentManifest | None = None,
) -> str:
    """Render the default or supplied manifest deterministically."""
    return json.dumps((manifest or default_historical_manifest()).to_dict(), indent=2) + "\n"


def render_historical_report_json(
    report: HistoricalParliamentReport | None = None,
) -> str:
    """Render the default or supplied fail-closed report deterministically."""
    resolved = report or evaluate_historical_manifest(default_historical_manifest())
    return json.dumps(resolved.to_dict(), indent=2) + "\n"


__all__ = [
    "DEFAULT_THRESHOLDS",
    "HistoricalParliamentManifest",
    "HistoricalParliamentRecord",
    "HistoricalParliamentReport",
    "default_historical_manifest",
    "evaluate_historical_manifest",
    "render_historical_manifest_json",
    "render_historical_report_json",
    "validate_historical_manifest",
]
