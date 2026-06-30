"""Tests for Track 53 model selection evidence."""

from __future__ import annotations

from pathlib import Path

from nlp_policy_nz.training.track53_evidence import (
    Track53ModelSelectionReport,
    default_track53_evaluation_context,
    default_track53_model_comparison_manifest,
    evaluate_track53_selection,
    render_track53_evaluation_context_json,
    render_track53_model_comparison_manifest_json,
    render_track53_recommendation_markdown,
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


def test_track53_context_and_manifest_keep_roles_and_constraints_separate() -> None:
    """Evaluation context and comparison manifest should remain role-scoped."""
    context = default_track53_evaluation_context()
    manifest = default_track53_model_comparison_manifest()

    assert context.task_matrix[0].startswith("Encoder baseline")
    assert context.datasets[0].source_track == "Track 13"
    assert context.metrics[0].id == "argument_f1"
    assert context.hardware_constraints[0].scope == "encoder baselines"
    assert manifest.recommended_encoder == "isaacus/emubert"
    assert manifest.recommended_adjudicator == "Equall/Saul-7B-Instruct-v1"
    assert manifest.recommended_retrieval == "Kanon 2 Embedder"


def test_track53_json_and_markdown_renderers_expose_selection_artifacts() -> None:
    """Rendered artefacts should expose the completed Track 53 output."""
    context_json = render_track53_evaluation_context_json()
    manifest_json = render_track53_model_comparison_manifest_json()
    recommendation = render_track53_recommendation_markdown()

    assert '"id": "track13_argument_and_stance"' in context_json
    assert '"recommended_encoder": "isaacus/emubert"' in manifest_json
    assert "Track 53 Recommendation" in recommendation
    assert "Kanon 2 Embedder" in recommendation


def test_track53_committed_artifacts_match_rendered_outputs() -> None:
    """Committed track artifacts should match the helper renderers."""
    base = Path("conductor/tracks/archive/track53_legal_model_evaluation_20260629")

    assert base.joinpath("evaluation_context.json").read_text(encoding="utf-8") == (
        render_track53_evaluation_context_json()
    )
    assert (
        base.joinpath("model_comparison_manifest.json").read_text(encoding="utf-8")
        == render_track53_model_comparison_manifest_json()
    )
    assert base.joinpath("recommendation.md").read_text(encoding="utf-8") == (
        render_track53_recommendation_markdown()
    )
