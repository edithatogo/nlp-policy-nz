"""Tests for Axiom Foundation interoperability helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from nlp_policy_nz.axiom import (
    BILL_STATUSES,
    DOCUMENT_TYPES,
    BillAction,
    BillHansardLink,
    BillStatus,
    BillVersion,
    DocumentType,
    RuleSpecReference,
    SourceSection,
    SourceSectionMetadata,
    compare_source_staleness,
    make_rulespec_reference,
    normalise_bill_status,
    pipeline_record_rulespec_reference,
    source_section_to_pipeline_record,
    source_sha256,
    source_verification_metadata,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FIXTURE = ROOT / "tests" / "fixtures" / "axiom" / "nz_source_section.txt"


def test_axiom_public_type_aliases_are_importable() -> None:
    """Public Axiom helpers should expose aliases used by downstream typing."""
    document_type: DocumentType = "act"
    bill_status: BillStatus = "introduced"

    assert document_type == "act"
    assert bill_status == "introduced"
    assert "royal_assent" in BILL_STATUSES
    assert "hansard" in DOCUMENT_TYPES


def _contains_key(value: object, key: str) -> bool:
    """Return whether a nested JSON-like value contains *key*."""
    if isinstance(value, dict):
        return key in value or any(_contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, key) for item in value)
    return False


def test_source_section_metadata_checksum_and_pipeline_roundtrip() -> None:
    """Source-section artifacts carry provenance and convert to PipelineRecord."""
    text = SOURCE_FIXTURE.read_text(encoding="utf-8")

    section = SourceSection.from_text(
        text,
        citation_path="nz/statutes/example-act/2026/5",
        jurisdiction="NZ",
        document_type="act",
        source_url="https://legislation.govt.nz/example-act/section/5",
        retrieved_at="2026-06-29T00:00:00Z",
        title="Example Act 2026, section 5",
        rights="Crown copyright",
    )
    record = source_section_to_pipeline_record(section)

    assert section.metadata.checksum_sha256 == source_sha256(text)
    assert section.metadata.citation_path == "nz/statutes/example-act/2026/5"
    assert record.doc_id == "nz/statutes/example-act/2026/5"
    assert record.corpus_source == "act"
    assert "Māori" in record.te_reo_terms
    assert record.report_title == "Example Act 2026, section 5"


def test_source_section_rejects_unknown_document_type() -> None:
    """Runtime construction should enforce the source document vocabulary."""
    with pytest.raises(ValueError, match="document_type must be one of"):
        SourceSection.from_text(
            "A person must comply.",
            citation_path="nz/statutes/example-act/2026/5",
            jurisdiction="NZ",
            document_type="webpage",  # type: ignore[arg-type]
            source_url="https://legislation.govt.nz/example-act/section/5",
            retrieved_at="2026-06-29T00:00:00Z",
        )


def test_source_section_metadata_rejects_malformed_identity_fields() -> None:
    """Direct metadata construction should enforce provenance field contracts."""
    with pytest.raises(ValueError, match="checksum_sha256"):
        SourceSectionMetadata(
            citation_path="nz/statutes/example-act/2026/5",
            jurisdiction="NZ",
            document_type="act",
            source_url="https://legislation.govt.nz/example-act/section/5",
            retrieved_at="2026-06-29T00:00:00Z",
            checksum_sha256="ABC",
        )

    with pytest.raises(ValueError, match="source_url is required"):
        SourceSectionMetadata(
            citation_path="nz/statutes/example-act/2026/5",
            jurisdiction="NZ",
            document_type="act",
            source_url=" ",
            retrieved_at="2026-06-29T00:00:00Z",
            checksum_sha256="0" * 64,
        )


def test_source_staleness_reports_current_stale_and_missing() -> None:
    """Staleness checks are non-mutating comparisons over citation paths."""
    text = SOURCE_FIXTURE.read_text(encoding="utf-8")
    section = SourceSection.from_text(
        text,
        citation_path="nz/statutes/example-act/2026/5",
        jurisdiction="NZ",
        document_type="act",
        source_url="https://legislation.govt.nz/example-act/section/5",
        retrieved_at="2026-06-29T00:00:00Z",
    )

    current = compare_source_staleness(
        section.metadata,
        {"nz/statutes/example-act/2026/5": text},
    )
    stale = compare_source_staleness(
        section.metadata,
        {"nz/statutes/example-act/2026/5": text.replace("public", "central")},
    )
    missing = compare_source_staleness(section.metadata, {})

    assert current.status == "current"
    assert not current.is_stale
    assert stale.status == "stale"
    assert stale.is_stale
    assert missing.status == "missing"
    assert missing.current_sha256 is None
    assert stale.to_dict()["status"] == "stale"


def test_rulespec_reference_and_source_verification_metadata() -> None:
    """RuleSpec bridge exports durable IDs and source verification blocks."""
    section = SourceSection.from_text(
        "A person must comply with the notice.",
        citation_path="nz/statutes/example-act/2026/10",
        jurisdiction="NZ",
        document_type="act",
        source_url="https://legislation.govt.nz/example-act/section/10",
        retrieved_at="2026-06-29T00:00:00Z",
    )
    record = source_section_to_pipeline_record(section)
    record.legal_effect = "Obligation"

    reference = make_rulespec_reference("nz/statutes/example-act/2026/10", "Must comply")
    inferred = pipeline_record_rulespec_reference(record)
    metadata = source_verification_metadata(section.metadata, concept="must comply")

    assert reference.durable_id == "nz:statutes/example-act/2026/10#must_comply"
    assert inferred.durable_id == "nz:statutes/example-act/2026/10#obligation"
    assert metadata["module"]["source_verification"]["corpus_citation_path"] == (
        "nz/statutes/example-act/2026/10"
    )
    assert not _contains_key(metadata["module"], "source_url")
    assert metadata["provenance"]["source_sha256"] == (section.metadata.checksum_sha256)
    assert metadata["rulespec_reference"]["durable_id"].endswith("#must_comply")


def test_rulespec_reference_rejects_empty_normalized_fragments() -> None:
    """Durable RuleSpec IDs must not degrade to empty path or concept parts."""
    direct = RuleSpecReference("NZ:", "nz/Statutes/Example Act/2026/10", "Must comply")

    assert direct.durable_id == "nz:statutes/example-act/2026/10#must_comply"

    with pytest.raises(ValueError, match="citation path"):
        make_rulespec_reference("nz/!!!", "obligation")

    with pytest.raises(ValueError, match="concept"):
        make_rulespec_reference("nz/statutes/example-act/2026/10", "!!!")

    with pytest.raises(ValueError, match="jurisdiction"):
        RuleSpecReference(" ", "nz/statutes/example-act/2026/10", "obligation")

    with pytest.raises(ValueError, match="concept"):
        RuleSpecReference("nz", "nz/statutes/example-act/2026/10", "!!!")


def test_bill_status_and_hansard_linkage_scaffold() -> None:
    """Bill lifecycle records expose normalized statuses and link metadata."""
    action = BillAction.from_raw(
        bill_id="climate-adaptation-bill-2026",
        action_date="2026-06-29",
        raw_status="Bill read a second time",
        chamber="House",
        source_url="https://www.parliament.nz/example",
    )
    version = BillVersion(
        bill_id=action.bill_id,
        version_id="introduced",
        title="Climate Adaptation Bill",
        checksum_sha256="0" * 64,
    )
    link = BillHansardLink(
        hansard_doc_id="NZ-HANS-2026-06-29-SP-04",
        bill_id=action.bill_id,
        bill_title=version.title,
        debate_date="2026-06-29",
        target_provision="clause 5",
        confidence=0.84,
        evidence="The member debated clause 5 of the Climate Adaptation Bill.",
    )

    assert normalise_bill_status("reported back from select committee") == "select_committee"
    assert action.status == "second_reading"
    assert version.to_dict()["title"] == "Climate Adaptation Bill"
    assert link.to_dict()["target_provision"] == "clause 5"

    with pytest.raises(ValueError, match="confidence"):
        BillHansardLink(
            hansard_doc_id="NZ-HANS-2026-06-29-SP-04",
            bill_id=action.bill_id,
            bill_title=version.title,
            debate_date="2026-06-29",
            confidence=1.5,
        )


def test_bill_linkage_records_reject_malformed_identity_fields() -> None:
    """Direct bill linkage records should enforce identity and checksum pins."""
    with pytest.raises(ValueError, match="bill_id is required"):
        BillAction(
            bill_id=" ",
            action_date="2026-06-29",
            raw_status="introduced",
            status="introduced",
        )

    with pytest.raises(ValueError, match="status must be one of"):
        BillAction(
            bill_id="climate-adaptation-bill-2026",
            action_date="2026-06-29",
            raw_status="made up",
            status="made_up",  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="checksum_sha256"):
        BillVersion(
            bill_id="climate-adaptation-bill-2026",
            version_id="introduced",
            title="Climate Adaptation Bill",
            checksum_sha256="ABC",
        )

    with pytest.raises(ValueError, match="hansard_doc_id is required"):
        BillHansardLink(
            hansard_doc_id=" ",
            bill_id="climate-adaptation-bill-2026",
            bill_title="Climate Adaptation Bill",
            debate_date="2026-06-29",
        )
