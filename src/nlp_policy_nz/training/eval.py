"""Evaluation metrics for NZ legal NLP fine-tuning tasks."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Sequence


def _safe_div(num: float, den: float) -> float:
    """Return ``num / den`` with zero protection."""
    return num / den if den else 0.0


def token_f1(prediction: Sequence[str], reference: Sequence[str]) -> float:
    """Compute bag-of-token F1 between a prediction and reference."""
    if not prediction and not reference:
        return 1.0
    if not prediction or not reference:
        return 0.0
    pred_counts = Counter(prediction)
    ref_counts = Counter(reference)
    overlap = sum((pred_counts & ref_counts).values())
    precision = _safe_div(overlap, len(prediction))
    recall = _safe_div(overlap, len(reference))
    return _safe_div(2 * precision * recall, precision + recall)


def classification_prf(
    predictions: Sequence[str],
    references: Sequence[str],
) -> dict[str, float]:
    """Return accuracy and macro precision/recall/F1 for labels."""
    if len(predictions) != len(references):
        raise ValueError("Predictions and references must have the same length")
    labels = sorted(set(predictions) | set(references))
    if not labels:
        return {"accuracy": 1.0, "macro_precision": 1.0, "macro_recall": 1.0, "macro_f1": 1.0}

    correct = sum(pred == ref for pred, ref in zip(predictions, references, strict=True))
    precisions: list[float] = []
    recalls: list[float] = []
    f1s: list[float] = []
    for label in labels:
        tp = sum(
            pred == label and ref == label
            for pred, ref in zip(predictions, references, strict=True)
        )
        fp = sum(
            pred == label and ref != label
            for pred, ref in zip(predictions, references, strict=True)
        )
        fn = sum(
            pred != label and ref == label
            for pred, ref in zip(predictions, references, strict=True)
        )
        precision = _safe_div(tp, tp + fp)
        recall = _safe_div(tp, tp + fn)
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(_safe_div(2 * precision * recall, precision + recall))

    return {
        "accuracy": _safe_div(correct, len(references)),
        "macro_precision": sum(precisions) / len(precisions),
        "macro_recall": sum(recalls) / len(recalls),
        "macro_f1": sum(f1s) / len(f1s),
    }


def _normalize_answer(value: str) -> str:
    """Normalize answer text for exact-match scoring."""
    return re.sub(r"\s+", " ", value.strip().casefold())


def exact_match(prediction: str, reference: str) -> float:
    """Return normalized exact match for QA-style answers."""
    return 1.0 if _normalize_answer(prediction) == _normalize_answer(reference) else 0.0


def maori_token_integrity(terms: Sequence[str], tokenized_texts: Sequence[Sequence[str]]) -> float:
    """Score the share of Māori terms preserved as contiguous token strings."""
    if not terms:
        return 1.0
    normalized_token_sets = [
        {_normalize_answer(token) for token in tokens}
        for tokens in tokenized_texts
    ]
    intact = 0
    for term in terms:
        normalized = _normalize_answer(term)
        if any(normalized in tokens for tokens in normalized_token_sets):
            intact += 1
    return intact / len(terms)
