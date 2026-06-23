"""Tests for Track 21 architecture exploration evidence reporting."""

from __future__ import annotations

from nlp_policy_nz.training.track21_evidence import (
    Track21EvidenceReport,
    evaluate_track21_acceptance,
    render_track21_evidence_markdown,
    track21_acceptance_contract,
    track21_residual_external_gates,
)


def test_repo_side_architecture_harness_does_not_satisfy_external_gates() -> None:
    """Dry-run architecture comparison must not count as live model evaluation."""
    report = Track21EvidenceReport(
        registry_candidates=4,
        deterministic_example_evaluations=4,
        dry_run_scripts=4,
        architecture_report_present=True,
        cuda_available=False,
        downloaded_architectures=0,
        measured_architectures=0,
        pareto_frontier_identified=False,
        recommendation_present=True,
        published_evaluation_dataset=False,
    )

    status = evaluate_track21_acceptance(report)

    assert status["repo_side_contracts"]
    assert not status["mor_pipeline_functional"]
    assert not status["external_architecture_evaluation"]
    assert not status["hub_publication"]


def test_measured_architecture_report_satisfies_track21_acceptance() -> None:
    """Measured external architecture evidence should satisfy all Track 21 gates."""
    report = Track21EvidenceReport(
        registry_candidates=6,
        deterministic_example_evaluations=6,
        dry_run_scripts=4,
        architecture_report_present=True,
        cuda_available=True,
        downloaded_architectures=3,
        measured_architectures=3,
        pareto_frontier_identified=True,
        recommendation_present=True,
        published_evaluation_dataset=True,
    )

    status = evaluate_track21_acceptance(report)

    assert all(status.values())


def test_track21_evidence_lists_external_training_gates() -> None:
    """Rendered evidence should keep clone/GPU/publication gates visible."""
    report = Track21EvidenceReport(
        registry_candidates=4,
        deterministic_example_evaluations=4,
        dry_run_scripts=4,
        architecture_report_present=True,
        cuda_available=False,
        downloaded_architectures=0,
        measured_architectures=0,
        pareto_frontier_identified=False,
        recommendation_present=True,
        published_evaluation_dataset=False,
    )

    markdown = render_track21_evidence_markdown(report)
    residual = track21_residual_external_gates(report)
    contract = track21_acceptance_contract(report)

    assert "repo_side_contracts: satisfied" in markdown
    assert "mor_pipeline_functional: pending" in markdown
    assert contract["repo_side_contracts"]["scope"] == "repo"
    assert contract["external_architecture_evaluation"]["scope"] == "external"
    assert any("MoR" in item for item in residual)
    assert any("GPU" in item for item in residual)
