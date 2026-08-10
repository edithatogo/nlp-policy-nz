"""Deterministic evaluation for offline structured candidates."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def evaluate_candidate(
    candidate: Mapping[str, Any], expected: Mapping[str, Any]
) -> dict[str, Any]:
    """Compare selected fields and return a non-promotional evaluation report."""
    fields = ("cleaned_tokens", "nz_act_citations", "te_reo_terms", "stance")
    comparisons: dict[str, bool] = {}
    for field in fields:
        actual = candidate.get(field, [] if field != "stance" else None)
        target = expected.get(field, [] if field != "stance" else None)
        comparisons[field] = actual == target
    matched = sum(comparisons.values())
    return {
        "schema": "track105-candidate-evaluation-v1",
        "fields_checked": list(fields),
        "field_matches": comparisons,
        "matched_fields": matched,
        "field_count": len(fields),
        "promotion_allowed": False,
        "review_required": True,
    }


__all__ = ["evaluate_candidate"]
