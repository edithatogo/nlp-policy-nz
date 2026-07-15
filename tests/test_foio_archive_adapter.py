"""Contract tests for the FOI-O/fyi-archive adapter boundary."""

from __future__ import annotations

import pytest

from nlp_policy_nz.extraction import (
    ExtractedSpan,
    ExtractionFamily,
    ExtractionRecord,
    SourceTrace,
)
from nlp_policy_nz.extraction.foio_adapter import (
    FoioArchiveSnapshot,
    build_foio_archive_bundle,
    compare_foio_baseline,
    render_foio_archive_bundle_json,
)


def _record(record_id: str, *, label: str = "obligation", start: int = 0) -> ExtractionRecord:
    return ExtractionRecord(
        record_id=record_id,
        family=ExtractionFamily.OBLIGATION,
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
