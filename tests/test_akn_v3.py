"""Tests for Track 14 Akoma Ntoso v3 schema support."""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from nlp_policy_nz.schema.akn_v3 import (
    AKNDocument,
    AKNValidationError,
    AKNValidator,
    FRBRMetadata,
    emit_amendment,
    emit_bill,
    emit_debate,
    emit_judgment,
)
from nlp_policy_nz.universal_framework_v4 import FrameworkConfig, run_framework

AKN_NS = "http://docs.oasis-open.org/legaldocml/ns/akn/3.0"
AKN_TEST_SCHEMA = Path("tests/fixtures/akn/akn_v3_subset.xsd")


def _validator() -> AKNValidator:
    """Return the deterministic Track 14 test XSD validator."""
    return AKNValidator(schema_source=AKN_TEST_SCHEMA)


def _root(xml: str) -> ET.Element:
    return ET.fromstring(xml)


def test_bill_emitter_includes_full_frbr_hierarchy() -> None:
    """Bill XML includes Work, Expression, Manifestation, and Item metadata."""
    metadata = FRBRMetadata(
        country="nz",
        document_type="bill",
        identifier="bill-001",
        date="2026-06-21",
        author="nlp-policy-nz",
        language="eng",
        version="1",
    )

    xml = emit_bill(metadata, title="Climate Response Bill", body=["The Minister may act."])
    root = _root(xml)

    assert root.tag == f"{{{AKN_NS}}}akomaNtoso"
    assert root.find(f".//{{{AKN_NS}}}bill") is not None
    for tag in ("FRBRWork", "FRBRExpression", "FRBRManifestation", "FRBRItem"):
        assert root.find(f".//{{{AKN_NS}}}{tag}") is not None


def test_document_type_emitters_are_valid() -> None:
    """All required Track 14 document emitters pass local AKN validation."""
    metadata = FRBRMetadata(
        country="nz",
        document_type="bill",
        identifier="doc-001",
        date="2026-06-21",
    )
    docs = [
        emit_bill(metadata, "Bill title", ["Bill body"]),
        emit_amendment(metadata.with_type("amendment"), "Clause 5", ["Replace text"]),
        emit_judgment(metadata.with_type("judgment"), "Case title", ["Held for applicant"]),
        emit_debate(metadata.with_type("debate"), "Debate title", ["Member: Kia ora"]),
    ]

    validator = _validator()
    for xml in docs:
        result = validator.validate(xml)
        assert result.valid, result.errors


def test_metadata_blocks_include_tlc_event_analysis_and_references() -> None:
    """Generated documents include Track 14 metadata enrichments."""
    metadata = FRBRMetadata(country="nz", document_type="bill", identifier="meta-001")
    xml = emit_bill(
        metadata,
        title="Metadata Bill",
        body=["Section 5 applies."],
        references=[("legislation-act-2019", "/nz/act/2019/58")],
        events=[("introduction", "2026-06-21")],
        analysis=[("pipeline", "nlp-policy-nz")],
    )
    root = _root(xml)

    assert root.find(f".//{{{AKN_NS}}}TLCEvent") is not None
    assert root.find(f".//{{{AKN_NS}}}analysis") is not None
    assert root.find(f".//{{{AKN_NS}}}references") is not None
    assert root.find(f".//{{{AKN_NS}}}TLCReference") is not None


def test_validator_rejects_missing_frbr() -> None:
    """Validator reports structural AKN errors instead of silently passing."""
    validator = _validator()
    result = validator.validate(f'<akomaNtoso xmlns="{AKN_NS}"><bill /></akomaNtoso>')

    assert not result.valid
    assert result.errors
    with pytest.raises(AKNValidationError):
        validator.validate_or_raise(f'<akomaNtoso xmlns="{AKN_NS}"><bill /></akomaNtoso>')


def test_xsd_validator_rejects_misplaced_required_elements() -> None:
    """Schema validation rejects element-presence shells with invalid structure."""
    xml = (
        f'<akomaNtoso xmlns="{AKN_NS}">'
        "<bill/>"
        "<FRBRWork/>"
        "<FRBRExpression/>"
        "<FRBRManifestation/>"
        "<FRBRItem/>"
        "<TLCEvent/>"
        "<analysis/>"
        "<references/>"
        "<body/>"
        "</akomaNtoso>"
    )

    result = _validator().validate(xml)

    assert not result.valid
    assert result.errors


def test_framework_v4_emits_valid_akoma_ntoso() -> None:
    """Universal framework v4 emits locally valid AKN for XML source chunks."""
    config = FrameworkConfig(
        country="nz",
        jurisdiction="New Zealand Parliament",
        source_data_format="XML",
        target_schema_standard="Akoma-Ntoso",
        document_type="bill",
        akn_schema_source=str(AKN_TEST_SCHEMA),
    )
    raw_xml = '<section id="sec-1" title="Purpose"><para>The Minister must report.</para></section>'

    document = run_framework(config, raw_xml)
    validator = _validator()

    assert isinstance(document, AKNDocument)
    assert document.document_type == "bill"
    assert validator.validate(document.xml).valid
    assert "<FRBRWork>" in document.xml


def test_examples_are_checked_into_repo() -> None:
    """Track 14 includes examples that can be used by CI validation."""
    examples_dir = Path("examples/akn")
    validator = _validator()

    for example in (examples_dir / "bill.xml", examples_dir / "debate.xml"):
        assert example.is_file()
        result = validator.validate(example.read_text(encoding="utf-8"))
        assert result.valid, result.errors
