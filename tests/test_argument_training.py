"""Tests for Track 13 argument/stance training scaffolding."""

from __future__ import annotations

from nlp_policy_nz.storage import PipelineRecord
from nlp_policy_nz.training.data import build_training_examples
from nlp_policy_nz.training.trainers import (
    create_legal_bert_argument_component_job,
    create_legal_bert_stance_job,
)


def test_training_examples_include_gold_argument_and_stance_tasks() -> None:
    """Gold annotated records should produce Track 13 supervised examples."""
    record = PipelineRecord(
        doc_id="hansard-argument-1",
        corpus_source="hansard",
        raw_text="Because rents are rising, the bill should pass.",
        cleaned_tokens=["Because", "rents", "are", "rising"],
        nz_act_citations=[],
        te_reo_terms=[],
        arguments=[
            {
                "component_id": "arg-1-premise",
                "component_type": "premise",
                "text": "Because rents are rising",
                "start": 0,
                "end": 24,
                "confidence": 1.0,
            },
        ],
        argument_label_source="gold",
        stance="pro",
        stance_label_source="gold",
    )

    examples = build_training_examples([record])
    by_task = {example.task: example for example in examples}

    assert by_task["argument"].labels["components"][0]["component_type"] == "premise"
    assert by_task["argument"].metadata["label_source"] == "gold"
    assert by_task["stance"].labels == {"stance": "pro"}
    assert by_task["stance"].metadata["label_source"] == "gold"


def test_training_examples_ignore_predicted_discourse_fields() -> None:
    """Predicted pipeline outputs should not become supervised labels."""
    record = PipelineRecord(
        doc_id="hansard-predicted-1",
        corpus_source="hansard",
        raw_text="Therefore the bill should pass.",
        cleaned_tokens=["Therefore", "the", "bill", "should", "pass"],
        nz_act_citations=[],
        te_reo_terms=[],
        arguments=[{"component_id": "arg-1", "component_type": "conclusion"}],
        stance="pro",
    )

    examples = build_training_examples([record])
    tasks = {example.task for example in examples}

    assert "argument" not in tasks
    assert "stance" not in tasks


def test_track13_legal_bert_job_specs_are_serializable() -> None:
    """Track 13 fine-tuning job specs should be concrete and JSON-ready."""
    argument_job = create_legal_bert_argument_component_job(
        dataset_split_dir="data/track13/argument_components",
        output_dir="models/argument-components",
    )
    stance_job = create_legal_bert_stance_job(
        dataset_split_dir="data/track13/stance",
        output_dir="models/stance",
    )

    assert argument_job.task == "argument"
    assert argument_job.dataset_split_dir == "data/track13/argument_components"
    assert stance_job.task == "stance"
    assert stance_job.model.model_name == "nlpaueb/legal-bert-base-uncased"
    assert stance_job.to_dict()["training"]["learning_rate"] == 2e-5
