"""Track 74 held-out evaluation set contract tests."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from nlp_policy_nz.training.track74_evaluation import (
    default_track74_manifest,
    evaluate_track74_manifest,
    render_track74_manifest_json,
    render_track74_report_json,
    validate_track74_manifest,
)

ROOT = Path(__file__).resolve().parents[1]


def test_track74_manifest_and_report_are_leakage_free_and_stable() -> None:
    """The default manifest should validate and produce a stable baseline report."""
    manifest = default_track74_manifest()
    leakage_free, errors = validate_track74_manifest(manifest)
    report = evaluate_track74_manifest(manifest)

    assert leakage_free is True
    assert errors == ()
    assert report.leakage_free is True
    assert report.example_count == 4
    assert report.task_scores["classification"] == 1.0
    assert report.task_scores["retrieval"] == 1.0
    assert report.task_scores["stance"] == 0.0
    assert report.overall_score == 0.7143
    assert report.promotion_threshold == 0.75
    assert report.promotion_ready is False


def test_track74_manifest_rejects_training_overlap() -> None:
    """Any source hash overlap with the training pool must fail closed."""
    manifest = default_track74_manifest()
    overlapped_case = replace(
        manifest.held_out_cases[0],
        source_hash=manifest.training_pool[0].source_hash,
    )
    tampered = replace(manifest, held_out_cases=(overlapped_case, *manifest.held_out_cases[1:]))

    leakage_free, errors = validate_track74_manifest(tampered)

    assert leakage_free is False
    assert any("leakage detected" in error for error in errors)


def test_track74_committed_artifacts_match_rendered_outputs() -> None:
    """Committed manifest and report artifacts should match the render helpers."""
    manifest_path = ROOT / "data" / "track74" / "held_out_evaluation_set.json"
    report_path = ROOT / "data" / "track74" / "baseline_report.json"

    assert manifest_path.read_text(encoding="utf-8") == render_track74_manifest_json()
    assert report_path.read_text(encoding="utf-8") == render_track74_report_json()
