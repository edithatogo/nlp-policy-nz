"""Local extractive evaluation helpers for governance orchestration."""

from __future__ import annotations

import re

from nlp_policy_nz.orchestration.haystack.decision import FAITHFULNESS_EVALUATOR_AUTHORITATIVE

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def exact_match_score(predicted: str, gold: str) -> float:
    """Return 1.0 for an exact string match, otherwise 0.0."""
    return 1.0 if predicted == gold else 0.0


def sas_proxy_score(predicted: str, gold: str) -> float:
    """Return a Jaccard similarity proxy for Haystack SAS evaluation."""
    predicted_tokens = {token.lower() for token in _TOKEN_PATTERN.findall(predicted)}
    gold_tokens = {token.lower() for token in _TOKEN_PATTERN.findall(gold)}
    if not predicted_tokens and not gold_tokens:
        return 1.0
    if not predicted_tokens or not gold_tokens:
        return 0.0
    intersection = predicted_tokens & gold_tokens
    union = predicted_tokens | gold_tokens
    return len(intersection) / len(union)


def emit_scorecard(
    predictions: list[str],
    ground_truths: list[str],
) -> dict[str, object]:
    """Emit a local evaluation scorecard for extractive answers."""
    if len(predictions) != len(ground_truths):
        msg = "predictions and ground_truths must have the same length"
        raise ValueError(msg)

    individual_scores = [
        {
            "exact_match": exact_match_score(prediction, gold),
            "sas_proxy": sas_proxy_score(prediction, gold),
        }
        for prediction, gold in zip(predictions, ground_truths, strict=True)
    ]
    exact_match = sum(score["exact_match"] for score in individual_scores) / len(individual_scores)
    sas_proxy = sum(score["sas_proxy"] for score in individual_scores) / len(individual_scores)
    return {
        "exact_match": exact_match,
        "sas_proxy": sas_proxy,
        "individual_scores": individual_scores,
        "faithfulness_evaluator_authoritative": FAITHFULNESS_EVALUATOR_AUTHORITATIVE,
        "promotion_allowed": False,
    }
