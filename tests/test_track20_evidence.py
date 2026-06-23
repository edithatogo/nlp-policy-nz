"""Tests for Track 20 fine-tuning evidence reporting."""

from __future__ import annotations

from nlp_policy_nz.training.track20_evidence import (
    Track20EvidenceReport,
    evaluate_track20_acceptance,
    render_track20_evidence_markdown,
    track20_acceptance_contract,
    track20_residual_external_gates,
)


def test_repo_side_training_scaffold_does_not_satisfy_model_gates() -> None:
    """Serializable job specs must not be treated as completed fine-tunes."""
    report = Track20EvidenceReport(
        training_data_prepared=True,
        task_mix_supported=True,
        legal_bert_job_spec=True,
        qlora_job_specs=5,
        cuda_available=False,
        legal_bert_perplexity_improvement=None,
        tier2_qlora_models_finetuned=0,
        citation_f1_improvement=None,
        maori_token_integrity_improvement=None,
        published_hub_models=0,
        coverage_percent=93.0,
    )

    status = evaluate_track20_acceptance(report)

    assert status["repo_side_contracts"]
    assert not status["legal_bert_perplexity"]
    assert not status["tier2_qlora_training"]
    assert not status["hub_publication"]


def test_measured_training_report_satisfies_track20_thresholds() -> None:
    """Measured fine-tuning evidence should satisfy all Track 20 gates."""
    report = Track20EvidenceReport(
        training_data_prepared=True,
        task_mix_supported=True,
        legal_bert_job_spec=True,
        qlora_job_specs=5,
        cuda_available=True,
        legal_bert_perplexity_improvement=0.08,
        tier2_qlora_models_finetuned=3,
        citation_f1_improvement=0.11,
        maori_token_integrity_improvement=0.16,
        published_hub_models=4,
        coverage_percent=91.0,
    )

    status = evaluate_track20_acceptance(report)

    assert all(status.values())


def test_track20_evidence_markdown_lists_external_training_gates() -> None:
    """Rendered evidence should show CUDA/training/publishing blockers."""
    report = Track20EvidenceReport(
        training_data_prepared=True,
        task_mix_supported=True,
        legal_bert_job_spec=True,
        qlora_job_specs=5,
        cuda_available=False,
        legal_bert_perplexity_improvement=None,
        tier2_qlora_models_finetuned=0,
        citation_f1_improvement=None,
        maori_token_integrity_improvement=None,
        published_hub_models=0,
        coverage_percent=93.0,
    )

    markdown = render_track20_evidence_markdown(report)
    residual = track20_residual_external_gates(report)

    assert "repo_side_contracts: satisfied" in markdown
    assert "legal_bert_perplexity: pending" in markdown
    assert any("CUDA" in item for item in residual)
    assert any("Hugging Face" in item for item in residual)


def test_track20_acceptance_contract_separates_repo_and_external_scopes() -> None:
    """Structured evidence keeps repo-side contracts separate from training gates."""
    report = Track20EvidenceReport(
        training_data_prepared=True,
        task_mix_supported=True,
        legal_bert_job_spec=True,
        qlora_job_specs=5,
        cuda_available=False,
        legal_bert_perplexity_improvement=None,
        tier2_qlora_models_finetuned=0,
        citation_f1_improvement=None,
        maori_token_integrity_improvement=None,
        published_hub_models=0,
        coverage_percent=93.0,
    )

    contract = track20_acceptance_contract(report)

    assert contract["repo_side_contracts"]["scope"] == "repo"
    assert contract["repo_side_contracts"]["satisfied"] is True
    assert contract["tier2_qlora_training"]["scope"] == "external"
    assert contract["tier2_qlora_training"]["satisfied"] is False
    assert contract["tier2_qlora_training"]["requires_cuda"] is True
