"""Tests for Track 78 RuleSpec promotion contracts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nlp_policy_nz.axiom import SourceSection
from nlp_policy_nz.extraction.schemas import ExtractedSpan, SourceTrace
from nlp_policy_nz.ontology import build_rules_as_code_bridge
from nlp_policy_nz.rulespec_promotion import (
    PromotionState,
    RuleSpecFormula,
    RuleSpecOracleFixtureRef,
    RuleSpecReviewerEvidence,
    build_rulespec_promotion_handoff,
    render_rulespec_promotion_handoff_json,
    render_rulespec_promotion_handoff_yaml,
    validate_rulespec_promotion_handoff,
    write_rulespec_promotion_handoff,
)

ROOT = Path(__file__).resolve().parents[1]
TRACK78_FIXTURES = ROOT / "data" / "track78" / "promotion_handoff_fixtures.json"


def _source_section() -> SourceSection:
    return SourceSection.from_text(
        "A person must provide information.",
        citation_path="nz/statutes/example-act/2026/10",
        jurisdiction="NZ",
        document_type="act",
        source_url="https://legislation.govt.nz/example-act/section/10",
        retrieved_at="2026-07-05T00:00:00Z",
        title="Example Act 2026, section 10",
    )


def _source_trace(section: SourceSection) -> SourceTrace:
    return SourceTrace(
        citation_path=section.metadata.citation_path,
        source_sha256=section.metadata.checksum_sha256,
        source_url=section.metadata.source_url,
        retrieved_at=section.metadata.retrieved_at,
        spans=(
            ExtractedSpan(start=0, end=len(section.text), text=section.text),
        ),
    )


def _reviewed_formula(section: SourceSection) -> RuleSpecFormula:
    return RuleSpecFormula(
        formula_id="information_duty",
        status=PromotionState.REVIEWED,
        expression="person.must_provide_information_within_20_working_days",
        entity="Person",
        period="day",
        parameters=("deadline_days",),
        source_spans=(
            ExtractedSpan(start=0, end=len(section.text), text=section.text),
        ),
    )


def _reviewer_evidence() -> tuple[RuleSpecReviewerEvidence, ...]:
    return (
        RuleSpecReviewerEvidence(
            reviewer="legal-reviewer",
            reviewed_at="2026-07-05T00:00:00Z",
            evidence_uri="data/track78/reviews/policyengine_oracle_review.md",
            notes="Reviewed formula and oracle fixture coverage.",
        ),
    )


def test_track78_fixture_manifest_covers_the_expected_review_states() -> None:
    """The checked-in fixture bundle should cover each review-state branch."""
    manifest = json.loads(TRACK78_FIXTURES.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == "track78.rulespec-promotion.fixtures.v1"
    assert {example["review_state"] for example in manifest["examples"]} == {
        "promoted",
        "rejected",
        "deferred",
        "blocked",
    }


def test_rulespec_promotion_handoff_round_trips_json_and_yaml(tmp_path: Path) -> None:
    """Promoted handoffs should render deterministically to JSON and YAML."""
    section = _source_section()
    bridge = build_rules_as_code_bridge(section, concept="information duty")
    handoff = build_rulespec_promotion_handoff(
        bridge,
        source_trace=_source_trace(section),
        review_state=PromotionState.PROMOTED,
        formulas=(_reviewed_formula(section),),
        oracle_fixture_refs=(
            RuleSpecOracleFixtureRef(
                fixture_id="policyengine-oracle-001",
                path="data/track78/oracles/policyengine_oracle_001.json",
                description="PolicyEngine oracle fixture for section 10",
            ),
        ),
        reviewer_evidence=_reviewer_evidence(),
        review_notes="Reviewed and promotable.",
        entities=({"entity_id": "person", "label": "Person"},),
        periods=({"period_id": "working-day", "label": "working days"},),
        parameters={"deadline_days": 20},
    )

    json_rendered = render_rulespec_promotion_handoff_json(handoff)
    yaml_rendered = render_rulespec_promotion_handoff_yaml(handoff)
    json_path, yaml_path = write_rulespec_promotion_handoff(handoff, tmp_path / "handoff")

    assert handoff.rulespec_id == "nz:statutes/example-act/2026/10#information_duty"
    assert json.loads(json_rendered)["review_state"] == "promoted"
    assert "rulespec_reference:" in yaml_rendered
    assert json.loads(json_path.read_text(encoding="utf-8")) == json.loads(json_rendered)
    assert yaml_path.is_file()
    assert json_path.is_file()
    validate_rulespec_promotion_handoff(handoff)


def test_rulespec_promotion_handoff_fails_closed_on_missing_source_proof() -> None:
    """Promotion must fail when source spans are missing."""
    section = _source_section()
    bridge = build_rules_as_code_bridge(section, concept="information duty")
    empty_trace = SourceTrace(
        citation_path=section.metadata.citation_path,
        source_sha256=section.metadata.checksum_sha256,
        source_url=section.metadata.source_url,
        retrieved_at=section.metadata.retrieved_at,
        spans=(),
    )

    with pytest.raises(ValueError, match="source spans are required"):
        build_rulespec_promotion_handoff(
            bridge,
            source_trace=empty_trace,
            review_state=PromotionState.PROMOTED,
            formulas=(_reviewed_formula(section),),
            oracle_fixture_refs=(
                RuleSpecOracleFixtureRef(
                    fixture_id="policyengine-oracle-001",
                    path="data/track78/oracles/policyengine_oracle_001.json",
                ),
            ),
            reviewer_evidence=_reviewer_evidence(),
        )


def test_rulespec_promotion_handoff_fails_closed_on_missing_legal_review() -> None:
    """Reviewed handoffs must include reviewer evidence."""
    section = _source_section()
    bridge = build_rules_as_code_bridge(section, concept="information duty")

    with pytest.raises(ValueError, match="legal review evidence is required"):
        build_rulespec_promotion_handoff(
            bridge,
            source_trace=_source_trace(section),
            review_state=PromotionState.REVIEWED,
        )


def test_rulespec_promotion_handoff_fails_closed_on_missing_oracle_fixtures() -> None:
    """Promoted handoffs must include oracle fixtures."""
    section = _source_section()
    bridge = build_rules_as_code_bridge(section, concept="information duty")

    with pytest.raises(ValueError, match="oracle fixture references are required"):
        build_rulespec_promotion_handoff(
            bridge,
            source_trace=_source_trace(section),
            review_state=PromotionState.PROMOTED,
            formulas=(_reviewed_formula(section),),
            reviewer_evidence=_reviewer_evidence(),
        )


def test_rulespec_promotion_handoff_fails_closed_on_unreviewed_formula_status() -> None:
    """Promoted handoffs must only include reviewed formulas."""
    section = _source_section()
    bridge = build_rules_as_code_bridge(section, concept="information duty")
    pending_formula = RuleSpecFormula(
        formula_id="information_duty",
        status=PromotionState.CANDIDATE,
        expression="person.must_provide_information_within_20_working_days",
        entity="Person",
        period="day",
        parameters=("deadline_days",),
        source_spans=(
            ExtractedSpan(start=0, end=len(section.text), text=section.text),
        ),
    )

    with pytest.raises(ValueError, match="formula status must be reviewed before promotion"):
        build_rulespec_promotion_handoff(
            bridge,
            source_trace=_source_trace(section),
            review_state=PromotionState.PROMOTED,
            formulas=(pending_formula,),
            oracle_fixture_refs=(
                RuleSpecOracleFixtureRef(
                    fixture_id="policyengine-oracle-001",
                    path="data/track78/oracles/policyengine_oracle_001.json",
                ),
            ),
            reviewer_evidence=_reviewer_evidence(),
        )


@pytest.mark.parametrize("state", [PromotionState.REJECTED, PromotionState.DEFERRED, PromotionState.BLOCKED])
def test_rulespec_promotion_handoff_accepts_terminal_review_states(state: PromotionState) -> None:
    """Rejected, deferred, and blocked handoffs should serialize without promotion gates."""
    section = _source_section()
    bridge = build_rules_as_code_bridge(section, concept="information duty")
    kwargs: dict[str, str] = {}
    if state == PromotionState.REJECTED:
        kwargs["rejection_reason"] = "Source scope is not specific enough for promotion."
    elif state == PromotionState.DEFERRED:
        kwargs["defer_reason"] = "Oracle fixtures are not ready yet."
    else:
        kwargs["review_notes"] = "Blocked until policy sign-off is completed."

    handoff = build_rulespec_promotion_handoff(
        bridge,
        source_trace=_source_trace(section),
        review_state=state,
        reviewer_evidence=_reviewer_evidence(),
        **kwargs,
    )

    validate_rulespec_promotion_handoff(handoff)
    assert handoff.review_state == state
    assert handoff.to_dict()["review_state"] == state.value
