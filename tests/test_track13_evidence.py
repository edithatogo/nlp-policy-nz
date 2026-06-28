"""Tests for Track 13 acceptance evidence reporting."""

from __future__ import annotations

from nlp_policy_nz.training.track13_evidence import (
    Track13EvidenceReport,
    evaluate_track13_acceptance,
    render_track13_evidence_markdown,
    summarize_track13_implementation_status,
    track13_acceptance_contract,
    track13_implementation_status_contract,
    track13_residual_external_gates,
)


def test_heuristic_fixture_scores_do_not_satisfy_external_training_gates() -> None:
    """Small deterministic fixtures must not be treated as held-out model evidence."""
    report = Track13EvidenceReport(
        argument_component_f1=1.0,
        argument_component_segments=4,
        argument_component_model_id="heuristic-rule-detector",
        argument_component_evaluation_source="fixture",
        stance_accuracy=1.0,
        stance_segments=6,
        stance_model_id="heuristic-rule-classifier",
        stance_evaluation_source="fixture",
        coverage_percent=94.0,
        aif_jsonld_export=True,
        pipeline_schema_fields=True,
    )

    status = evaluate_track13_acceptance(report)

    assert not status["argument_component_classifier"]
    assert not status["stance_classifier"]
    assert status["repo_side_contracts"]


def test_heuristic_transformer_label_does_not_satisfy_model_gate() -> None:
    """Model IDs must not pass the gate just by containing transformer keywords."""
    report = Track13EvidenceReport(
        argument_component_f1=0.95,
        argument_component_segments=500,
        argument_component_model_id="heuristic-transformer-detector",
        argument_component_evaluation_source="held_out_hansard",
        stance_accuracy=0.95,
        stance_segments=500,
        stance_model_id="rule-based-bert-stance",
        stance_evaluation_source="held_out_hansard",
        coverage_percent=94.0,
        aif_jsonld_export=True,
        pipeline_schema_fields=True,
    )

    status = evaluate_track13_acceptance(report)

    assert not status["argument_component_classifier"]
    assert not status["stance_classifier"]


def test_held_out_transformer_report_satisfies_track13_thresholds() -> None:
    """A properly scoped held-out evaluation should satisfy all Track 13 gates."""
    report = Track13EvidenceReport(
        argument_component_f1=0.82,
        argument_component_segments=500,
        argument_component_model_id="nlp-policy-nz/legal-bert-argument-components",
        argument_component_evaluation_source="held_out_hansard",
        stance_accuracy=0.87,
        stance_segments=500,
        stance_model_id="nlp-policy-nz/legal-bert-stance",
        stance_evaluation_source="held_out_hansard",
        coverage_percent=91.0,
        aif_jsonld_export=True,
        pipeline_schema_fields=True,
    )

    status = evaluate_track13_acceptance(report)

    assert all(status.values())


def test_track13_evidence_markdown_lists_open_external_gates() -> None:
    """Rendered evidence should make pending external gates visible."""
    report = Track13EvidenceReport(
        argument_component_f1=0.8,
        argument_component_segments=4,
        argument_component_model_id="heuristic-rule-detector",
        argument_component_evaluation_source="fixture",
        stance_accuracy=0.9,
        stance_segments=6,
        stance_model_id="heuristic-rule-classifier",
        stance_evaluation_source="fixture",
        coverage_percent=95.0,
        aif_jsonld_export=True,
        pipeline_schema_fields=True,
    )

    markdown = render_track13_evidence_markdown(report)

    assert "argument_component_classifier: pending" in markdown
    assert "stance_classifier: pending" in markdown
    assert "repo_side_contracts: satisfied" in markdown
    assert "Residual External Gates" in markdown
    assert "argument_component_classifier" in markdown


def test_track13_acceptance_contract_is_json_ready_and_explicit() -> None:
    """Structured evidence should preserve thresholds and residual gates."""
    report = Track13EvidenceReport(
        argument_component_f1=0.78,
        argument_component_segments=499,
        argument_component_model_id="nlp-policy-nz/legal-bert-argument-components",
        argument_component_evaluation_source="held_out_hansard",
        stance_accuracy=0.91,
        stance_segments=500,
        stance_model_id="heuristic-rule-classifier",
        stance_evaluation_source="fixture",
        coverage_percent=88.5,
        aif_jsonld_export=True,
        pipeline_schema_fields=True,
    )

    contract = track13_acceptance_contract(report)

    assert set(contract) == {
        "argument_component_classifier",
        "stance_classifier",
        "aif_jsonld_export",
        "pipeline_schema_fields",
        "coverage",
        "repo_side_contracts",
    }
    assert contract["argument_component_classifier"]["required_metric"] == "f1 >= 0.8"
    assert contract["argument_component_classifier"]["minimum_segments"] == 500
    assert contract["argument_component_classifier"]["observed_segments"] == 499
    assert contract["stance_classifier"]["model_id"] == "heuristic-rule-classifier"
    assert contract["coverage"]["required_metric"] == "coverage_percent >= 90.0"
    assert contract["repo_side_contracts"]["satisfied"] is False


def test_track13_residual_external_gates_only_lists_classifier_gates() -> None:
    """Repo-side gaps should stay separate from external training blockers."""
    report = Track13EvidenceReport(
        argument_component_f1=1.0,
        argument_component_segments=4,
        argument_component_model_id="heuristic-rule-detector",
        argument_component_evaluation_source="fixture",
        stance_accuracy=0.9,
        stance_segments=500,
        stance_model_id="nlp-policy-nz/legal-bert-stance",
        stance_evaluation_source="held_out_hansard",
        coverage_percent=50.0,
        aif_jsonld_export=False,
        pipeline_schema_fields=True,
    )

    residual = track13_residual_external_gates(report)

    assert residual == [
        "argument_component_classifier requires Legal-BERT/transformer held-out Hansard F1 >= 0.800 over at least 500 human-labelled segments"
    ]


def test_track13_implementation_status_separates_repo_completion_from_external_gates() -> None:
    """Review handoff should allow repo completion while preserving external blockers."""
    report = Track13EvidenceReport(
        argument_component_f1=1.0,
        argument_component_segments=4,
        argument_component_model_id="heuristic-rule-detector",
        argument_component_evaluation_source="fixture",
        stance_accuracy=1.0,
        stance_segments=6,
        stance_model_id="heuristic-rule-classifier",
        stance_evaluation_source="fixture",
        coverage_percent=94.0,
        aif_jsonld_export=True,
        pipeline_schema_fields=True,
    )

    status = summarize_track13_implementation_status(
        report,
        accepted_silver_labels=0,
        disagreement_queue_rows=13,
    )
    contract = track13_implementation_status_contract(status)

    assert status.repo_side_complete
    assert status.review_ready
    assert status.externally_blocked
    assert len(status.external_gates_pending) == 2
    assert contract["repo_side_complete"] is True
    assert contract["review_ready"] is True
    assert contract["externally_blocked"] is True
    assert contract["silver_labels"] == {
        "accepted": 0,
        "disagreement_queue_rows": 13,
        "accepted_as_gold": False,
    }
