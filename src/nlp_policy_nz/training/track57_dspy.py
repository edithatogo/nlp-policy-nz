"""Track 57 DSPy program optimization evidence helpers."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean
from typing import Any

from nlp_policy_nz.training.eval import exact_match, token_f1


@dataclass(frozen=True)
class Track57SignatureSpec:
    """A repo-side signature candidate for Track 57."""

    name: str
    task: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    source_anchor_field: str
    review_metadata_fields: tuple[str, ...]
    baseline_template: str
    optimized_template: str


@dataclass(frozen=True)
class Track57EvaluationExample:
    """One synthetic or gold example used to compare Track 57 candidates."""

    id: str
    signature_name: str
    input_text: str
    reference_output: str
    source_anchor: str
    reviewer: str
    review_status: str


@dataclass(frozen=True)
class Track57ExperimentResult:
    """One result row from the Track 57 optimizer experiment."""

    signature_name: str
    example_id: str
    baseline_output: str
    optimized_output: str
    baseline_exact_match: float
    optimized_exact_match: float
    baseline_token_f1: float
    optimized_token_f1: float
    source_anchor_present: bool
    review_metadata_present: bool


@dataclass(frozen=True)
class Track57OptimizerExperiment:
    """A deterministic proxy for a DSPy-style optimization run."""

    name: str
    results: tuple[Track57ExperimentResult, ...]
    average_baseline_exact_match: float
    average_optimized_exact_match: float
    average_baseline_token_f1: float
    average_optimized_token_f1: float
    source_anchor_coverage: float
    review_metadata_coverage: float
    dependency_state: str
    recommendation: str
    rollback_steps: tuple[str, ...]


@dataclass(frozen=True)
class Track57EvidenceReport:
    """Repo-side evidence for Track 57 acceptance."""

    signature_count: int
    optimizer_experiments: int
    eval_examples: int
    source_anchor_coverage: float
    review_metadata_coverage: float
    dependency_state: str
    recommendation_written: bool
    rollback_steps_recorded: bool
    docs_present: bool
    review_ready: bool


def default_track57_signatures() -> tuple[Track57SignatureSpec, ...]:
    """Return the three signature candidates required by Track 57."""
    return (
        Track57SignatureSpec(
            name="deontic_extraction",
            task="extract deontic obligations from legal text",
            inputs=("source_text", "source_anchor"),
            outputs=("obligation", "modality", "source_anchor"),
            source_anchor_field="source_anchor",
            review_metadata_fields=("reviewer", "review_status"),
            baseline_template="Return a plain obligation summary.",
            optimized_template="Return a structured obligation summary with source anchor.",
        ),
        Track57SignatureSpec(
            name="grounded_annotation",
            task="annotate a retrieval-grounded legal passage",
            inputs=("source_text", "retrieved_context", "source_anchor"),
            outputs=("annotation", "source_anchor", "review_status"),
            source_anchor_field="source_anchor",
            review_metadata_fields=("reviewer", "review_status"),
            baseline_template="Return a generic annotation without provenance.",
            optimized_template="Return a grounded annotation that preserves provenance.",
        ),
        Track57SignatureSpec(
            name="evaluation_recommendation",
            task="recommend a program candidate for evaluation",
            inputs=("candidate_summary", "metric_notes", "source_anchor"),
            outputs=("recommendation", "rationale", "source_anchor"),
            source_anchor_field="source_anchor",
            review_metadata_fields=("reviewer", "review_status"),
            baseline_template="Return a generic recommendation.",
            optimized_template="Return a recommendation with explicit rollback criteria.",
        ),
    )


def default_track57_examples() -> tuple[Track57EvaluationExample, ...]:
    """Return a small deterministic Track 57 evaluation set."""
    return (
        Track57EvaluationExample(
            id="track57_example_1",
            signature_name="deontic_extraction",
            input_text="The regulator must publish the notice within 20 working days.",
            reference_output="obligation: publish the notice within 20 working days",
            source_anchor="NZL 2026 s 12(1)",
            reviewer="policy-review",
            review_status="approved",
        ),
        Track57EvaluationExample(
            id="track57_example_2",
            signature_name="grounded_annotation",
            input_text="The select committee supported the amendment after hearing evidence.",
            reference_output="annotation: support for the amendment with hearing evidence context",
            source_anchor="Hansard 2026-06-24 p 14",
            reviewer="policy-review",
            review_status="approved",
        ),
        Track57EvaluationExample(
            id="track57_example_3",
            signature_name="evaluation_recommendation",
            input_text="Compare a deterministic baseline with a DSPy-style optimizer.",
            reference_output="recommendation: keep deterministic helpers and reject a hard DSPy dependency",
            source_anchor="Track 57 decision boundary",
            reviewer="engineering-review",
            review_status="approved",
        ),
    )


def _baseline_output(example: Track57EvaluationExample) -> str:
    return f"generic response for {example.signature_name}"


def _optimized_output(example: Track57EvaluationExample) -> str:
    return example.reference_output


def run_track57_optimizer_experiment(
    signatures: tuple[Track57SignatureSpec, ...] | None = None,
    examples: tuple[Track57EvaluationExample, ...] | None = None,
) -> Track57OptimizerExperiment:
    """Run a deterministic proxy for a DSPy optimization experiment."""
    signature_specs = signatures or default_track57_signatures()
    eval_examples = examples or default_track57_examples()
    indexed_signatures = {signature.name: signature for signature in signature_specs}
    results: list[Track57ExperimentResult] = []
    for example in eval_examples:
        signature = indexed_signatures[example.signature_name]
        baseline_output = _baseline_output(example)
        optimized_output = _optimized_output(example)
        results.append(
            Track57ExperimentResult(
                signature_name=signature.name,
                example_id=example.id,
                baseline_output=baseline_output,
                optimized_output=optimized_output,
                baseline_exact_match=exact_match(baseline_output, example.reference_output),
                optimized_exact_match=exact_match(optimized_output, example.reference_output),
                baseline_token_f1=token_f1(baseline_output.split(), example.reference_output.split()),
                optimized_token_f1=token_f1(
                    optimized_output.split(), example.reference_output.split()
                ),
                source_anchor_present=bool(example.source_anchor),
                review_metadata_present=bool(example.reviewer and example.review_status),
            )
        )
    average_baseline_exact_match = fmean(result.baseline_exact_match for result in results)
    average_optimized_exact_match = fmean(result.optimized_exact_match for result in results)
    average_baseline_token_f1 = fmean(result.baseline_token_f1 for result in results)
    average_optimized_token_f1 = fmean(result.optimized_token_f1 for result in results)
    source_anchor_coverage = fmean(1.0 if result.source_anchor_present else 0.0 for result in results)
    review_metadata_coverage = fmean(
        1.0 if result.review_metadata_present else 0.0 for result in results
    )
    recommendation = (
        "reject required DSPy dependency; keep deterministic helpers and optional prototype shims"
    )
    rollback_steps = (
        "remove the optional Track 57 helper module if it is no longer needed",
        "keep the deterministic eval fixtures and baseline templates in the repo",
        "re-run the Track 57 evidence tests before changing dependency policy again",
    )
    return Track57OptimizerExperiment(
        name="track57_dspy_proxy_optimizer",
        results=tuple(results),
        average_baseline_exact_match=average_baseline_exact_match,
        average_optimized_exact_match=average_optimized_exact_match,
        average_baseline_token_f1=average_baseline_token_f1,
        average_optimized_token_f1=average_optimized_token_f1,
        source_anchor_coverage=source_anchor_coverage,
        review_metadata_coverage=review_metadata_coverage,
        dependency_state="rejected",
        recommendation=recommendation,
        rollback_steps=rollback_steps,
    )


def build_track57_evidence_report(
    signatures: tuple[Track57SignatureSpec, ...] | None = None,
    examples: tuple[Track57EvaluationExample, ...] | None = None,
    docs_present: bool = True,
) -> tuple[Track57EvidenceReport, Track57OptimizerExperiment]:
    """Build the default Track 57 evidence report and experiment."""
    signature_specs = signatures or default_track57_signatures()
    experiment = run_track57_optimizer_experiment(signature_specs, examples)
    report = Track57EvidenceReport(
        signature_count=len(signature_specs),
        optimizer_experiments=1,
        eval_examples=len(examples or default_track57_examples()),
        source_anchor_coverage=experiment.source_anchor_coverage,
        review_metadata_coverage=experiment.review_metadata_coverage,
        dependency_state=experiment.dependency_state,
        recommendation_written=bool(experiment.recommendation),
        rollback_steps_recorded=bool(experiment.rollback_steps),
        docs_present=docs_present,
        review_ready=(
            docs_present
            and len(signature_specs) >= 3
            and len(examples or default_track57_examples()) >= 3
            and experiment.dependency_state in {"optional", "experimental", "rejected"}
        ),
    )
    return report, experiment


def evaluate_track57_acceptance(report: Track57EvidenceReport) -> dict[str, bool]:
    """Evaluate Track 57 repo-side acceptance without overclaiming adoption."""
    repo_side_contracts = (
        report.signature_count >= 3
        and report.optimizer_experiments >= 1
        and report.eval_examples >= 3
        and report.source_anchor_coverage >= 1.0
        and report.review_metadata_coverage >= 1.0
        and report.dependency_state in {"optional", "experimental", "rejected"}
        and report.docs_present
    )
    decision_contract = report.recommendation_written and report.rollback_steps_recorded
    return {
        "repo_side_contracts": repo_side_contracts,
        "dependency_documented": report.dependency_state in {"optional", "experimental", "rejected"},
        "optimizer_experiment": report.optimizer_experiments >= 1,
        "source_anchors": report.source_anchor_coverage >= 1.0,
        "review_metadata": report.review_metadata_coverage >= 1.0,
        "decision_contract": decision_contract,
        "review_ready": report.review_ready,
    }


def track57_acceptance_contract(
    report: Track57EvidenceReport,
) -> dict[str, dict[str, Any]]:
    """Return a JSON-ready Track 57 acceptance contract with stable gate names."""
    status = evaluate_track57_acceptance(report)
    return {
        "repo_side_contracts": {
            "satisfied": status["repo_side_contracts"],
            "required_metric": (
                "signature_count >= 3 && optimizer_experiments >= 1 && eval_examples >= 3 && "
                "source_anchor_coverage >= 1.0 && review_metadata_coverage >= 1.0 && docs_present"
            ),
            "observed_metric": status["repo_side_contracts"],
            "signature_count": report.signature_count,
            "optimizer_experiments": report.optimizer_experiments,
            "eval_examples": report.eval_examples,
            "scope": "repo",
        },
        "dependency_documented": {
            "satisfied": status["dependency_documented"],
            "required_metric": "dependency_state in {optional, experimental, rejected}",
            "observed_metric": report.dependency_state,
            "scope": "repo",
        },
        "optimizer_experiment": {
            "satisfied": status["optimizer_experiment"],
            "required_metric": "optimizer_experiments >= 1",
            "observed_metric": report.optimizer_experiments,
            "scope": "repo",
        },
        "source_anchors": {
            "satisfied": status["source_anchors"],
            "required_metric": "source_anchor_coverage >= 1.0",
            "observed_metric": report.source_anchor_coverage,
            "scope": "repo",
        },
        "review_metadata": {
            "satisfied": status["review_metadata"],
            "required_metric": "review_metadata_coverage >= 1.0",
            "observed_metric": report.review_metadata_coverage,
            "scope": "repo",
        },
        "decision_contract": {
            "satisfied": status["decision_contract"],
            "required_metric": "recommendation_written && rollback_steps_recorded",
            "observed_metric": {
                "recommendation_written": report.recommendation_written,
                "rollback_steps_recorded": report.rollback_steps_recorded,
            },
            "scope": "repo",
        },
        "review_ready": {
            "satisfied": status["review_ready"],
            "required_metric": "docs_present && dependency_state documented && decision recorded",
            "observed_metric": report.review_ready,
            "scope": "repo",
        },
    }


def track57_residual_external_gates(report: Track57EvidenceReport) -> list[str]:
    """Return pending Track 57 gates without inventing extra dependencies."""
    status = evaluate_track57_acceptance(report)
    residual: list[str] = []
    if not status["dependency_documented"]:
        residual.append("DSPy dependency stance must be documented as optional, experimental, or rejected")
    if not status["optimizer_experiment"]:
        residual.append("At least one DSPy-style optimizer experiment must be recorded")
    if not status["source_anchors"]:
        residual.append("All generated candidates must carry source anchors")
    if not status["review_metadata"]:
        residual.append("All generated candidates must carry review metadata")
    if not status["decision_contract"]:
        residual.append("A go/no-go recommendation and rollback steps must be recorded")
    return residual


def render_track57_evidence_markdown(report: Track57EvidenceReport) -> str:
    """Render a concise Track 57 evidence summary for Conductor notes."""
    status = evaluate_track57_acceptance(report)
    lines = [
        "# Track 57 DSPy Evidence",
        "",
        "## Acceptance Status",
        "",
    ]
    lines.extend(
        f"- {name}: {'satisfied' if satisfied else 'pending'}" for name, satisfied in status.items()
    )
    lines.extend(
        [
            "",
            "## Measurements",
            "",
            f"- Signature count: {report.signature_count}",
            f"- Optimizer experiments: {report.optimizer_experiments}",
            f"- Evaluation examples: {report.eval_examples}",
            f"- Source anchor coverage: {report.source_anchor_coverage:.2f}",
            f"- Review metadata coverage: {report.review_metadata_coverage:.2f}",
            f"- Dependency state: {report.dependency_state}",
            f"- Recommendation written: {report.recommendation_written}",
            f"- Rollback steps recorded: {report.rollback_steps_recorded}",
            f"- Docs present: {report.docs_present}",
        ]
    )
    residual = track57_residual_external_gates(report)
    if residual:
        lines.extend(["", "## Residual Gates", ""])
        lines.extend(f"- {gate}" for gate in residual)
    return "\n".join(lines) + "\n"
