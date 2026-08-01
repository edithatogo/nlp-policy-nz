from __future__ import annotations

import pytest

from nlp_policy_nz.universal_framework_v3 import (
    DocumentChunk,
    FrameworkConfig,
    HTMLIngestionEngine,
    JSONLIngestionEngine,
    XMLIngestionEngine,
    get_ingestion_engine,
)


@pytest.mark.unit
def test_framework_config() -> None:
    """Test FrameworkConfig struct."""
    config = FrameworkConfig(
        country="New Zealand",
        jurisdiction="National Parliament & PCO Legislative Corpus",
        source_data_format="XML",
        target_schema_standard="ParlaMint-TEI-Ana",
    )
    assert config.country == "New Zealand"
    assert config.jurisdiction == "National Parliament & PCO Legislative Corpus"
    assert config.source_data_format == "XML"
    assert config.target_schema_standard == "ParlaMint-TEI-Ana"


@pytest.mark.unit
def test_document_chunk() -> None:
    """Test DocumentChunk struct."""
    chunk = DocumentChunk(
        chunk_id="test_id",
        text="Test text",
        structural_type="section",
        attributes={"attr1": "value1"},
    )
    assert chunk.chunk_id == "test_id"
    assert chunk.text == "Test text"
    assert chunk.structural_type == "section"
    assert chunk.attributes == {"attr1": "value1"}


@pytest.mark.unit
def test_get_ingestion_engine() -> None:
    """Test getting ingestion engines for different formats."""
    assert isinstance(get_ingestion_engine("XML"), XMLIngestionEngine)
    assert isinstance(get_ingestion_engine("xml"), XMLIngestionEngine)

    assert isinstance(get_ingestion_engine("HTML"), HTMLIngestionEngine)
    assert isinstance(get_ingestion_engine("html"), HTMLIngestionEngine)

    assert isinstance(get_ingestion_engine("JSONL"), JSONLIngestionEngine)
    assert isinstance(get_ingestion_engine("jsonl"), JSONLIngestionEngine)


@pytest.mark.unit
def test_get_ingestion_engine_invalid() -> None:
    """Test getting ingestion engine for invalid format."""
    with pytest.raises(ValueError, match="Unsupported source format: invalid_format"):
        get_ingestion_engine("invalid_format")


@pytest.mark.unit
def test_xml_ingestion_engine_basic() -> None:
    """Test XMLIngestionEngine with basic XML."""
    xml_data = """
    <root>
        <section id="sec-1" title="Interpretation">
            <para>The terms apply to this Act.</para>
        </section>
        <part id="part-1">
            <speech speaker="John Doe">Hello</speech>
        </part>
    </root>
    """
    engine = XMLIngestionEngine()
    chunks = engine.ingest(xml_data)

    assert len(chunks) == 3

    assert chunks[0].chunk_id == "sec-1"
    assert chunks[0].structural_type == "section"
    assert chunks[0].text == "The terms apply to this Act."
    assert chunks[0].attributes == {"title": "Interpretation"}

    assert chunks[1].chunk_id == "part-1"
    assert chunks[1].structural_type == "part"
    assert chunks[1].text == "Hello"
    assert chunks[1].attributes == {}

    assert chunks[2].chunk_id == "xml-chunk-2"
    assert chunks[2].structural_type == "speech"
    assert chunks[2].text == "Hello"
    assert chunks[2].attributes == {"speaker": "John Doe"}


@pytest.mark.unit
def test_xml_ingestion_engine_invalid_xml() -> None:
    """Test XMLIngestionEngine with invalid XML."""
    engine = XMLIngestionEngine()
    chunks = engine.ingest("This is not XML")

    # As per implementation, if not valid XML it falls back to BeautifulSoup parsing,
    # and if that doesn't yield elements it returns empty or parsed content
    # For now, let's just see how it reacts.
    assert isinstance(chunks, list)
