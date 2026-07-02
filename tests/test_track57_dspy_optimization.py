"""Tests for Track 57 DSPy program optimization evidence."""

from __future__ import annotations

from nlp_policy_nz.training.track57_dspy import (
    build_track57_evidence_report,
    default_track57_examples,
    default_track57_signatures,
    evaluate_track57_acceptance,
    render_track57_evidence_markdown,
    run_track57_optimizer_experiment,
    track57_acceptance_contract,
    track57_residual_external_gates,
)


def test_track57_signature_and_example_inventory_is_present() -> None:
    signatures = default_track57_signatures()
    examples = default_track57_examples()

    assert len(signatures) == 3
    assert len(examples) == 3
    assert all(signature.source_anchor_field == "source_anchor" for signature in signatures)
    assert all("reviewer" in signature.review_metadata_fields for signature in signatures)


def test_track57_optimizer_proxy_improves_over_baseline() -> None:
    experiment = run_track57_optimizer_experiment()

    assert experiment.dependency_state == "rejected"
    assert experiment.average_optimized_exact_match >= experiment.average_baseline_exact_match
    assert experiment.average_optimized_token_f1 >= experiment.average_baseline_token_f1
    assert all(result.source_anchor_present for result in experiment.results)
    assert all(result.review_metadata_present for result in experiment.results)


def test_track57_acceptance_and_markdown_cover_the_go_no_go_decision() -> None:
    report, experiment = build_track57_evidence_report()
    status = evaluate_track57_acceptance(report)
    contract = track57_acceptance_contract(report)
    residual = track57_residual_external_gates(report)
    markdown = render_track57_evidence_markdown(report)

    assert status["repo_side_contracts"]
    assert status["dependency_documented"]
    assert status["optimizer_experiment"]
    assert status["decision_contract"]
    assert contract["repo_side_contracts"]["satisfied"]
    assert not residual
    assert "DSPy" in markdown
    assert "rollback" not in markdown.casefold() or experiment.rollback_steps

