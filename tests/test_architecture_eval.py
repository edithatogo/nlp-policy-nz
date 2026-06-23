from __future__ import annotations

from nlp_policy_nz.training.eval_arch import (
    ArchitectureEvaluation,
    ArchitectureMetrics,
    default_architecture_registry,
    pareto_frontier,
    rank_architectures,
    recommend_architecture,
    render_architecture_report,
)
from nlp_policy_nz.training.track21_evidence import (
    Track21EvidenceReport,
    evaluate_track21_acceptance,
    render_track21_evidence_markdown,
    track21_acceptance_contract,
    track21_residual_external_gates,
)


def test_default_registry_covers_bleeding_edge_families() -> None:
    registry = default_architecture_registry()

    assert {"mor", "ttt-linear", "mamba-3", "diffusion-gemma"} <= set(registry)
    assert {
        "mor-kv",
        "devestral",
        "ttt-rnn",
        "ssd",
        "sambay",
        "gemma-diffusion",
        "nex-n2",
        "nex-rl",
        "nex-au",
        "cosmos-3",
        "hy-world-2",
        "mimo-v2-5",
        "minimax-01",
        "ring",
        "ling",
        "tirex",
    } <= set(registry)
    assert registry["mor"].family == "mixture-of-recursions"
    assert "nz-legal-citation" in registry["mamba-3"].tasks


def test_pareto_frontier_excludes_dominated_candidates() -> None:
    evaluations = [
        ArchitectureEvaluation(
            "mor",
            "nz-legal-dev",
            ArchitectureMetrics(
                tokens_per_second=1400,
                peak_memory_gb=24,
                citation_f1=0.91,
                perplexity=11.0,
                max_context_tokens=32768,
                maori_token_integrity=0.98,
            ),
        ),
        ArchitectureEvaluation(
            "ttt-linear",
            "nz-legal-dev",
            ArchitectureMetrics(
                tokens_per_second=900,
                peak_memory_gb=30,
                citation_f1=0.88,
                perplexity=14.5,
                max_context_tokens=16384,
                maori_token_integrity=0.95,
            ),
        ),
        ArchitectureEvaluation(
            "mamba-3",
            "nz-legal-dev",
            ArchitectureMetrics(
                tokens_per_second=2200,
                peak_memory_gb=18,
                citation_f1=0.90,
                perplexity=11.8,
                max_context_tokens=65536,
                maori_token_integrity=0.97,
            ),
        ),
    ]

    frontier = {evaluation.architecture_id for evaluation in pareto_frontier(evaluations)}

    assert "ttt-linear" not in frontier
    assert {"mor", "mamba-3"} <= frontier


def test_ranking_prefers_throughput_accuracy_balance() -> None:
    evaluations = [
        ArchitectureEvaluation(
            "diffusion-gemma",
            "nz-legal-dev",
            ArchitectureMetrics(650, 20, 0.93, 10.7, 8192, 0.99),
        ),
        ArchitectureEvaluation(
            "mamba-3",
            "nz-legal-dev",
            ArchitectureMetrics(2100, 18, 0.91, 11.6, 65536, 0.98),
        ),
    ]

    ranked = rank_architectures(evaluations)

    assert ranked[0].architecture_id == "mamba-3"


def test_recommendation_and_report_are_explicit_about_repo_side_scope() -> None:
    evaluations = [
        ArchitectureEvaluation(
            "mor",
            "nz-legal-dev",
            ArchitectureMetrics(1400, 24, 0.91, 11.0, 32768, 0.98),
        ),
        ArchitectureEvaluation(
            "mamba-3",
            "nz-legal-dev",
            ArchitectureMetrics(2200, 18, 0.90, 11.8, 65536, 0.97),
        ),
    ]

    recommendation = recommend_architecture(evaluations)
    report = render_architecture_report(default_architecture_registry(), evaluations)

    assert recommendation.architecture_id == "mamba-3"
    assert "repo-side evaluation harness" in report
    assert "mamba-3" in report
    assert "External training and checkpoint publication remain gated" in report


def test_track21_repo_side_evidence_does_not_satisfy_external_model_gates() -> None:
    report = Track21EvidenceReport(
        registry_candidates=4,
        deterministic_example_evaluations=4,
        dry_run_scripts=4,
        architecture_report_present=True,
        cuda_available=False,
        downloaded_architectures=0,
        measured_architectures=0,
        pareto_frontier_identified=True,
        recommendation_present=True,
        published_evaluation_dataset=False,
    )

    status = evaluate_track21_acceptance(report)
    contract = track21_acceptance_contract(report)
    residual = track21_residual_external_gates(report)
    markdown = render_track21_evidence_markdown(report)

    assert status["repo_side_contracts"] is True
    assert status["architecture_report"] is True
    assert status["external_architecture_evaluation"] is False
    assert status["hub_publication"] is False
    assert contract["repo_side_contracts"]["scope"] == "repo"
    assert contract["external_architecture_evaluation"]["scope"] == "external"
    assert "repo_side_contracts: satisfied" in markdown
    assert any("GPU" in item for item in residual)
    assert any("Hugging Face" in item for item in residual)


def test_track21_measured_external_evidence_satisfies_acceptance_gates() -> None:
    report = Track21EvidenceReport(
        registry_candidates=4,
        deterministic_example_evaluations=4,
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
