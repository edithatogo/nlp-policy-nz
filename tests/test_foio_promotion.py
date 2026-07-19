"""Tests for the FOI-O empirical promotion evidence boundary."""

from __future__ import annotations

from pathlib import Path

from nlp_policy_nz.extraction.foio_promotion import (
    FoioEvidenceSnapshot,
    FoioPromotionLane,
    FoioPromotionStatus,
    build_foio_promotion_evidence_report,
    load_foio_promotion_evidence_manifest,
    render_foio_promotion_evidence_json,
    render_foio_promotion_evidence_markdown,
)

ROOT = Path(__file__).resolve().parents[1]


def _snapshot() -> FoioEvidenceSnapshot:
    return FoioEvidenceSnapshot(
        archive_repository="owner/archive",
        archive_revision="0123456789abcdef0123456789abcdef01234567",
        archive_content_sha256="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        legal_source_revision="89abcdef0123456789abcdef0123456789abcdef",
        ontology_version="foi-o@2.0.0",
        model_revision="model-sha256:0123456789abcdef",
        pipeline_version="nlp-policy-nz@0.1.0",
        rights_evidence_uri="https://example.test/rights/record",
        rights_snapshot_sha256="abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
    )


def test_promotion_is_blocked_by_placeholder_identities_and_missing_review() -> None:
    lane = FoioPromotionLane(
        jurisdiction="NZ",
        snapshot=_snapshot().model_copy(update={"archive_revision": "a" * 40}),
        held_out_record_ids=("held-out-1",),
        rights_cleared=True,
        evaluation_report={"metrics": []},
    )

    report = build_foio_promotion_evidence_report((lane,))

    assert not report.promotion_ready
    assert report.lanes[0].status is FoioPromotionStatus.BLOCKED
    assert any("archive_revision is a placeholder" in blocker for blocker in report.lanes[0].blockers)
    assert "reviewer identities are missing" in report.lanes[0].blockers


def test_promotion_requires_disjoint_held_out_split() -> None:
    lane = FoioPromotionLane(
        jurisdiction="Cth",
        snapshot=_snapshot(),
        held_out_record_ids=("record-1",),
        training_record_ids=("record-1",),
        rights_cleared=True,
        reviewer_ids=("reviewer-1",),
        adjudication_complete=True,
        evaluation_report={"metrics": []},
    )

    report = build_foio_promotion_evidence_report((lane,))

    assert "held-out and training record identifiers overlap" in report.lanes[0].blockers


def test_manifest_is_explicitly_blocked_without_invented_evidence() -> None:
    report = load_foio_promotion_evidence_manifest(ROOT / "data/foio/promotion_evidence_manifest.json")

    assert not report.promotion_ready
    assert [lane.jurisdiction for lane in report.lanes] == ["Cth", "NSW", "NZ"]
    assert all(lane.status is FoioPromotionStatus.BLOCKED for lane in report.lanes)
    assert all(not lane.held_out_record_ids for lane in report.lanes)
    assert render_foio_promotion_evidence_json(report).endswith("\n")
    assert "Promotion ready: `false`" in render_foio_promotion_evidence_markdown(report)
