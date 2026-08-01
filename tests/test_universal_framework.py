from __future__ import annotations

import pytest


def test_imports():
    """Verify that universal_framework can be imported without errors."""
    from nlp_policy_nz.universal_framework import (
        FrameworkConfig,
        HTMLIngestionEngine,
        JSONLIngestionEngine,
        XMLIngestionEngine,
        get_ingestion_engine,
        run_demo,
    )

    assert FrameworkConfig is not None
    assert HTMLIngestionEngine is not None
    assert JSONLIngestionEngine is not None
    assert XMLIngestionEngine is not None
    assert get_ingestion_engine is not None
    assert run_demo is not None


def test_framework_config():
    """Test FrameworkConfig instantiation."""
    from nlp_policy_nz.universal_framework import FrameworkConfig

    config = FrameworkConfig(
        country="Test Country",
        jurisdiction="Test Jurisdiction",
        source_data_format="XML",
        target_schema_standard="Akoma-Ntoso",
    )
    assert config.country == "Test Country"
    assert config.base_spacy_pipeline == "en_core_web_sm"


def test_xml_ingestion_engine():
    """Test basic functionality of XMLIngestionEngine."""
    from nlp_policy_nz.universal_framework import XMLIngestionEngine

    engine = XMLIngestionEngine()
    sample_xml = '<section id="s1" title="Test Section"><para>Test content.</para></section>'
    chunks = engine.ingest(sample_xml)

    assert len(chunks) == 1
    assert chunks[0].chunk_id == "s1"
    assert chunks[0].structural_type == "section"
    assert chunks[0].text == "Test content."
    assert chunks[0].attributes.get("title") == "Test Section"


def test_html_ingestion_engine():
    """Test basic functionality of HTMLIngestionEngine."""
    from nlp_policy_nz.universal_framework import HTMLIngestionEngine

    engine = HTMLIngestionEngine()
    sample_html = '<article id="a1"><p>HTML content.</p></article>'
    chunks = engine.ingest(sample_html)

    assert len(chunks) == 1
    assert chunks[0].chunk_id == "a1"
    assert chunks[0].structural_type == "article"
    assert chunks[0].text == "HTML content."


def test_jsonl_ingestion_engine():
    """Test basic functionality of JSONLIngestionEngine."""
    from nlp_policy_nz.universal_framework import JSONLIngestionEngine

    engine = JSONLIngestionEngine()
    sample_jsonl = '{"id": "j1", "type": "paragraph", "text": "JSONL content", "metadata": {"author": "Tester"}}\n\n  \n{"id": "j2", "type": "speech", "text": "More content"}'
    chunks = engine.ingest(sample_jsonl)

    assert len(chunks) == 2
    assert chunks[0].chunk_id == "j1"
    assert chunks[0].structural_type == "paragraph"
    assert chunks[0].text == "JSONL content"
    assert chunks[0].attributes.get("author") == "Tester"

    assert chunks[1].chunk_id == "j2"
    assert chunks[1].structural_type == "speech"
    assert chunks[1].text == "More content"
    assert chunks[1].attributes == {}


def test_get_ingestion_engine():
    """Test the ingestion factory function."""
    from nlp_policy_nz.universal_framework import (
        HTMLIngestionEngine,
        JSONLIngestionEngine,
        XMLIngestionEngine,
        get_ingestion_engine,
    )

    assert isinstance(get_ingestion_engine("XML"), XMLIngestionEngine)
    assert isinstance(get_ingestion_engine("xml"), XMLIngestionEngine)
    assert isinstance(get_ingestion_engine("HTML"), HTMLIngestionEngine)
    assert isinstance(get_ingestion_engine("html"), HTMLIngestionEngine)
    assert isinstance(get_ingestion_engine("JSONL"), JSONLIngestionEngine)
    assert isinstance(get_ingestion_engine("jsonl"), JSONLIngestionEngine)

    with pytest.raises(ValueError, match="Unsupported source format: UNKNOWN"):
        get_ingestion_engine("UNKNOWN")
