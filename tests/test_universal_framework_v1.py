from __future__ import annotations

import json

import pytest
import spacy
from spacy.tokens import Doc, Span

from nlp_policy_nz.universal_framework_v1 import (
    FrameworkConfig,
    HTMLIngestionEngine,
    JSONLIngestionEngine,
    MetaExtensionRegistry,
    TargetSchemaEmitter,
    XMLIngestionEngine,
    get_ingestion_engine,
    run_framework,
)


def test_framework_config() -> None:
    """Test creating and validating a FrameworkConfig."""
    config = FrameworkConfig(
        country="New Zealand",
        jurisdiction="National Parliament",
        source_data_format="XML",
        target_schema_standard="ParlaMint-TEI-Ana",
    )
    assert config.country == "New Zealand"
    assert config.jurisdiction == "National Parliament"
    assert config.source_data_format == "XML"
    assert config.target_schema_standard == "ParlaMint-TEI-Ana"
    assert config.base_spacy_pipeline == "en_core_web_sm"


def test_xml_ingestion() -> None:
    """Test XMLIngestionEngine parsing."""
    raw_xml = '<section id="sec-1" title="Intro"><para>Hello world.</para></section>'
    engine = XMLIngestionEngine()
    chunks = engine.ingest(raw_xml)
    assert len(chunks) == 1
    assert chunks[0].chunk_id == "sec-1"
    assert chunks[0].structural_type == "section"
    assert chunks[0].text == "Hello world."
    assert chunks[0].attributes == {"title": "Intro"}


def test_html_ingestion() -> None:
    """Test HTMLIngestionEngine parsing."""
    raw_html = '<article id="art-1" class="speech"><p>First speech</p></article>'
    engine = HTMLIngestionEngine()
    chunks = engine.ingest(raw_html)
    assert len(chunks) == 1
    assert chunks[0].chunk_id == "art-1"
    assert chunks[0].structural_type == "article"
    assert chunks[0].text == "First speech"
    # HTMLIngestionEngine sets attributes to empty dict as per its implementation
    assert chunks[0].attributes == {}


def test_jsonl_ingestion() -> None:
    """Test JSONLIngestionEngine parsing."""
    raw_jsonl = '{"id": "doc-1", "text": "Line 1", "type": "paragraph", "metadata": {"author": "Alice"}}\n{"id": "doc-2", "text": "Line 2", "type": "speech"}'
    engine = JSONLIngestionEngine()
    chunks = engine.ingest(raw_jsonl)
    assert len(chunks) == 2
    assert chunks[0].chunk_id == "doc-1"
    assert chunks[0].text == "Line 1"
    assert chunks[0].structural_type == "paragraph"
    assert chunks[0].attributes == {"author": "Alice"}

    assert chunks[1].chunk_id == "doc-2"
    assert chunks[1].text == "Line 2"
    assert chunks[1].structural_type == "speech"
    assert chunks[1].attributes == {}


def test_get_ingestion_engine() -> None:
    """Test the factory method for ingestion engines."""
    assert isinstance(get_ingestion_engine("XML"), XMLIngestionEngine)
    assert isinstance(get_ingestion_engine("xml"), XMLIngestionEngine)
    assert isinstance(get_ingestion_engine("HTML"), HTMLIngestionEngine)
    assert isinstance(get_ingestion_engine("JSONL"), JSONLIngestionEngine)

    with pytest.raises(ValueError, match="Unsupported source format: CSV"):
        get_ingestion_engine("CSV")


def test_meta_extension_registry() -> None:
    """Test dynamic metadata registry for spaCy."""
    config = FrameworkConfig(
        country="TestLand",
        jurisdiction="Test",
        source_data_format="XML",
        target_schema_standard="Akoma-Ntoso",
    )
    country_key, schema_key, chunk_id_key = MetaExtensionRegistry.register(config)

    # Assert naming convention is followed
    assert country_key == "testland_akoma_ntoso_country"
    assert schema_key == "testland_akoma_ntoso_structural_type"
    assert chunk_id_key == "testland_akoma_ntoso_chunk_id"

    # Check that properties are registered
    assert Doc.has_extension(country_key)
    assert Span.has_extension(schema_key)
    assert Span.has_extension(chunk_id_key)


def test_target_schema_emitter_parlamint() -> None:
    """Test emitting in ParlaMint-TEI-Ana format."""
    config = FrameworkConfig(
        country="NZ",
        jurisdiction="Test",
        source_data_format="XML",
        target_schema_standard="ParlaMint-TEI-Ana",
    )
    country_key, schema_key, chunk_id_key = MetaExtensionRegistry.register(config)
    emitter = TargetSchemaEmitter(config, country_key, schema_key, chunk_id_key)

    nlp = spacy.blank("en")
    doc = nlp("Hello world.")

    # Mocking tokens for lemma_ and pos_ (Spacy blank model doesn't have these by default)
    # Actually, we can just use set to manually assign schema/chunk ID for emission
    full_span = doc[0 : len(doc)]
    full_span._.set(schema_key, "speech")
    full_span._.set(chunk_id_key, "sp-1")

    output = emitter.emit(doc)
    assert '<div type="speech" xml:id="sp-1">' in output
    assert '<w lemma="" pos="">Hello</w>' in output
    assert '<w lemma="" pos="">world</w>' in output
    assert '<w lemma="" pos="">.</w>' in output
    assert "</div>" in output


def test_target_schema_emitter_akoma_ntoso() -> None:
    """Test emitting in Akoma-Ntoso format."""
    config = FrameworkConfig(
        country="NZ",
        jurisdiction="Test",
        source_data_format="XML",
        target_schema_standard="Akoma-Ntoso",
    )
    country_key, schema_key, chunk_id_key = MetaExtensionRegistry.register(config)
    emitter = TargetSchemaEmitter(config, country_key, schema_key, chunk_id_key)

    nlp = spacy.blank("en")
    doc = nlp("Hello world.")

    full_span = doc[0 : len(doc)]
    full_span._.set(schema_key, "section")
    full_span._.set(chunk_id_key, "sec-1")

    output = emitter.emit(doc)
    assert "<akomaNtoso>" in output
    assert '<section id="sec-1">' in output
    assert "<p>Hello world.</p>" in output
    assert "</section>" in output
    assert "</akomaNtoso>" in output


def test_target_schema_emitter_parlacap() -> None:
    """Test emitting in ParlaCAP-JSONL format."""
    config = FrameworkConfig(
        country="NZ",
        jurisdiction="Test",
        source_data_format="XML",
        target_schema_standard="ParlaCAP-JSONL",
    )
    country_key, schema_key, chunk_id_key = MetaExtensionRegistry.register(config)
    emitter = TargetSchemaEmitter(config, country_key, schema_key, chunk_id_key)

    nlp = spacy.blank("en")
    doc = nlp("Hello world")

    full_span = doc[0 : len(doc)]
    full_span._.set(schema_key, "paragraph")
    full_span._.set(chunk_id_key, "p-1")

    output = emitter.emit(doc)
    data = json.loads(output)

    assert data["id"] == "p-1"
    assert data["country"] == "NZ"
    assert data["structural_type"] == "paragraph"
    assert len(data["tokens"]) == 2
    assert data["tokens"][0]["text"] == "Hello"
    assert data["tokens"][1]["text"] == "world"


def test_target_schema_emitter_unknown() -> None:
    """Test emitting throws ValueError for unknown formats."""
    config = FrameworkConfig(
        country="NZ",
        jurisdiction="Test",
        source_data_format="XML",
        target_schema_standard="Unknown-Format",
    )
    country_key, schema_key, chunk_id_key = MetaExtensionRegistry.register(config)
    emitter = TargetSchemaEmitter(config, country_key, schema_key, chunk_id_key)

    nlp = spacy.blank("en")
    doc = nlp("Hello")

    with pytest.raises(ValueError, match="Unknown target schema: Unknown-Format"):
        emitter.emit(doc)


def test_run_framework_xml_parlamint() -> None:
    """Test running the full framework from XML to ParlaMint-TEI-Ana."""
    config = FrameworkConfig(
        country="New Zealand",
        jurisdiction="Parliament",
        source_data_format="XML",
        target_schema_standard="ParlaMint-TEI-Ana",
    )
    raw_data = '<section id="s1"><para>This is a test.</para></section>'

    output = run_framework(config, raw_data)

    assert '<div type="section" xml:id="s1">' in output
    assert '<w lemma="" pos="">This</w>' in output
    assert "</div>" in output


def test_run_framework_jsonl_parlacap() -> None:
    """Test running the full framework from JSONL to ParlaCAP-JSONL."""
    config = FrameworkConfig(
        country="United Kingdom",
        jurisdiction="Hansard",
        source_data_format="JSONL",
        target_schema_standard="ParlaCAP-JSONL",
    )
    raw_data = '{"id": "sp1", "text": "This is a speech.", "type": "speech"}'

    output = run_framework(config, raw_data)

    data = json.loads(output)
    assert data["id"] == "sp1"
    assert data["country"] == "United Kingdom"
    assert data["structural_type"] == "speech"
    assert len(data["tokens"]) == 5
    assert data["tokens"][0]["text"] == "This"
