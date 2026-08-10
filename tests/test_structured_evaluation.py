"""Tests for deterministic Track 105 candidate evaluation."""

from nlp_policy_nz.structured_evaluation import evaluate_candidate


def test_evaluation_is_complete_but_never_promotional() -> None:
    values = {"cleaned_tokens": ["a"], "stance": "neutral"}
    report = evaluate_candidate(values, values)
    assert report["matched_fields"] == report["field_count"]
    assert report["promotion_allowed"] is False
    assert report["review_required"] is True


def test_evaluation_identifies_field_mismatch() -> None:
    report = evaluate_candidate(
        {"cleaned_tokens": ["a"], "stance": "pro"},
        {"cleaned_tokens": ["b"], "stance": "neutral"},
    )
    assert report["field_matches"]["cleaned_tokens"] is False
    assert report["field_matches"]["stance"] is False
