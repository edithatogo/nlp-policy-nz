"""Track 53 legal model evaluation evidence helpers."""

from __future__ import annotations

import json
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
class Track53EvaluationDataset:
    """Dataset or benchmark artifact used for Track 53 selection."""

    id: str
    source_track: str
    task: str
    role: str
    measurement: str
    notes: str


@dataclass(frozen=True)
class Track53Metric:
    """One metric used to compare Track 53 candidate models."""

    id: str
    direction: str
    description: str
    notes: str


@dataclass(frozen=True)
class Track53HardwareConstraint:
    """One hardware or privacy constraint relevant to Track 53."""

    id: str
    scope: str
    description: str


@dataclass(frozen=True)
class Track53ModelCandidate:
    """One Track 53 candidate model and its intended role."""

    model: str
    category: str
    access_mode: str
    role: str
    notes: str


@dataclass(frozen=True)
class Track53EvaluationContext:
    """Repo-side evaluation context for Track 53."""

    task_matrix: tuple[str, ...]
    datasets: tuple[Track53EvaluationDataset, ...]
    metrics: tuple[Track53Metric, ...]
    hardware_constraints: tuple[Track53HardwareConstraint, ...]


@dataclass(frozen=True)
class Track53ModelComparisonManifest:
    """Repo-side model comparison manifest for Track 53."""

    encoder_candidates: tuple[Track53ModelCandidate, ...]
    adjudicator_candidates: tuple[Track53ModelCandidate, ...]
    retrieval_candidates: tuple[Track53ModelCandidate, ...]
    recommended_encoder: str
    recommended_adjudicator: str
    recommended_retrieval: str
    tradeoffs: tuple[str, ...]
    privacy_constraints: tuple[str, ...]
    follow_up_issue: str


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


def default_track53_evaluation_context() -> Track53EvaluationContext:
    """Return the Track 53 evaluation context used for repo-side selection."""
    return Track53EvaluationContext(
        task_matrix=(
            "Encoder baseline: argument and stance classification",
            "Adjudicator: silver-label disagreement review",
            "Retrieval: semantic linking and citation-search support",
        ),
        datasets=(
            Track53EvaluationDataset(
                id="track13_argument_and_stance",
                source_track="Track 13",
                task="argument and stance classification",
                role="encoder baseline evaluation",
                measurement="held-out F1/accuracy proxy from repo-side contracts",
                notes="Tracks the NZ Hansard argument/stance workload without gold evidence.",
            ),
            Track53EvaluationDataset(
                id="track22_nz_mleb_fixture",
                source_track="Track 22",
                task="retrieval",
                role="retrieval/linking evaluation",
                measurement="fixture query coverage and schema validation",
                notes="Deterministic NZ retrieval fixture used as a local benchmark proxy.",
            ),
            Track53EvaluationDataset(
                id="track20_training_splits",
                source_track="Track 20",
                task="fine-tuning readiness",
                role="hardware and training compatibility",
                measurement="job-spec and split-contract validation",
                notes="Provides a local boundary for what can be fine-tuned and published later.",
            ),
        ),
        metrics=(
            Track53Metric(
                id="argument_f1",
                direction="higher-is-better",
                description="Argument component quality on NZ Hansard text",
                notes="Use to compare encoder candidates in Track 53 context.",
            ),
            Track53Metric(
                id="stance_accuracy",
                direction="higher-is-better",
                description="Stance classification accuracy on NZ debate text",
                notes="Must remain separated from gold-label claims.",
            ),
            Track53Metric(
                id="retrieval_precision",
                direction="higher-is-better",
                description="Retrieval and semantic-linking usefulness",
                notes="Approximates candidate value for search and ranking work.",
            ),
            Track53Metric(
                id="latency_and_memory",
                direction="lower-is-better",
                description="Inference cost for local or air-gapped use",
                notes="Important for CPU-only and small-GPU deployment decisions.",
            ),
        ),
        hardware_constraints=(
            Track53HardwareConstraint(
                id="local_cpu_only",
                scope="encoder baselines",
                description="Candidate must be usable in a local CPU or small-GPU setup.",
            ),
            Track53HardwareConstraint(
                id="self_hosted_or_api",
                scope="silver-label adjudicators",
                description="Candidate may require a local host or API access but must not be treated as gold evidence.",
            ),
            Track53HardwareConstraint(
                id="privacy_gate",
                scope="all models",
                description="No NZ sensitive text should be sent to external services without explicit review.",
            ),
        ),
    )


def default_track53_model_comparison_manifest() -> Track53ModelComparisonManifest:
    """Return the default Track 53 model comparison manifest."""
    return Track53ModelComparisonManifest(
        encoder_candidates=(
            Track53ModelCandidate(
                model="isaacus/emubert",
                category="encoder",
                access_mode="open-hf",
                role="preferred local encoder baseline",
                notes="Closer legal-domain fit for NZ law than the legacy Legal-BERT comparator.",
            ),
            Track53ModelCandidate(
                model="nlpaueb/legal-bert-base-uncased",
                category="encoder",
                access_mode="open-hf",
                role="legacy encoder comparator",
                notes="Retained as a reproducible baseline, not the presumed best choice.",
            ),
        ),
        adjudicator_candidates=(
            Track53ModelCandidate(
                model="Equall/Saul-7B-Instruct-v1",
                category="adjudicator",
                access_mode="local-or-self-hosted",
                role="silver-label adjudication candidate",
                notes="Strong candidate for disagreement review and explanation generation.",
            ),
            Track53ModelCandidate(
                model="isaacus/open-australian-legal-llm",
                category="adjudicator",
                access_mode="open-hf",
                role="AU-to-NZ silver-label adjudicator",
                notes="Useful where AU legal pretraining may transfer to NZ legal text.",
            ),
        ),
        retrieval_candidates=(
            Track53ModelCandidate(
                model="Kanon 2 Embedder",
                category="retrieval",
                access_mode="api-or-airgapped",
                role="retrieval and semantic linking candidate",
                notes="Evaluate for citation search and document similarity support.",
            ),
            Track53ModelCandidate(
                model="Kanon 2 Reranker",
                category="retrieval",
                access_mode="api-or-airgapped",
                role="ranking and reranking candidate",
                notes="Useful for reordering retrieval hits where exact open weights are unavailable.",
            ),
        ),
        recommended_encoder="isaacus/emubert",
        recommended_adjudicator="Equall/Saul-7B-Instruct-v1",
        recommended_retrieval="Kanon 2 Embedder",
        tradeoffs=(
            "EmuBERT is lighter and more local-friendly, while Legal-BERT is retained for comparison.",
            "Saul-7B gives a practical local/legal LLM option, but still needs privacy review.",
            "Kanon-style retrieval improves semantic search but may require proprietary or air-gapped access.",
        ),
        privacy_constraints=(
            "Do not route sensitive NZ text to external services without explicit review.",
            "Silver-label outputs must remain separate from human-gold claims.",
        ),
        follow_up_issue=(
            "Revisit after NZ-legislation fine-tuning to compare NZ-adapted encoders, "
            "legal LLM adjudicators, and frontier-model silver labelling."
        ),
    )


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


def render_track53_evaluation_context_json() -> str:
    """Return the Track 53 evaluation context as formatted JSON."""
    context = default_track53_evaluation_context()
    return json.dumps(
        {
            "task_matrix": list(context.task_matrix),
            "datasets": [dataset.__dict__ for dataset in context.datasets],
            "metrics": [metric.__dict__ for metric in context.metrics],
            "hardware_constraints": [
                constraint.__dict__ for constraint in context.hardware_constraints
            ],
        },
        indent=2,
    ) + "\n"


def render_track53_model_comparison_manifest_json() -> str:
    """Return the Track 53 model comparison manifest as formatted JSON."""
    manifest = default_track53_model_comparison_manifest()
    return json.dumps(
        {
            "encoder_candidates": [candidate.__dict__ for candidate in manifest.encoder_candidates],
            "adjudicator_candidates": [
                candidate.__dict__ for candidate in manifest.adjudicator_candidates
            ],
            "retrieval_candidates": [
                candidate.__dict__ for candidate in manifest.retrieval_candidates
            ],
            "recommended_encoder": manifest.recommended_encoder,
            "recommended_adjudicator": manifest.recommended_adjudicator,
            "recommended_retrieval": manifest.recommended_retrieval,
            "tradeoffs": list(manifest.tradeoffs),
            "privacy_constraints": list(manifest.privacy_constraints),
            "follow_up_issue": manifest.follow_up_issue,
        },
        indent=2,
    ) + "\n"


def render_track53_recommendation_markdown() -> str:
    """Return the Track 53 final recommendation summary as Markdown."""
    manifest = default_track53_model_comparison_manifest()
    lines = [
        "# Track 53 Recommendation",
        "",
        "## Selected Roles",
        "",
        f"- Encoder baseline: {manifest.recommended_encoder}",
        f"- Silver-label adjudicator: {manifest.recommended_adjudicator}",
        f"- Retrieval candidate: {manifest.recommended_retrieval}",
        "",
        "## Tradeoffs",
        "",
    ]
    lines.extend(f"- {tradeoff}" for tradeoff in manifest.tradeoffs)
    lines.extend(
        [
            "",
            "## Privacy Constraints",
            "",
        ]
    )
    lines.extend(f"- {constraint}" for constraint in manifest.privacy_constraints)
    lines.extend(
        [
            "",
            "## Follow-Up",
            "",
            f"- {manifest.follow_up_issue}",
        ]
    )
    return "\n".join(lines) + "\n"
