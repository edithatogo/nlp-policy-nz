"""Tests for Track 63 nlprule-style grammar matching evaluation."""

from __future__ import annotations

from nlp_policy_nz.extraction.schemas import ExtractionFamily
from nlp_policy_nz.quality import (
    default_track63_rules,
    detect_track63_matches,
    evaluate_track63_acceptance,
    render_track63_evidence_markdown,
    run_track63_evaluation,
    track63_match_to_extraction_record,
    track63_match_to_quality_issue,
)


def test_default_track63_rules_cover_grammar_and_maori_tokens() -> None:
    """The default rule set includes the expected evaluation cues."""
    rule_ids = {rule.rule_id for rule in default_track63_rules()}
    assert {
        "obligation_modal",
        "prohibition_modal",
        "deadline_window",
        "legal_section_reference",
        "maori_māori",
        "maori_tikanga",
        "maori_kāwanatanga",
    } <= rule_ids


def test_detect_track63_matches_preserve_maori_tokens_and_alignment() -> None:
    """Matches should preserve Maori tokens and keep token-boundary alignment."""
    text = (
        "The committee must publish the report within 20 working days and keep "
        "tikanga and Māori intact under section 5."
    )
    matches = detect_track63_matches(text)
    rule_ids = {match.rule_id for match in matches}
    assert "obligation_modal" in rule_ids
    assert "deadline_window" in rule_ids
    assert "legal_section_reference" in rule_ids
    assert "maori_māori" in rule_ids
    assert "maori_tikanga" in rule_ids
    assert all(match.start < match.end for match in matches)


def test_track63_matches_map_to_existing_schemas() -> None:
    """Rule output should map into the repo's extraction and quality schemas."""
    text = "The regulator shall keep kāwanatanga intact under section 5."
    match = detect_track63_matches(text)[0]
    record = track63_match_to_extraction_record(
        match,
        source_text=text,
        citation_path="Hansard 2026-07-03 p 9",
    )
    issue = track63_match_to_quality_issue(match)
    assert record.family in {
        ExtractionFamily.OBLIGATION,
        ExtractionFamily.PROHIBITION,
        ExtractionFamily.DATE,
        ExtractionFamily.CROSS_REFERENCE,
        ExtractionFamily.ENTITY,
    }
    assert record.source_trace.spans[0].text == match.text
    assert issue.code.startswith("track63_")
    assert issue.severity == "info"


def test_track63_evidence_contract_is_satisfied() -> None:
    """The deterministic evaluation should satisfy the repo-side contract."""
    result = run_track63_evaluation()
    report = result.report
    status = evaluate_track63_acceptance(report)
    assert status["repo_side_contracts"] is True
    assert status["library_viability"] is True
    assert status["comparison_contract"] is True
    assert status["maori_token_preservation"] is True
    assert status["legal_span_alignment"] is True
    assert status["schema_mapping"] is True
    assert status["decision_contract"] is True
    assert render_track63_evidence_markdown(result)

