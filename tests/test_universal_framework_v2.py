"""Tests for universal_framework_v2."""

import json

from nlp_policy_nz.universal_framework_v2 import (
    SAMPLE_JSONL,
    SAMPLE_XML,
    DocumentChunk,
    FrameworkConfig,
    MetaExtensionRegistry,
    run_demo,
    run_framework,
)


def test_framework_config_instantiation() -> None:
    """Test that FrameworkConfig can be instantiated correctly."""
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
    assert config.base_spacy_pipeline == "en_core_web_sm"


def test_document_chunk_instantiation() -> None:
    """Test that DocumentChunk can be instantiated correctly."""
    chunk = DocumentChunk(
        chunk_id="test-id",
        structural_type="paragraph",
        text="This is a test.",
    )
    assert chunk.chunk_id == "test-id"
    assert chunk.structural_type == "paragraph"
    assert chunk.text == "This is a test."


def test_meta_extension_registry_sanitize_name() -> None:
    """Test sanitize_name utility function."""
    assert (
        MetaExtensionRegistry.sanitize_name("New Zealand_ParlaMint-TEI-Ana")
        == "new_zealand_parlamint_tei_ana"
    )
    assert (
        MetaExtensionRegistry.sanitize_name("United Kingdom_ParlaCAP-JSONL")
        == "united_kingdom_parlacap_jsonl"
    )


def test_run_framework_xml() -> None:
    """Test run_framework with XML input."""
    config = FrameworkConfig(
        country="New Zealand",
        jurisdiction="National Parliament & PCO Legislative Corpus",
        source_data_format="XML",
        target_schema_standard="ParlaMint-TEI-Ana",
    )
    result = run_framework(config, SAMPLE_XML)

    assert 'xml:id="sec-5"' in result
    assert 'who="#unknown_speaker"' in result
    assert 'ana="#section"' in result
    assert "The" in result
    assert "terms" in result
    assert "apply" in result
    assert "to" in result
    assert "this" in result
    assert "Act" in result


def test_run_framework_jsonl() -> None:
    """Test run_framework with JSONL input."""
    config = FrameworkConfig(
        country="United Kingdom",
        jurisdiction="UK Hansard Parliamentary Debates",
        source_data_format="JSONL",
        target_schema_standard="ParlaCAP-JSONL",
    )
    result = run_framework(config, SAMPLE_JSONL)

    data = json.loads(result)
    assert data["id"] == "speech-102"
    assert data["country"] == "United Kingdom"
    assert data["structural_type"] == "speech"

    tokens = [t["text"] for t in data["tokens"]]
    assert "I" in tokens
    assert "support" in tokens


def test_run_demo() -> None:
    """Test that the run_demo function executes without errors."""
    run_demo()
