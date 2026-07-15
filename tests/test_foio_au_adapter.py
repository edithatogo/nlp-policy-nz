"""Tests for the profile-isolated Australian FOI-O adapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from nlp_policy_nz.extraction import (
    AustralianJurisdiction,
    ExtractedSpan,
    ExtractionFamily,
    ExtractionRecord,
    SourceTrace,
)
from nlp_policy_nz.extraction.foio_au_adapter import (
    FoioAustralianArchiveBundle,
    FoioAustralianProfileSnapshot,
    build_australian_archive_bundle,
    evaluate_australian_candidates,
    evaluate_australian_fixture,
    load_australian_evaluation_fixture,
    render_australian_archive_bundle_json,
    render_australian_evaluation_json,
    route_australian_jurisdiction,
)


def _record(
    record_id: str,
    *,
    jurisdiction: str | None,
    label: str = "obligation",
    citation_path: str = "australia/foi/example",
) -> ExtractionRecord:
    attributes = {"review": "candidate"}
    if jurisdiction is not None:
        attributes["jurisdiction"] = jurisdiction
    return ExtractionRecord(
        record_id=record_id,
        family=ExtractionFamily.OBLIGATION,
        label=label,
        value="must disclose",
        confidence=0.9,
        attributes=attributes,
        source_trace=SourceTrace(
            citation_path=citation_path,
            source_sha256="b" * 64,
            source_url="https://example.test/foi",
            retrieved_at="2026-07-15T00:00:00Z",
            spans=(ExtractedSpan(start=0, end=4, text="must"),),
        ),
    )


def _snapshot(jurisdiction: AustralianJurisdiction) -> FoioAustralianProfileSnapshot:
    return FoioAustralianProfileSnapshot(
        jurisdiction=jurisdiction,
        profile_id=f"foi-o-au-{jurisdiction.value.lower()}@1.0.0",
        archive_repository="edithatogo/fyi-archive-nz",
        archive_revision="a" * 40,
        archive_content_sha256="b" * 64,
        legal_source_revision="c" * 40,
        legal_source_url="https://www.legislation.gov.au/",
        ontology_version="foi-o@2.0.0",
        model_revision="model@2026-07-15",
        schema_version="2.0.0",
        extraction_contract_version="2.0.0",
        pipeline_version="nlp-policy-nz@0.1.0",
        retrieved_at="2026-07-15T00:00:00Z",
    )


def test_router_is_explicit_and_abstains_when_ambiguous_or_unsupported() -> None:
    assert route_australian_jurisdiction(_record("cth", jurisdiction="Cth")).jurisdiction == (
        AustralianJurisdiction.COMMONWEALTH
    )
    assert route_australian_jurisdiction(_record("nsw", jurisdiction="NSW")).jurisdiction == (
        AustralianJurisdiction.NSW
    )
    ambiguous = _record(
        "ambiguous",
        jurisdiction=None,
        citation_path="commonwealth/nsw/foi/example",
    )
    assert route_australian_jurisdiction(ambiguous).status == "abstained"
    assert route_australian_jurisdiction(_record("nz", jurisdiction=None, citation_path="nz/foi")).status == (
        "abstained"
    )


def test_bundle_rejects_cross_profile_contamination_and_is_candidate_only() -> None:
    bundle = build_australian_archive_bundle(
        [_record("cth", jurisdiction="Cth")],
        _snapshot(AustralianJurisdiction.COMMONWEALTH),
    )
    assert bundle.review_status == "candidate"
    assert bundle.manifest.records[0].attributes["foio_au_jurisdiction"] == "Cth"
    assert render_australian_archive_bundle_json(bundle).endswith("\n")
    with pytest.raises(ValueError, match="cross-profile contamination"):
        build_australian_archive_bundle(
            [_record("nsw", jurisdiction="NSW")],
            _snapshot(AustralianJurisdiction.COMMONWEALTH),
        )


def test_bundle_rejects_unroutable_and_digest_mismatch() -> None:
    with pytest.raises(ValueError, match="cannot be routed"):
        build_australian_archive_bundle(
            [_record("unknown", jurisdiction=None, citation_path="australia/unknown")],
            _snapshot(AustralianJurisdiction.COMMONWEALTH),
        )
    with pytest.raises(ValueError, match="source digest"):
        build_australian_archive_bundle(
            [_record("cth", jurisdiction="Cth").model_copy(
                update={"source_trace": _record("cth", jurisdiction="Cth").source_trace.model_copy(
                    update={"source_sha256": "d" * 64}
                )}
            )],
            _snapshot(AustralianJurisdiction.COMMONWEALTH),
        )


def test_per_jurisdiction_metrics_include_disagreement_and_abstention() -> None:
    reference = [
        _record("cth:1", jurisdiction="Cth"),
        _record("nsw:1", jurisdiction="NSW"),
    ]
    candidate = [
        _record("cth:1", jurisdiction="Cth"),
        _record("nsw:1", jurisdiction="NSW", label="permission"),
    ]
    report = evaluate_australian_candidates(
        reference,
        candidate,
        abstained_record_ids=("Cth:abstained-1", "NSW:abstained-1"),
    )
    nsw = next(item for item in report.jurisdictions if item.jurisdiction == AustralianJurisdiction.NSW)
    assert nsw.disagreement_count == 1
    assert nsw.abstention_count == 1
    assert render_australian_evaluation_json(report).endswith("\n")


def test_bounded_fixture_is_pinned_and_evaluable() -> None:
    fixture_path = Path("data/foio/australian_evaluation_fixture.json")
    fixture = load_australian_evaluation_fixture(fixture_path)
    report = evaluate_australian_fixture(fixture_path)
    assert {snapshot.jurisdiction for snapshot in fixture.snapshots} == {
        AustralianJurisdiction.COMMONWEALTH,
        AustralianJurisdiction.NSW,
    }
    assert len(report.jurisdictions) == 2
    assert all(item.reference_records == 1 for item in report.jurisdictions)


def test_bounded_bundle_artifact_is_schema_valid_and_candidate_only() -> None:
    bundle = FoioAustralianArchiveBundle.model_validate_json(
        Path("artifacts/foio/australian_cth_dry_run_bundle.json").read_text(encoding="utf-8")
    )
    assert bundle.review_status == "candidate"
    assert bundle.snapshot.jurisdiction == AustralianJurisdiction.COMMONWEALTH
