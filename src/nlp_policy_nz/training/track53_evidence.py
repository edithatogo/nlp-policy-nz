"""Track 53 legal model evaluation evidence helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

LOCAL_ENCODER_MODELS: tuple[str, ...] = (
    "isaacus/emubert",
    "nlpaueb/legal-bert-base-uncased",
)
SILVER_LABEL_MODELS: tuple[str, ...] = (
    "Equall/Saul-7B-Instruct-v1",
    "isaacus/open-australian-legal-llm",
)
RETRIEVAL_MODELS: tuple[str, ...] = (
    "Kanon 2 Embedder",
    "Kanon 2 Reranker",
)


@dataclass(frozen=True)
class Track53ModelSelectionReport:
    """Repo-side Track 53 model-selection evidence."""

    task_matrix_defined: bool
    datasets_recorded: bool
    manifest_created: bool
    encoder_baseline_evaluated: bool
    silver_adjudicator_evaluated: bool
    retrieval_candidates_evaluated: bool
    tradeoffs_recorded: bool
    recommendation_written: bool
    follow_up_recorded: bool
    review_ready: bool


def evaluate_track53_selection(report: Track53ModelSelectionReport) -> dict[str, bool]:
    """Evaluate the Track 53 repo-side selection workflow."""
    baseline_contract = (
        report.task_matrix_defined and report.datasets_recorded and report.manifest_created
    )
    candidate_contract = (
        report.encoder_baseline_evaluated
        and report.silver_adjudicator_evaluated
        and report.retrieval_candidates_evaluated
        and report.tradeoffs_recorded
    )
    handoff_contract = (
        report.recommendation_written and report.follow_up_recorded and report.review_ready
    )
    return {
        "baseline_contract": baseline_contract,
        "candidate_contract": candidate_contract,
        "handoff_contract": handoff_contract,
        "repo_side_contracts": baseline_contract and candidate_contract and handoff_contract,
    }


def track53_selection_contract(
    report: Track53ModelSelectionReport,
) -> dict[str, dict[str, Any]]:
    """Return a JSON-ready Track 53 selection contract."""
    status = evaluate_track53_selection(report)
    return {
        "baseline_contract": {
            "satisfied": status["baseline_contract"],
            "required_metric": "task_matrix_defined && datasets_recorded && manifest_created",
            "observed_metric": status["baseline_contract"],
            "scope": "repo",
        },
        "candidate_contract": {
            "satisfied": status["candidate_contract"],
            "required_metric": (
                "encoder_baseline_evaluated && silver_adjudicator_evaluated && "
                "retrieval_candidates_evaluated && tradeoffs_recorded"
            ),
            "observed_metric": status["candidate_contract"],
            "scope": "repo",
        },
        "handoff_contract": {
            "satisfied": status["handoff_contract"],
            "required_metric": "recommendation_written && follow_up_recorded && review_ready",
            "observed_metric": status["handoff_contract"],
            "scope": "repo",
        },
        "repo_side_contracts": {
            "satisfied": status["repo_side_contracts"],
            "required_metric": "all repo-side selection tasks complete",
            "observed_metric": status["repo_side_contracts"],
            "scope": "repo",
        },
    }


def render_track53_selection_markdown(report: Track53ModelSelectionReport) -> str:
    """Render a concise Track 53 evidence summary."""
    status = evaluate_track53_selection(report)
    lines = [
        "# Track 53 Evidence",
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
            "## Model Roles",
            "",
            f"- Local encoder baselines: {', '.join(LOCAL_ENCODER_MODELS)}",
            f"- Silver-label adjudicators: {', '.join(SILVER_LABEL_MODELS)}",
            f"- Retrieval candidates: {', '.join(RETRIEVAL_MODELS)}",
        ]
    )
    return "\n".join(lines) + "\n"
