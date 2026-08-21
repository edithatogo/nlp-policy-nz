"""Tests for the NZ Legislative XML Parser."""

import pytest
import spacy

from nlp_policy_nz.xml_parser import (
    SAMPLE_NZ_XML,
    LegislativeXMLParser,
    run_demo,
)


def test_legislative_xml_parser_basic():
    """Test that the parser can be instantiated and extracts text and metadata."""
    parser = LegislativeXMLParser(SAMPLE_NZ_XML)
    clean_text, metadata = parser.parse()

    assert isinstance(clean_text, str)
    assert len(clean_text) > 0

    assert isinstance(metadata, list)
    assert len(metadata) > 0

    # Check that metadata elements contain expected values
    act_meta = next(m for m in metadata if m.element_type == "act")
    assert act_meta.element_id == "2026-001"
    assert act_meta.element_title == "Legislative Test Act 2026"


def test_run_demo_executes_successfully():
    """Test that the built-in demo function runs without errors."""
    try:
        run_demo()
    except Exception as e:
        pytest.fail(f"run_demo() raised {type(e).__name__} unexpectedly: {e}")


def test_spacy_components():
    """Test that the custom spacy components successfully load and process a document."""
    parser = LegislativeXMLParser(SAMPLE_NZ_XML)
    clean_text, metadata = parser.parse()

    nlp = spacy.blank("en")
    nlp.add_pipe("nz_xml_structure_injector", first=True)
    nlp.add_pipe("nz_cross_reference_matcher", after="nz_xml_structure_injector")

    doc = nlp.make_doc(clean_text)
    doc._.nz_xml_metadata = metadata

    doc = nlp(doc)

    assert "nz_xml_structure" in doc.spans
    assert "nz_cross_references" in doc.spans
    assert len(doc.spans["nz_xml_structure"]) > 0
