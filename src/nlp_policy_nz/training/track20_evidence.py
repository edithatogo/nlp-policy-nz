"""Track 20 acceptance evidence helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

MIN_LEGAL_BERT_PERPLEXITY_IMPROVEMENT = 0.0
MIN_TIER2_QLORA_MODELS = 3
MIN_CITATION_F1_IMPROVEMENT = 0.10
MIN_MAORI_TOKEN_INTEGRITY_IMPROVEMENT = 0.15
MIN_PUBLISHED_HUB_MODELS = 1
MIN_COVERAGE_PERCENT = 90.0
MIN_QLORA_JOB_SPECS = 3


@dataclass(frozen=True)
class Track20EvidenceReport:
    """Measured evidence for Track 20 acceptance criteria."""

    training_data_prepared: bool
    task_mix_supported: bool
    legal_bert_job_spec: bool
    qlora_job_specs: int
    cuda_available: bool
    legal_bert_perplexity_improvement: float | None
    tier2_qlora_models_finetuned: int
    citation_f1_improvement: float | None
    maori_token_integrity_improvement: float | None
    published_hub_models: int
    coverage_percent: float


def evaluate_track20_acceptance(report: Track20EvidenceReport) -> dict[str, bool]:
    """Evaluate Track 20 acceptance criteria without overclaiming scaffold evidence."""
    repo_side_contracts = (
        report.training_data_prepared
        and report.task_mix_supported
        and report.legal_bert_job_spec
        and report.qlora_job_specs >= MIN_QLORA_JOB_SPECS
        and report.coverage_percent >= MIN_COVERAGE_PERCENT
    )
    legal_bert_perplexity = (
        report.cuda_available
        and report.legal_bert_perplexity_improvement is not None
        and report.legal_bert_perplexity_improvement > MIN_LEGAL_BERT_PERPLEXITY_IMPROVEMENT
    )
    tier2_qlora_training = (
        report.cuda_available and report.tier2_qlora_models_finetuned >= MIN_TIER2_QLORA_MODELS
    )
    citation_f1 = (
        report.cuda_available
        and report.citation_f1_improvement is not None
        and report.citation_f1_improvement > MIN_CITATION_F1_IMPROVEMENT
    )
    maori_token_integrity = (
        report.cuda_available
        and report.maori_token_integrity_improvement is not None
        and report.maori_token_integrity_improvement > MIN_MAORI_TOKEN_INTEGRITY_IMPROVEMENT
    )
    return {
        "repo_side_contracts": repo_side_contracts,
        "cuda_validation": report.cuda_available,
        "legal_bert_perplexity": legal_bert_perplexity,
        "tier2_qlora_training": tier2_qlora_training,
        "citation_f1_improvement": citation_f1,
        "maori_token_integrity": maori_token_integrity,
        "hub_publication": report.published_hub_models >= MIN_PUBLISHED_HUB_MODELS,
        "coverage": report.coverage_percent >= MIN_COVERAGE_PERCENT,
    }


def track20_acceptance_contract(
    report: Track20EvidenceReport,
) -> dict[str, dict[str, Any]]:
    """Return a JSON-ready Track 20 acceptance contract with stable gate names."""
    status = evaluate_track20_acceptance(report)
    return {
        "repo_side_contracts": {
            "satisfied": status["repo_side_contracts"],
            "required_metric": (
                "training_data_prepared && task_mix_supported && "
                "legal_bert_job_spec && qlora_job_specs >= "
                f"{MIN_QLORA_JOB_SPECS} && coverage"
            ),
            "observed_metric": status["repo_side_contracts"],
            "training_data_prepared": report.training_data_prepared,
            "task_mix_supported": report.task_mix_supported,
            "legal_bert_job_spec": report.legal_bert_job_spec,
            "qlora_job_specs": report.qlora_job_specs,
            "scope": "repo",
        },
        "cuda_validation": {
            "satisfied": status["cuda_validation"],
            "required_metric": "cuda_available == true",
            "observed_metric": report.cuda_available,
            "scope": "external",
        },
        "legal_bert_perplexity": {
            "satisfied": status["legal_bert_perplexity"],
            "required_metric": (
                f"legal_bert_perplexity_improvement > {MIN_LEGAL_BERT_PERPLEXITY_IMPROVEMENT}"
            ),
            "observed_metric": report.legal_bert_perplexity_improvement,
            "requires_cuda": True,
            "scope": "external",
        },
        "tier2_qlora_training": {
            "satisfied": status["tier2_qlora_training"],
            "required_metric": (f"tier2_qlora_models_finetuned >= {MIN_TIER2_QLORA_MODELS}"),
            "observed_metric": report.tier2_qlora_models_finetuned,
            "requires_cuda": True,
            "scope": "external",
        },
        "citation_f1_improvement": {
            "satisfied": status["citation_f1_improvement"],
            "required_metric": (f"citation_f1_improvement > {MIN_CITATION_F1_IMPROVEMENT}"),
            "observed_metric": report.citation_f1_improvement,
            "requires_cuda": True,
            "scope": "external",
        },
        "maori_token_integrity": {
            "satisfied": status["maori_token_integrity"],
            "required_metric": (
                f"maori_token_integrity_improvement > {MIN_MAORI_TOKEN_INTEGRITY_IMPROVEMENT}"
            ),
            "observed_metric": report.maori_token_integrity_improvement,
            "requires_cuda": True,
            "scope": "external",
        },
        "hub_publication": {
            "satisfied": status["hub_publication"],
            "required_metric": f"published_hub_models >= {MIN_PUBLISHED_HUB_MODELS}",
            "observed_metric": report.published_hub_models,
            "scope": "external",
        },
        "coverage": {
            "satisfied": status["coverage"],
            "required_metric": f"coverage_percent >= {MIN_COVERAGE_PERCENT}",
            "observed_metric": report.coverage_percent,
            "scope": "repo",
        },
    }


def track20_residual_external_gates(report: Track20EvidenceReport) -> list[str]:
    """Return pending external training gates without listing repo-side gaps."""
    status = evaluate_track20_acceptance(report)
    residual: list[str] = []
    if not status["cuda_validation"]:
        residual.append("CUDA environment validation is required before training claims")
    if not status["legal_bert_perplexity"]:
        residual.append(
            "Legal-BERT MLM requires measured held-out perplexity improvement "
            "from a completed CUDA-backed run"
        )
    if not status["tier2_qlora_training"]:
        residual.append(
            f"Tier-2 QLoRA requires at least {MIN_TIER2_QLORA_MODELS} completed "
            "CUDA-backed model fine-tunes"
        )
    if not status["citation_f1_improvement"]:
        residual.append(
            "Citation extraction requires measured held-out F1 improvement "
            f"> {MIN_CITATION_F1_IMPROVEMENT:.2f} versus base models"
        )
    if not status["maori_token_integrity"]:
        residual.append(
            "Te Reo Maori token integrity requires measured improvement "
            f"> {MIN_MAORI_TOKEN_INTEGRITY_IMPROVEMENT:.2f}"
        )
    if not status["hub_publication"]:
        residual.append("Hugging Face publication evidence is required for adapted models")
    return residual


def render_track20_evidence_markdown(report: Track20EvidenceReport) -> str:
    """Render a concise Track 20 evidence summary for conductor notes."""
    status = evaluate_track20_acceptance(report)
    lines = [
        "# Track 20 Evidence",
        "",
        "## Acceptance Status",
        "",
    ]
    lines.extend(
        f"- {name}: {'satisfied' if satisfied else 'pending'}" for name, satisfied in status.items()
    )
    lines.extend(
        [
            "",
            "## Measurements",
            "",
            f"- QLoRA job specs: {report.qlora_job_specs}",
            f"- CUDA available: {report.cuda_available}",
            "- Legal-BERT perplexity improvement: "
            f"{_format_optional(report.legal_bert_perplexity_improvement)}",
            f"- Tier-2 QLoRA models fine-tuned: {report.tier2_qlora_models_finetuned}",
            f"- Citation F1 improvement: {_format_optional(report.citation_f1_improvement)}",
            "- Te Reo Maori token integrity improvement: "
            f"{_format_optional(report.maori_token_integrity_improvement)}",
            f"- Published Hugging Face models: {report.published_hub_models}",
            f"- Coverage: {report.coverage_percent:.1f}%",
        ]
    )
    residual = track20_residual_external_gates(report)
    if residual:
        lines.extend(["", "## Residual External Gates", ""])
        lines.extend(f"- {gate}" for gate in residual)
    return "\n".join(lines) + "\n"


def _format_optional(value: float | None) -> str:
    """Format optional metric values without implying missing measurements exist."""
    if value is None:
        return "not measured"
    return f"{value:.3f}"
