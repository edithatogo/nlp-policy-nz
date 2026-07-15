"""Contract tests for the FOI-O/fyi-archive adapter boundary."""

from __future__ import annotations

from pathlib import Path

import pytest

from nlp_policy_nz.extraction import (
    ExtractedSpan,
    ExtractionFamily,
    ExtractionRecord,
    SourceTrace,
)
from nlp_policy_nz.extraction.foio_adapter import (
    FoioArchiveBundle,
    FoioArchiveSnapshot,
    build_foio_archive_bundle,
    compare_foio_baseline,
    evaluate_foio_candidates,
    evaluate_foio_fixture,
    load_foio_evaluation_fixture,
    render_foio_archive_bundle_json,
    render_foio_evaluation_json,
)


def _record(
    record_id: str,
    *,
    family: ExtractionFamily = ExtractionFamily.OBLIGATION,
    label: str = "obligation",
    start: int = 0,
) -> ExtractionRecord:
    return ExtractionRecord(
        record_id=record_id,
        family=family,
        label=label,
        value="must disclose",
        source_trace=SourceTrace(
            citation_path="nz/foi/example/1",
            source_sha256="a" * 64,
            source_url="hf://datasets/edithatogo/fyi-archive-nz/records/1",
            retrieved_at="2026-07-15T00:00:00Z",
            spans=(ExtractedSpan(start=start, end=start + 5, text="must"),),
        ),
    )


def _snapshot() -> FoioArchiveSnapshot:
    return FoioArchiveSnapshot(
        archive_repository="edithatogo/fyi-archive-nz",
        archive_revision="a" * 40,
        archive_record_id="record-1",
        archive_content_sha256="a" * 64,
        ontology_version="foi-o@2.0.0",
        schema_version="2.0.0",
        extraction_contract_version="2.0.0",
        pipeline_version="nlp-policy-nz@0.1.0",
    )


def test_bundle_is_candidate_only_and_deterministic() -> None:
    bundle = build_foio_archive_bundle([_record("b"), _record("a")], _snapshot())

    assert bundle.review_status == "candidate"
    assert tuple(record.record_id for record in bundle.manifest.records) == ("a", "b")
    assert render_foio_archive_bundle_json(bundle) == render_foio_archive_bundle_json(bundle)
    assert bundle.manifest.records[0].attributes["foio_provenance"]["ontology_version"] == (
        "foi-o@2.0.0"
    )


def test_bundle_rejects_source_digest_mismatch() -> None:
    with pytest.raises(ValueError, match="source digest"):
        build_foio_archive_bundle(
            [
                _record("a", start=2).model_copy(
                    update={
                        "source_trace": _record("a", start=2).source_trace.model_copy(
                            update={"source_sha256": "b" * 64}
                        )
                    }
                )
            ],
            _snapshot(),
        )


def test_baseline_delta_reports_relabel_and_shift() -> None:
    delta = compare_foio_baseline([_record("a")], [_record("a", label="permission", start=2)])

    assert delta == {
        "added": (),
        "removed": (),
        "relabelled": ("a",),
        "shifted": ("a",),
    }


def test_evaluation_reports_family_metrics_calibration_and_coverage() -> None:
    reference = [_record("a"), _record("b", family=ExtractionFamily.PERMISSION, label="permission")]
    candidate = [_record("a"), _record("b", label="obligation")]

    report = evaluate_foio_candidates(reference, candidate)

    obligation = next(metric for metric in report.metrics if metric.family.value == "obligation")
    assert obligation.true_positives == 1
    assert obligation.false_positives == 1
    assert obligation.false_negatives == 0
    assert obligation.precision == 0.5
    assert obligation.recall == 1.0
    assert obligation.f1 == pytest.approx(2 / 3)
    assert obligation.coverage == 1.0
    assert report.model_dump(mode="json") == report.model_copy().model_dump(mode="json")
    assert render_foio_evaluation_json(report).endswith("\n")


def test_bounded_fixture_is_pinned_and_evaluable() -> None:
    fixture_path = Path("data/foio/bounded_evaluation_fixture.json")
    fixture = load_foio_evaluation_fixture(fixture_path)
    report = evaluate_foio_fixture(fixture_path)

    assert fixture.snapshot.archive_revision == "a" * 40
    assert report.reference_records == 2
    assert report.candidate_records == 2
    assert all(metric.coverage == 1.0 for metric in report.metrics)


def test_dry_run_bundle_is_schema_valid_and_candidate_only() -> None:
    bundle = FoioArchiveBundle.model_validate_json(
        Path("artifacts/foio/dry_run_derived_bundle.json").read_text(encoding="utf-8")
    )

    assert bundle.review_status == "candidate"
    assert bundle.manifest.summary.total_records == 2
    assert all("foio_provenance" in record.attributes for record in bundle.manifest.records)
