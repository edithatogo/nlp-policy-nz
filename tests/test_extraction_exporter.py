from __future__ import annotations

import json
from typing import TYPE_CHECKING

from nlp_policy_nz.cli.main import main
from nlp_policy_nz.extraction import (
    ExtractionFamily,
    extraction_manifest_from_pipeline_records,
)
from nlp_policy_nz.storage import PipelineRecord, serialize_to_parquet

if TYPE_CHECKING:
    from pathlib import Path


def _pipeline_record() -> PipelineRecord:
    return PipelineRecord(
        doc_id="example-10",
        corpus_source="legislation",
        raw_text="A person must apply before 1 July 2026.",
        cleaned_tokens=["A", "person", "must", "apply", "before", "1", "July", "2026"],
        nz_act_citations=["nz/statutes/example-act/2026/10"],
        te_reo_terms=[],
        deontic_modality=[
            {
                "label": "obligation",
                "text": "must apply",
                "start": 9,
                "end": 19,
            }
        ],
        temporal_expressions=[
            {
                "type": "DATE",
                "text": "1 July 2026",
                "value": "2026-07-01",
            }
        ],
        resolved_entities=[
            {
                "text": "person",
                "label": "LEGAL_PERSON",
                "qid": "Q215627",
            }
        ],
        legal_effect="obligation",
    )


def test_pipeline_records_export_broad_extraction_manifest() -> None:
    manifest = extraction_manifest_from_pipeline_records(
        [_pipeline_record()],
        retrieved_at="2026-06-30T00:00:00Z",
        source_url_base="https://example.test/source",
    )

    families = {record.family for record in manifest.records}

    assert manifest.summary.total_records == 6
    assert ExtractionFamily.OBLIGATION in families
    assert ExtractionFamily.DATE in families
    assert ExtractionFamily.ENTITY in families
    assert ExtractionFamily.CROSS_REFERENCE in families
    assert ExtractionFamily.RULES_AS_CODE in families
    assert manifest.trace_reports[0].citation_path == "nz/statutes/example-act/2026/10"
    assert manifest.trace_reports[0].source_sha256 == manifest.records[0].source_trace.source_sha256


def test_export_extractions_cli_writes_manifest(tmp_path: Path) -> None:
    parquet = tmp_path / "records.parquet"
    output = tmp_path / "extractions.json"
    serialize_to_parquet([_pipeline_record()], parquet)

    rc = main(
        [
            "export-extractions",
            "--parquet",
            str(parquet),
            "--output",
            str(output),
            "--retrieved-at",
            "2026-06-30T00:00:00Z",
            "--source-url-base",
            "https://example.test/source",
        ]
    )

    payload = json.loads(output.read_text(encoding="utf-8"))

    assert rc == 0
    assert payload["producer"] == "nlp-policy-nz"
    assert payload["summary"]["total_records"] == 6
    assert payload["trace_reports"][0]["record_ids"]
