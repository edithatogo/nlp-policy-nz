"""Tests for Track 53 model selection evidence."""

from __future__ import annotations

from nlp_policy_nz.training.track53_evidence import (
    Track53ModelSelectionReport,
    evaluate_track53_selection,
    render_track53_selection_markdown,
    track53_selection_contract,
)


def test_track53_repo_side_contracts_fail_closed_when_selection_is_incomplete() -> None:
    """Partial scaffolding must not satisfy the Track 53 selection gates."""
    report = Track53ModelSelectionReport(
        task_matrix_defined=True,
        datasets_recorded=True,
        manifest_created=False,
        encoder_baseline_evaluated=False,
        silver_adjudicator_evaluated=False,
        retrieval_candidates_evaluated=False,
        tradeoffs_recorded=False,
        recommendation_written=False,
        follow_up_recorded=False,
        review_ready=False,
    )

    status = evaluate_track53_selection(report)

    assert not status["baseline_contract"]
    assert not status["candidate_contract"]
    assert not status["handoff_contract"]
    assert not status["repo_side_contracts"]


def test_track53_selection_contract_is_json_ready_and_explicit() -> None:
    """A full repo-side selection pass should render a JSON-ready contract."""
    report = Track53ModelSelectionReport(
        task_matrix_defined=True,
        datasets_recorded=True,
        manifest_created=True,
        encoder_baseline_evaluated=True,
        silver_adjudicator_evaluated=True,
        retrieval_candidates_evaluated=True,
        tradeoffs_recorded=True,
        recommendation_written=True,
        follow_up_recorded=True,
        review_ready=True,
    )

    contract = track53_selection_contract(report)

    assert contract["baseline_contract"]["satisfied"] is True
    assert contract["candidate_contract"]["satisfied"] is True
    assert contract["handoff_contract"]["satisfied"] is True
    assert contract["repo_side_contracts"]["satisfied"] is True


def test_track53_evidence_markdown_lists_model_roles() -> None:
    """Rendered evidence should name the candidate role groups explicitly."""
    report = Track53ModelSelectionReport(
        task_matrix_defined=True,
        datasets_recorded=True,
        manifest_created=True,
        encoder_baseline_evaluated=False,
        silver_adjudicator_evaluated=False,
        retrieval_candidates_evaluated=False,
        tradeoffs_recorded=False,
        recommendation_written=False,
        follow_up_recorded=False,
        review_ready=False,
    )

    markdown = render_track53_selection_markdown(report)

    assert "Track 53 Evidence" in markdown
    assert "isaacus/emubert" in markdown
    assert "Equall/Saul-7B-Instruct-v1" in markdown
    assert "Kanon 2 Reranker" in markdown
