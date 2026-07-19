"""Track 132 leakage, evidence, and fail-closed promotion contracts."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from nlp_policy_nz.parliament.held_out import (
    HistoricalParliamentRecord,
    default_historical_manifest,
    evaluate_historical_manifest,
    render_historical_manifest_json,
    render_historical_report_json,
    validate_historical_manifest,
)

ROOT = Path(__file__).resolve().parents[1]


def _record(split: str = "test", **changes: object) -> HistoricalParliamentRecord:
    record = HistoricalParliamentRecord(
        record_id=f"{split}-1",
        source_id=f"volume-{split}",
        volume_id=f"volume-{split}",
        page_id="page-1",
        split=split,  # type: ignore[arg-type]
        source_sha256=f"hash-{split}",
        annotation_ref="annotation-1" if split == "test" else None,
        annotator_ids=("annotator-1",),
        adjudicator_ids=("adjudicator-1",),
        authority_evidence_ids=("authority-1",) if split == "test" else (),
        review_decision_ref="review-1" if split == "test" else None,
    )
    return replace(record, **changes)


def test_track132_scaffold_is_explicitly_no_promotion() -> None:
    manifest = default_historical_manifest()
    valid, errors = validate_historical_manifest(manifest)
    report = evaluate_historical_manifest(manifest)

    assert valid is True
    assert errors == ()
    assert report.promotion_ready is False
    assert report.decision == "no-promotion"
    assert "no held-out test records are present" in report.reasons


def test_track132_rejects_page_volume_and_hash_leakage() -> None:
    train = _record("train", record_id="train-1", source_id="shared", volume_id="shared")
    test = _record(
        record_id="test-1",
        source_id="shared",
        volume_id="shared",
        source_sha256="hash-train",
    )
    valid, errors = validate_historical_manifest(
        replace(default_historical_manifest(), records=(train, test))
    )

    assert valid is False
    assert any("hash leakage" in error for error in errors)
    assert any("volume leakage" in error for error in errors)
    assert any("source leakage" in error for error in errors)
    assert any("duplicate source page" in error for error in errors)


def test_track132_rejects_role_overlap_and_missing_evidence() -> None:
    record = _record(
        annotator_ids=("same-person",),
        adjudicator_ids=("same-person",),
        authority_evidence_ids=(),
        review_decision_ref=None,
        annotation_ref=None,
    )
    valid, errors = validate_historical_manifest(
        replace(default_historical_manifest(), records=(record,))
    )

    assert valid is False
    assert any("role overlap" in error for error in errors)
    assert any("missing held-out annotation" in error for error in errors)
    assert any("missing authority evidence" in error for error in errors)
    assert any("signed review" in error for error in errors)


def test_track132_promotes_only_with_complete_evidence_and_thresholds() -> None:
    manifest = replace(default_historical_manifest(), records=(_record(),))
    metrics = {
        "hierarchy_accuracy": 0.95,
        "speaker_accuracy": 0.95,
        "link_f1": 0.9,
        "abstention_recall": 0.95,
        "span_fidelity": 0.98,
    }
    report = evaluate_historical_manifest(manifest, metrics)

    assert report.promotion_ready is True
    assert report.decision == "promote"
    assert report.reasons == ()

    below_threshold = evaluate_historical_manifest(manifest, {**metrics, "speaker_accuracy": 0.1})
    assert below_threshold.promotion_ready is False
    assert "metric below threshold: speaker_accuracy" in below_threshold.reasons


def test_track132_committed_artifacts_match_rendered_outputs() -> None:
    manifest_path = ROOT / "data" / "track132" / "held_out_manifest.json"
    report_path = ROOT / "data" / "track132" / "promotion_report.json"

    assert manifest_path.read_text(encoding="utf-8") == render_historical_manifest_json()
    assert report_path.read_text(encoding="utf-8") == render_historical_report_json()
