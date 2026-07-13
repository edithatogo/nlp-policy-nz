"""Leakage-resistant evaluation metrics for reconstructed parliament structure."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .structure import StructureDocument


class EvaluationThresholds(BaseModel):
    """Minimum held-out scores required for promotion."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    min_structure_accuracy: float = Field(default=0.9, ge=0, le=1)
    min_speaker_accuracy: float = Field(default=0.9, ge=0, le=1)
    min_link_f1: float = Field(default=0.8, ge=0, le=1)
    min_span_fidelity: float = Field(default=0.95, ge=0, le=1)
    min_abstention_recall: float = Field(default=0.9, ge=0, le=1)


class StructureEvaluation(BaseModel):
    """Independent held-out scores and promotion result."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    structure_accuracy: float = Field(ge=0, le=1)
    speaker_accuracy: float = Field(ge=0, le=1)
    link_f1: float = Field(ge=0, le=1)
    span_fidelity: float = Field(ge=0, le=1)
    abstention_recall: float = Field(ge=0, le=1)
    passed: bool
    failures: tuple[str, ...] = ()


def evaluate_structure(
    reference: StructureDocument,
    candidate: StructureDocument,
    *,
    thresholds: EvaluationThresholds | None = None,
) -> StructureEvaluation:
    """Compare candidate assertions without using candidate text as gold data."""
    if reference.page_id != candidate.page_id:
        raise ValueError("reference and candidate must describe the same page")
    limits = thresholds or EvaluationThresholds()
    values = {
        "structure_accuracy": _sequence_score(
            [(node.node_type, node.label) for node in reference.nodes],
            [(node.node_type, node.label) for node in candidate.nodes],
        ),
        "speaker_accuracy": _speaker_score(reference, candidate),
        "link_f1": _f1(_link_keys(reference), _link_keys(candidate)),
        "span_fidelity": _span_score(reference, candidate),
        "abstention_recall": _abstention_score(reference, candidate),
    }
    gates = {
        "structure_accuracy": values["structure_accuracy"] >= limits.min_structure_accuracy,
        "speaker_accuracy": values["speaker_accuracy"] >= limits.min_speaker_accuracy,
        "link_f1": values["link_f1"] >= limits.min_link_f1,
        "span_fidelity": values["span_fidelity"] >= limits.min_span_fidelity,
        "abstention_recall": values["abstention_recall"] >= limits.min_abstention_recall,
    }
    failures = tuple(name for name, passed in gates.items() if not passed)
    return StructureEvaluation(**values, passed=not failures, failures=failures)


def _sequence_score(reference: list[tuple[str, str]], candidate: list[tuple[str, str]]) -> float:
    if not reference:
        return 1.0
    return sum(
        index < len(candidate) and item == candidate[index] for index, item in enumerate(reference)
    ) / len(reference)


def _speaker_score(reference: StructureDocument, candidate: StructureDocument) -> float:
    if not reference.speakers:
        return 1.0
    candidates = {item.surface_form: item for item in candidate.speakers}
    return sum(
        item.surface_form in candidates
        and item.identity_id == candidates[item.surface_form].identity_id
        and item.abstained == candidates[item.surface_form].abstained
        for item in reference.speakers
    ) / len(reference.speakers)


def _link_keys(document: StructureDocument) -> set[tuple[str, str, str]]:
    return {(link.subject_id, link.relation, link.target_text) for link in document.links}


def _f1(reference: set[tuple[str, str, str]], candidate: set[tuple[str, str, str]]) -> float:
    if not reference and not candidate:
        return 1.0
    if not reference or not candidate:
        return 0.0
    true_positive = len(reference & candidate)
    precision = true_positive / len(candidate)
    recall = true_positive / len(reference)
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _span_score(reference: StructureDocument, candidate: StructureDocument) -> float:
    expected = _span_keys(reference)
    actual = _span_keys(candidate)
    return 1.0 if not expected else len(expected & actual) / len(expected)


def _span_keys(document: StructureDocument) -> set[tuple[str, str, int, int, str]]:
    spans = [span for node in document.nodes for span in node.source_spans]
    spans.extend(span for item in document.speakers for span in item.source_spans)
    spans.extend(span for item in document.links for span in item.source_spans)
    spans.extend(span for item in document.review_queue for span in item.source_spans)
    return {(span.page_id, span.block_id, span.start, span.end, span.text) for span in spans}


def _abstention_score(reference: StructureDocument, candidate: StructureDocument) -> float:
    expected = {(item.kind, item.reason) for item in reference.review_queue}
    actual = {(item.kind, item.reason) for item in candidate.review_queue}
    return 1.0 if not expected else len(expected & actual) / len(expected)


__all__ = ["EvaluationThresholds", "StructureEvaluation", "evaluate_structure"]
