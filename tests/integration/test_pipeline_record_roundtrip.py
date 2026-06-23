"""Integration tests for PipelineRecord Parquet round-tripping."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from nlp_policy_nz.storage import PipelineRecord, load_from_parquet, serialize_to_parquet


def test_pipeline_record_roundtrip_preserves_track_fields() -> None:
    """PipelineRecord rows survive Parquet serialisation and deserialisation."""
    output_dir = Path(".tmp") / "track23-roundtrip" / uuid4().hex
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "records.parquet"
    source = PipelineRecord(
        doc_id="NZ-ACT-2024-001-SEC-1",
        corpus_source="legislation",
        raw_text="The Minister must consult Māori representatives.",
        cleaned_tokens=["The", "Minister", "must", "consult", "Māori", "representatives"],
        nz_act_citations=["section 1"],
        te_reo_terms=["Māori"],
        legal_effect="obligation",
    )

    serialize_to_parquet([source], path)
    loaded = load_from_parquet(path)

    assert loaded == [source]
