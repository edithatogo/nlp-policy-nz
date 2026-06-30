from __future__ import annotations

from pathlib import Path

from nlp_policy_nz.extraction import (
    list_catalog_runs,
    report_catalog_source_staleness,
    write_manifest_to_catalog,
)
from nlp_policy_nz.extraction.exporter import extraction_manifest_from_pipeline_records
from nlp_policy_nz.storage import PipelineRecord


def _pipeline_record() -> PipelineRecord:
    return PipelineRecord(
        doc_id="example-10",
        corpus_source="legislation",
        raw_text="A person must apply before 1 July 2026.",
        cleaned_tokens=["A", "person", "must", "apply", "before", "1", "July", "2026"],
        nz_act_citations=["nz/statutes/example-act/2026/10"],
        te_reo_terms=[],
        deontic_modality=[{"label": "obligation", "text": "must apply"}],
        temporal_expressions=[{"type": "DATE", "text": "1 July 2026", "value": "2026-07-01"}],
        resolved_entities=[{"text": "person", "label": "LEGAL_PERSON", "qid": "Q215627"}],
        legal_effect="obligation",
    )


def test_catalog_records_manifest_run_and_summary(tmp_path: Path) -> None:
    manifest = extraction_manifest_from_pipeline_records(
        [_pipeline_record()],
        retrieved_at="2026-06-30T00:00:00Z",
    )
    db_path = tmp_path / "extractions.sqlite"

    run_id = write_manifest_to_catalog(db_path, manifest, run_id="fixture-run")
    runs = list_catalog_runs(db_path)

    assert run_id == "fixture-run"
    assert len(runs) == 1
    assert runs[0].run_id == "fixture-run"
    assert runs[0].producer == "nlp-policy-nz"
    assert runs[0].total_records == 6


def test_catalog_reports_current_stale_and_missing_sources(tmp_path: Path) -> None:
    record = _pipeline_record()
    manifest = extraction_manifest_from_pipeline_records(
        [record],
        retrieved_at="2026-06-30T00:00:00Z",
    )
    db_path = tmp_path / "extractions.sqlite"
    write_manifest_to_catalog(db_path, manifest, run_id="fixture-run")

    current = report_catalog_source_staleness(
        db_path,
        {"nz/statutes/example-act/2026/10": record.raw_text},
    )
    stale = report_catalog_source_staleness(
        db_path,
        {"nz/statutes/example-act/2026/10": f"{record.raw_text} Changed."},
    )
    missing = report_catalog_source_staleness(db_path, {})

    assert current[0].status == "current"
    assert current[0].record_count == 6
    assert stale[0].status == "stale"
    assert stale[0].current_sha256 != stale[0].pinned_sha256
    assert missing[0].status == "missing"
    assert missing[0].current_sha256 is None
