"""End-to-end tests for a small local legislation processing path."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import spacy

from nlp_policy_nz.guard import create_maori_guard_component, normalize_text
from nlp_policy_nz.storage import PipelineRecord, load_from_parquet, serialize_to_parquet
from nlp_policy_nz.syntactic import chunk_legislation_document


def test_local_text_to_parquet_e2e_path() -> None:
    """A small text sample can be normalised, chunked, stored, and loaded."""
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    create_maori_guard_component(nlp)
    text = normalize_text("Maaori Act 2024 applies. The Minister must consult iwi.")
    chunks = chunk_legislation_document(text, nlp, year=2024, number=1)
    records = [
        PipelineRecord(
            doc_id=chunk["doc_id"],
            corpus_source="legislation",
            raw_text=chunk["text"],
            cleaned_tokens=chunk["text"].split(),
            nz_act_citations=[],
            te_reo_terms=["Māori"] if "Māori" in chunk["text"] else ["iwi"],
        )
        for chunk in chunks
    ]
    output_dir = Path(".tmp") / "track23-e2e" / uuid4().hex
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "records.parquet"

    serialize_to_parquet(records, output)
    loaded = load_from_parquet(output)

    assert [record.doc_id for record in loaded] == [
        "NZ-ACT-2024-001-SEC-0",
        "NZ-ACT-2024-001-SEC-1",
    ]
    assert loaded[0].raw_text == "Māori Act 2024 applies."
