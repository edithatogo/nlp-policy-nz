"""Track 21 acceptance evidence helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

MIN_REGISTRY_CANDIDATES = 4
MIN_DETERMINISTIC_EXAMPLE_EVALUATIONS = 3
MIN_DRY_RUN_SCRIPTS = 4
MIN_DOWNLOADED_ARCHITECTURES = 3
MIN_MEASURED_ARCHITECTURES = 3


@dataclass(frozen=True)
class Track21EvidenceReport:
    """Evidence for Track 21 architecture exploration acceptance."""

    registry_candidates: int
    deterministic_example_evaluations: int
    dry_run_scripts: int
    architecture_report_present: bool
    cuda_available: bool
    downloaded_architectures: int
    measured_architectures: int
    pareto_frontier_identified: bool
    recommendation_present: bool
    published_evaluation_dataset: bool


def evaluate_track21_acceptance(report: Track21EvidenceReport) -> dict[str, bool]:
    """Evaluate Track 21 acceptance criteria without overclaiming dry-run evidence."""
    repo_side_contracts = (
        report.registry_candidates >= MIN_REGISTRY_CANDIDATES
        and report.deterministic_example_evaluations
        >= MIN_DETERMINISTIC_EXAMPLE_EVALUATIONS
        and report.dry_run_scripts >= MIN_DRY_RUN_SCRIPTS
    )
    external_architecture_evaluation = (
        report.cuda_available
        and report.downloaded_architectures >= MIN_DOWNLOADED_ARCHITECTURES
        and report.measured_architectures >= MIN_MEASURED_ARCHITECTURES
    )
    return {
        "repo_side_contracts": repo_side_contracts,
        "mor_pipeline_functional": report.cuda_available
        and report.downloaded_architectures >= 1,
        "external_architecture_evaluation": external_architecture_evaluation,
        "pareto_frontier": external_architecture_evaluation
        and report.pareto_frontier_identified,
        "architecture_report": report.architecture_report_present,
        "recommendation": report.recommendation_present,
        "hub_publication": report.published_evaluation_dataset,
    }


def track21_acceptance_contract(
    report: Track21EvidenceReport,
) -> dict[str, dict[str, Any]]:
    """Return a JSON-ready Track 21 acceptance contract with stable gate names."""
    status = evaluate_track21_acceptance(report)
    return {
        "repo_side_contracts": {
            "satisfied": status["repo_side_contracts"],
            "required_metric": (
                f"registry_candidates >= {MIN_REGISTRY_CANDIDATES} && "
                "deterministic_example_evaluations >= "
                f"{MIN_DETERMINISTIC_EXAMPLE_EVALUATIONS} && "
                f"dry_run_scripts >= {MIN_DRY_RUN_SCRIPTS}"
            ),
            "observed_metric": status["repo_side_contracts"],
            "registry_candidates": report.registry_candidates,
            "deterministic_example_evaluations": (
                report.deterministic_example_evaluations
            ),
            "dry_run_scripts": report.dry_run_scripts,
            "scope": "repo",
        },
        "mor_pipeline_functional": {
            "satisfied": status["mor_pipeline_functional"],
            "required_metric": "cuda_available && downloaded_architectures >= 1",
            "observed_metric": {
                "cuda_available": report.cuda_available,
                "downloaded_architectures": report.downloaded_architectures,
            },
            "requires_gpu": True,
            "scope": "external",
        },
        "external_architecture_evaluation": {
            "satisfied": status["external_architecture_evaluation"],
            "required_metric": (
                "cuda_available && downloaded_architectures >= "
                f"{MIN_DOWNLOADED_ARCHITECTURES} && measured_architectures >= "
                f"{MIN_MEASURED_ARCHITECTURES}"
            ),
            "observed_metric": {
                "cuda_available": report.cuda_available,
                "downloaded_architectures": report.downloaded_architectures,
                "measured_architectures": report.measured_architectures,
            },
            "requires_gpu": True,
            "scope": "external",
        },
        "pareto_frontier": {
            "satisfied": status["pareto_frontier"],
            "required_metric": "external measurements identify frontier",
            "observed_metric": report.pareto_frontier_identified,
            "scope": "external",
        },
        "architecture_report": {
            "satisfied": status["architecture_report"],
            "required_metric": "docs/architecture_comparison.md present",
            "observed_metric": report.architecture_report_present,
            "scope": "repo",
        },
        "recommendation": {
            "satisfied": status["recommendation"],
            "required_metric": "recommendation present",
            "observed_metric": report.recommendation_present,
            "scope": "repo",
        },
        "hub_publication": {
            "satisfied": status["hub_publication"],
            "required_metric": "evaluation dataset/results published",
            "observed_metric": report.published_evaluation_dataset,
            "scope": "external",
        },
    }


def track21_residual_external_gates(report: Track21EvidenceReport) -> list[str]:
    """Return pending Track 21 external gates without listing repo-side gaps."""
    status = evaluate_track21_acceptance(report)
    residual: list[str] = []
    if not report.cuda_available:
        residual.append("GPU/CUDA validation is required before model-run claims")
    if not status["mor_pipeline_functional"]:
        residual.append(
            "MoR pipeline functionality requires at least one downloaded architecture "
            "and a CUDA-capable runtime"
        )
    if not status["external_architecture_evaluation"]:
        residual.append(
            f"At least {MIN_MEASURED_ARCHITECTURES} architectures require downloaded "
            "checkpoints and measured NZ legal benchmark runs"
        )
    if not status["pareto_frontier"]:
        residual.append(
            "Throughput-accuracy Pareto frontier must be based on measured external runs"
        )
    if not status["hub_publication"]:
        residual.append("Hugging Face publication evidence is required for evaluation data")
    return residual


def render_track21_evidence_markdown(report: Track21EvidenceReport) -> str:
    """Render a concise Track 21 evidence summary for Conductor notes."""
    status = evaluate_track21_acceptance(report)
    lines = [
        "# Track 21 Evidence",
        "",
        "## Acceptance Status",
        "",
    ]
    lines.extend(
        f"- {name}: {'satisfied' if satisfied else 'pending'}"
        for name, satisfied in status.items()
    )
    lines.extend(
        [
            "",
            "## Measurements",
            "",
            f"- Registry candidates: {report.registry_candidates}",
            "- Deterministic example evaluations: "
            f"{report.deterministic_example_evaluations}",
            f"- Dry-run scripts: {report.dry_run_scripts}",
            f"- Architecture report present: {report.architecture_report_present}",
            f"- CUDA available: {report.cuda_available}",
            f"- Downloaded architectures: {report.downloaded_architectures}",
            f"- Measured architectures: {report.measured_architectures}",
            f"- Pareto frontier identified: {report.pareto_frontier_identified}",
            f"- Recommendation present: {report.recommendation_present}",
            "- Published evaluation dataset: "
            f"{report.published_evaluation_dataset}",
        ]
    )
    residual = track21_residual_external_gates(report)
    if residual:
        lines.extend(["", "## Residual External Gates", ""])
        lines.extend(f"- {gate}" for gate in residual)
    return "\n".join(lines) + "\n"
