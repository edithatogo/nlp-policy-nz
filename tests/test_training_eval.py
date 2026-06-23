"""Tests for Track 20 training evaluation and trainer scaffolding."""

from __future__ import annotations

from nlp_policy_nz.training.eval import (
    classification_prf,
    exact_match,
    maori_token_integrity,
    token_f1,
)
from nlp_policy_nz.training.run_qlora import main as qlora_main
from nlp_policy_nz.training.trainers import (
    ModelTrainingConfig,
    QLoRAConfig,
    TrainingJobSpec,
    create_legal_bert_mlm_job,
    create_qlora_job,
)


def test_classification_prf_reports_macro_scores() -> None:
    """Classification metrics include macro precision/recall/F1."""
    metrics = classification_prf(
        predictions=["obligation", "permission", "obligation"],
        references=["obligation", "permission", "prohibition"],
    )

    assert round(metrics["accuracy"], 3) == 0.667
    assert 0 < metrics["macro_f1"] < 1


def test_token_f1_handles_overlap_and_empty_inputs() -> None:
    """Token-level F1 handles normal and empty predictions."""
    assert token_f1(["section", "7"], ["section", "7", "Act"]) > 0
    assert token_f1([], ["section"]) == 0.0
    assert token_f1([], []) == 1.0


def test_exact_match_is_case_and_space_normalized() -> None:
    """QA exact match normalizes casing and repeated whitespace."""
    assert exact_match("  Section   7 ", "section 7") == 1.0
    assert exact_match("Section 8", "section 7") == 0.0


def test_maori_token_integrity_scores_unsplit_terms() -> None:
    """Māori token integrity rewards terms that remain as single tokens."""
    tokenized = [["Ko", "Aotearoa", "tēnei"], ["Te", "Tiriti"]]
    assert maori_token_integrity(["Aotearoa", "Te Tiriti"], tokenized) == 0.5


def test_legal_bert_job_uses_track20_defaults() -> None:
    """Legal-BERT MLM job captures Track 20 default hyperparameters."""
    job = create_legal_bert_mlm_job(output_dir="models/legal-bert-nz")

    assert isinstance(job, TrainingJobSpec)
    assert job.task == "mlm"
    assert job.model.model_name == "nlpaueb/legal-bert-base-uncased"
    assert job.training.learning_rate == 2e-5
    assert job.training.per_device_batch_size == 32
    assert job.hub_model_id == "nlp-policy-nz/legal-bert-nz"


def test_qlora_job_records_adapter_and_quantization_settings() -> None:
    """QLoRA jobs preserve model, task, rank, and target module settings."""
    job = create_qlora_job(
        model_name="google/gemma-3-9b",
        task="citation",
        output_dir="models/gemma-citation",
        hub_model_id="nlp-policy-nz/gemma-citation",
        qlora=QLoRAConfig(rank=16, target_modules=("q_proj", "v_proj")),
    )

    assert job.task == "citation"
    assert job.model.model_name == "google/gemma-3-9b"
    assert job.qlora is not None
    assert job.qlora.load_in_4bit is True
    assert job.qlora.rank == 16
    assert job.qlora.target_modules == ("q_proj", "v_proj")


def test_training_job_to_dict_is_json_ready() -> None:
    """Job specs serialize into simple JSON-compatible dictionaries."""
    job = TrainingJobSpec(
        task="deontic",
        model=ModelTrainingConfig(model_name="test-model", output_dir="models/test"),
    )

    payload = job.to_dict()

    assert payload["task"] == "deontic"
    assert payload["model"]["model_name"] == "test-model"
    assert payload["qlora"] is None


def test_run_qlora_prints_job_spec(capsys) -> None:
    """QLoRA CLI stub prints a serializable job spec."""
    rc = qlora_main(
        [
            "--model-name",
            "google/gemma-3-9b",
            "--task",
            "citation",
            "--output-dir",
            "models/gemma",
            "--hub-model-id",
            "nlp-policy-nz/gemma",
            "--print-spec",
        ]
    )

    assert rc == 0
    assert '"model_name": "google/gemma-3-9b"' in capsys.readouterr().out
