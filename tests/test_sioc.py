"""Tests for the SIOC linked-data export module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from rdflib import Graph, URIRef
from rdflib.namespace import RDF

from nlp_policy_nz.linked_data.sioc import (
    SpeechPost,
    _metadata_value,
    _speech_from_record,
    export_hansard_sioc,
    generate_sioc_graph,
)
from nlp_policy_nz.storage import PipelineRecord

if TYPE_CHECKING:
    from pathlib import Path


def test_metadata_value() -> None:
    """Test metadata value fallback behavior."""
    metadata = {"exists": "value", "empty": ""}

    assert _metadata_value(metadata, "exists", "default") == "value"
    assert _metadata_value(metadata, "missing", "default") == "default"
    assert _metadata_value(metadata, "empty", "default") == "default"


def test_speech_from_record() -> None:
    """Test converting a pipeline record and metadata to a SpeechPost."""
    record = PipelineRecord(
        doc_id="han-123",
        corpus_source="hansard",
        raw_text="Test speech text.",
        cleaned_tokens=["Test", "speech"],
        nz_act_citations=[],
        te_reo_terms=[],
        bill_reference="Test Bill",
    )
    metadata = {
        "speaker_name": "John Doe",
        "speaker_identifier": "mp/john-doe",
        "created_at": "2024-01-01",
    }

    speech = _speech_from_record(record, metadata)

    assert speech.identifier == "han-123"
    assert speech.speaker_name == "John Doe"
    assert speech.speaker_identifier == "mp/john-doe"
    assert speech.content == "Test speech text."
    assert speech.debate_title == "Test Bill"
    assert speech.debate_id == "test-bill"
    assert speech.created_at == "2024-01-01"


def test_speech_from_record_defaults() -> None:
    """Test converting a pipeline record and empty metadata uses defaults."""
    record = PipelineRecord(
        doc_id="han-456",
        corpus_source="hansard",
        raw_text="Another speech.",
        cleaned_tokens=["Another"],
        nz_act_citations=[],
        te_reo_terms=[],
    )

    speech = _speech_from_record(record, {})

    assert speech.identifier == "han-456"
    assert speech.speaker_name == "Unknown Speaker"
    assert speech.speaker_identifier == "speaker/unknown-speaker"
    assert speech.debate_title == "Hansard Debate"
    assert speech.debate_id == "hansard-debate"
    assert speech.created_at is None


def test_export_hansard_sioc_no_hansard_records() -> None:
    """Test export_hansard_sioc raises ValueError when no hansard records exist."""
    records = [
        PipelineRecord(
            doc_id="leg-1",
            corpus_source="legislation",
            raw_text="Legislation text.",
            cleaned_tokens=[],
            nz_act_citations=[],
            te_reo_terms=[],
        )
    ]

    with pytest.raises(ValueError, match=r"No Hansard records available for SIOC export\."):
        export_hansard_sioc(records, "dummy.ttl")


def test_speechpost_dataclass() -> None:
    """Test SpeechPost instantiation."""
    speech = SpeechPost(
        identifier="speech-1",
        debate_id="debate-1",
        debate_title="Title",
        speaker_name="Name",
        speaker_identifier="mp/name",
        content="Content",
    )
    assert speech.identifier == "speech-1"
    assert speech.created_at is None


def test_generate_sioc_graph() -> None:
    """Test generating a SIOC graph with speeches."""
    speeches = [
        SpeechPost(
            identifier="speech-1",
            debate_id="debate-1",
            debate_title="Title",
            speaker_name="Name",
            speaker_identifier="mp/name",
            content="Content",
            created_at="2024-01-01",
        )
    ]
    graph = generate_sioc_graph(speeches)

    post = URIRef("https://data.parliament.nz/speech/speech-1")
    assert (post, RDF.type, URIRef("http://rdfs.org/sioc/ns#Post")) in graph


def test_export_hansard_sioc(tmp_path: Path) -> None:
    """Test successful export to SIOC."""
    records = [
        PipelineRecord(
            doc_id="han-123",
            corpus_source="hansard",
            raw_text="Speech text.",
            cleaned_tokens=["Speech"],
            nz_act_citations=[],
            te_reo_terms=[],
        )
    ]
    output_path = tmp_path / "output.ttl"

    result = export_hansard_sioc(records, output_path)

    assert result == output_path
    assert output_path.exists()

    parsed = Graph()
    parsed.parse(result, format="turtle")
    assert (
        URIRef("https://data.parliament.nz/speech/han-123"),
        RDF.type,
        URIRef("http://rdfs.org/sioc/ns#Post"),
    ) in parsed
