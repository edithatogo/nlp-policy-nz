"""Track 13 acceptance evidence helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

MIN_ARGUMENT_F1 = 0.80
MIN_STANCE_ACCURACY = 0.85
MIN_HELD_OUT_SEGMENTS = 500
MIN_COVERAGE_PERCENT = 90.0

HELD_OUT_SOURCES: frozenset[str] = frozenset(
    {"held_out_hansard", "human_annotated_hansard", "gold_hansard"}
)
NON_MODEL_MARKERS: tuple[str, ...] = (
    "fixture",
    "heuristic",
    "mock",
    "rule-based",
    "rule_",
    "rules",
)
TRANSFORMER_MODEL_MARKERS: tuple[str, ...] = (
    "bert",
    "legal-bert",
    "transformer",
)


@dataclass(frozen=True)
class Track13EvidenceReport:
    """Measured evidence for Track 13 acceptance criteria."""

    argument_component_f1: float
    argument_component_segments: int
    argument_component_model_id: str
    argument_component_evaluation_source: str
    stance_accuracy: float
    stance_segments: int
    stance_model_id: str
    stance_evaluation_source: str
    coverage_percent: float
    aif_jsonld_export: bool
    pipeline_schema_fields: bool


def evaluate_track13_acceptance(report: Track13EvidenceReport) -> dict[str, bool]:
    """Evaluate Track 13 acceptance criteria without overclaiming fixture results."""
    argument_gate = (
        report.argument_component_f1 >= MIN_ARGUMENT_F1
        and report.argument_component_segments >= MIN_HELD_OUT_SEGMENTS
        and _is_transformer_model(report.argument_component_model_id)
        and _is_held_out_source(report.argument_component_evaluation_source)
    )
    stance_gate = (
        report.stance_accuracy >= MIN_STANCE_ACCURACY
        and report.stance_segments >= MIN_HELD_OUT_SEGMENTS
        and _is_transformer_model(report.stance_model_id)
        and _is_held_out_source(report.stance_evaluation_source)
    )
    return {
        "argument_component_classifier": argument_gate,
        "stance_classifier": stance_gate,
        "aif_jsonld_export": report.aif_jsonld_export,
        "pipeline_schema_fields": report.pipeline_schema_fields,
        "coverage": report.coverage_percent >= MIN_COVERAGE_PERCENT,
        "repo_side_contracts": (
            report.aif_jsonld_export
            and report.pipeline_schema_fields
            and report.coverage_percent >= MIN_COVERAGE_PERCENT
        ),
    }


def track13_acceptance_contract(
    report: Track13EvidenceReport,
) -> dict[str, dict[str, Any]]:
    """Return a JSON-ready Track 13 acceptance contract with stable gate names."""
    status = evaluate_track13_acceptance(report)
    return {
        "argument_component_classifier": {
            "satisfied": status["argument_component_classifier"],
            "required_metric": f"f1 >= {MIN_ARGUMENT_F1}",
            "observed_metric": report.argument_component_f1,
            "minimum_segments": MIN_HELD_OUT_SEGMENTS,
            "observed_segments": report.argument_component_segments,
            "model_id": report.argument_component_model_id,
            "evaluation_source": report.argument_component_evaluation_source,
            "requires_transformer_model": True,
            "requires_held_out_hansard": True,
            "scope": "external",
        },
        "stance_classifier": {
            "satisfied": status["stance_classifier"],
            "required_metric": f"accuracy >= {MIN_STANCE_ACCURACY}",
            "observed_metric": report.stance_accuracy,
            "minimum_segments": MIN_HELD_OUT_SEGMENTS,
            "observed_segments": report.stance_segments,
            "model_id": report.stance_model_id,
            "evaluation_source": report.stance_evaluation_source,
            "requires_transformer_model": True,
            "requires_held_out_hansard": True,
            "scope": "external",
        },
        "aif_jsonld_export": {
            "satisfied": status["aif_jsonld_export"],
            "required_metric": "implemented == true",
            "observed_metric": report.aif_jsonld_export,
            "scope": "repo",
        },
        "pipeline_schema_fields": {
            "satisfied": status["pipeline_schema_fields"],
            "required_metric": "implemented == true",
            "observed_metric": report.pipeline_schema_fields,
            "scope": "repo",
        },
        "coverage": {
            "satisfied": status["coverage"],
            "required_metric": f"coverage_percent >= {MIN_COVERAGE_PERCENT}",
            "observed_metric": report.coverage_percent,
            "scope": "repo",
        },
        "repo_side_contracts": {
            "satisfied": status["repo_side_contracts"],
            "required_metric": "aif_jsonld_export && pipeline_schema_fields && coverage",
            "observed_metric": status["repo_side_contracts"],
            "scope": "repo",
        },
    }


def track13_residual_external_gates(report: Track13EvidenceReport) -> list[str]:
    """Return pending external classifier gates without listing repo-side gaps."""
    status = evaluate_track13_acceptance(report)
    residual: list[str] = []
    if not status["argument_component_classifier"]:
        residual.append(
            "argument_component_classifier requires Legal-BERT/transformer "
            f"held-out Hansard F1 >= {MIN_ARGUMENT_F1:.3f} over at least "
            f"{MIN_HELD_OUT_SEGMENTS} human-labelled segments"
        )
    if not status["stance_classifier"]:
        residual.append(
            "stance_classifier requires Legal-BERT/transformer held-out Hansard "
            f"accuracy >= {MIN_STANCE_ACCURACY:.3f} over at least "
            f"{MIN_HELD_OUT_SEGMENTS} human-labelled segments"
        )
    return residual


def render_track13_evidence_markdown(report: Track13EvidenceReport) -> str:
    """Render a concise Track 13 evidence summary for conductor notes."""
    status = evaluate_track13_acceptance(report)
    lines = [
        "# Track 13 Evidence",
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
            f"- Argument component F1: {report.argument_component_f1:.3f} "
            f"over {report.argument_component_segments} segments "
            f"({report.argument_component_evaluation_source}, {report.argument_component_model_id})",
            f"- Stance accuracy: {report.stance_accuracy:.3f} "
            f"over {report.stance_segments} segments "
            f"({report.stance_evaluation_source}, {report.stance_model_id})",
            f"- Coverage: {report.coverage_percent:.1f}%",
        ]
    )
    residual = track13_residual_external_gates(report)
    if residual:
        lines.extend(["", "## Residual External Gates", ""])
        lines.extend(f"- {gate}" for gate in residual)
    return "\n".join(lines) + "\n"


def _is_transformer_model(model_id: str) -> bool:
    """Return whether a model identifier denotes a transformer fine-tune."""
    folded = model_id.casefold()
    if any(marker in folded for marker in NON_MODEL_MARKERS):
        return False
    return any(marker in folded for marker in TRANSFORMER_MODEL_MARKERS)


def _is_held_out_source(source: str) -> bool:
    """Return whether an evaluation source is held-out Hansard evidence."""
    return source.casefold() in HELD_OUT_SOURCES
