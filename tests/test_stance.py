"""Tests for Track 13 stance classification."""

from __future__ import annotations

from nlp_policy_nz.discourse import StanceClassifier, evaluate_stance_accuracy


def test_stance_classifier_detects_pro_con_neutral() -> None:
    """Classifier should map debate cues to pro/con/neutral labels."""
    classifier = StanceClassifier()

    assert classifier.classify("I support this bill because it will help families.").stance == "pro"
    assert classifier.classify("I oppose this amendment because it raises costs.").stance == "con"
    assert classifier.classify("The committee reported the bill back.").stance == "neutral"


def test_stance_classifier_fixture_exceeds_accuracy_threshold() -> None:
    """Track 13 labelled stance fixture should exceed the >85% accuracy gate."""
    labelled = [
        {"text": "I support the bill and commend it to the House.", "stance": "pro"},
        {"text": "We oppose this amendment because it is harmful.", "stance": "con"},
        {"text": "This measure should pass to improve housing.", "stance": "pro"},
        {"text": "The bill was read a second time.", "stance": "neutral"},
        {"text": "This proposal should be rejected.", "stance": "con"},
        {"text": "The member resumed their seat.", "stance": "neutral"},
    ]

    accuracy = evaluate_stance_accuracy(labelled, classifier=StanceClassifier())

    assert accuracy >= 0.85
