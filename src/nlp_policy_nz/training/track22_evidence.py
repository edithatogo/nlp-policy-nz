"""Track 22 acceptance evidence helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

MIN_DATASET_MANIFESTS = 4
MIN_MODEL_MANIFESTS = 5
MIN_TOOL_MANIFESTS = 2
MIN_DRY_RUN_SCRIPTS = 2


@dataclass(frozen=True)
class Track22EvidenceReport:
    """Evidence for Track 22 Isaacus integration acceptance."""

    dataset_manifests: int
    model_manifests: int
    tool_manifests: int
    normalization_tests_passing: bool
    dry_run_scripts: int
    docs_present: bool
    open_au_corpus_downloaded: bool
    nz_au_corpus_merged: bool
    open_au_llm_finetuned: bool
    kanon_2_evaluated: bool
    nz_mleb_extended: bool
    nz_mleb_baselines_published: bool
    semchunk_evaluated: bool
    blackstone_graph_monitoring: bool


def evaluate_track22_acceptance(report: Track22EvidenceReport) -> dict[str, bool]:
    """Evaluate Track 22 acceptance without overclaiming repo-only scaffolds."""
    repo_side_contracts = (
        report.dataset_manifests >= MIN_DATASET_MANIFESTS
        and report.model_manifests >= MIN_MODEL_MANIFESTS
        and report.tool_manifests >= MIN_TOOL_MANIFESTS
        and report.normalization_tests_passing
        and report.dry_run_scripts >= MIN_DRY_RUN_SCRIPTS
        and report.docs_present
    )
    open_au_corpus_integration = (
        report.open_au_corpus_downloaded
        and report.nz_au_corpus_merged
    )
    return {
        "repo_side_contracts": repo_side_contracts,
        "open_au_corpus_integration": open_au_corpus_integration,
        "au_to_nz_transfer": report.open_au_llm_finetuned,
        "kanon_2_retrieval": report.kanon_2_evaluated,
        "nz_mleb_extension": report.nz_mleb_extended,
        "nz_mleb_publication": report.nz_mleb_baselines_published,
        "semchunk_evaluation": report.semchunk_evaluated,
        "blackstone_graph_monitoring": report.blackstone_graph_monitoring,
    }


def track22_acceptance_contract(
    report: Track22EvidenceReport,
) -> dict[str, dict[str, Any]]:
    """Return a JSON-ready Track 22 acceptance contract with stable gate names."""
    status = evaluate_track22_acceptance(report)
    return {
        "repo_side_contracts": {
            "satisfied": status["repo_side_contracts"],
            "required_metric": (
                f"dataset_manifests >= {MIN_DATASET_MANIFESTS} && "
                f"model_manifests >= {MIN_MODEL_MANIFESTS} && "
                f"tool_manifests >= {MIN_TOOL_MANIFESTS} && "
                "normalization_tests_passing && dry_run_scripts >= "
                f"{MIN_DRY_RUN_SCRIPTS} && docs_present"
            ),
            "observed_metric": status["repo_side_contracts"],
            "dataset_manifests": report.dataset_manifests,
            "model_manifests": report.model_manifests,
            "tool_manifests": report.tool_manifests,
            "normalization_tests_passing": report.normalization_tests_passing,
            "dry_run_scripts": report.dry_run_scripts,
            "docs_present": report.docs_present,
            "scope": "repo",
        },
        "open_au_corpus_integration": {
            "satisfied": status["open_au_corpus_integration"],
            "required_metric": (
                "open_au_corpus_downloaded && nz_au_corpus_merged"
            ),
            "observed_metric": {
                "open_au_corpus_downloaded": report.open_au_corpus_downloaded,
                "nz_au_corpus_merged": report.nz_au_corpus_merged,
            },
            "scope": "external",
        },
        "au_to_nz_transfer": {
            "satisfied": status["au_to_nz_transfer"],
            "required_metric": "open_au_llm_finetuned == true",
            "observed_metric": report.open_au_llm_finetuned,
            "scope": "external",
        },
        "kanon_2_retrieval": {
            "satisfied": status["kanon_2_retrieval"],
            "required_metric": "kanon_2_evaluated == true",
            "observed_metric": report.kanon_2_evaluated,
            "scope": "external",
        },
        "nz_mleb_extension": {
            "satisfied": status["nz_mleb_extension"],
            "required_metric": "nz_mleb_extended == true",
            "observed_metric": report.nz_mleb_extended,
            "scope": "external",
        },
        "nz_mleb_publication": {
            "satisfied": status["nz_mleb_publication"],
            "required_metric": "nz_mleb_baselines_published == true",
            "observed_metric": report.nz_mleb_baselines_published,
            "scope": "external",
        },
        "semchunk_evaluation": {
            "satisfied": status["semchunk_evaluation"],
            "required_metric": "semchunk_evaluated == true",
            "observed_metric": report.semchunk_evaluated,
            "scope": "external",
        },
        "blackstone_graph_monitoring": {
            "satisfied": status["blackstone_graph_monitoring"],
            "required_metric": "blackstone_graph_monitoring == true",
            "observed_metric": report.blackstone_graph_monitoring,
            "scope": "repo",
        },
    }


def track22_residual_external_gates(report: Track22EvidenceReport) -> list[str]:
    """Return pending Track 22 external gates without listing repo-only gaps."""
    status = evaluate_track22_acceptance(report)
    residual: list[str] = []
    if not status["open_au_corpus_integration"]:
        residual.append(
            "Hugging Face Open Australian Legal Corpus must be downloaded, hashed, normalised, "
            "and merged with the NZ corpus"
        )
    if not status["au_to_nz_transfer"]:
        residual.append("Open Australian Legal LLM requires AU-to-NZ fine-tuning evidence")
    if not status["kanon_2_retrieval"]:
        residual.append("Kanon 2 retrieval requires API or air-gapped measured evaluation")
    if not status["nz_mleb_extension"]:
        residual.append("NZ-MLEB requires jurisdiction extension with relevance judgements")
    if not status["nz_mleb_publication"]:
        residual.append("NZ-MLEB baselines require measured publication evidence")
    if not status["semchunk_evaluation"]:
        residual.append("semchunk requires measured comparison against local chunking")
    return residual


def render_track22_evidence_markdown(report: Track22EvidenceReport) -> str:
    """Render a concise Track 22 evidence summary for Conductor notes."""
    status = evaluate_track22_acceptance(report)
    lines = [
        "# Track 22 Evidence",
        "",
        "## Acceptance Status",
        "",
    ]
    lines.extend(
        f"- {name}: {'satisfied' if satisfied else 'pending'}"
        for name, satisfied in status.items()
    )
    lines.extend(
        [
            "",
            "## Measurements",
            "",
            f"- Dataset manifests: {report.dataset_manifests}",
            f"- Model manifests: {report.model_manifests}",
            f"- Tool manifests: {report.tool_manifests}",
            f"- Normalization tests passing: {report.normalization_tests_passing}",
            f"- Dry-run scripts: {report.dry_run_scripts}",
            f"- Docs present: {report.docs_present}",
            f"- Open AU corpus downloaded: {report.open_au_corpus_downloaded}",
            f"- NZ-AU corpus merged: {report.nz_au_corpus_merged}",
            f"- Open AU LLM fine-tuned: {report.open_au_llm_finetuned}",
            f"- Kanon 2 evaluated: {report.kanon_2_evaluated}",
            f"- NZ-MLEB extended: {report.nz_mleb_extended}",
            "- NZ-MLEB baselines published: "
            f"{report.nz_mleb_baselines_published}",
            f"- semchunk evaluated: {report.semchunk_evaluated}",
            f"- Blackstone Graph monitoring: {report.blackstone_graph_monitoring}",
        ]
    )
    residual = track22_residual_external_gates(report)
    if residual:
        lines.extend(["", "## Residual External Gates", ""])
        lines.extend(f"- {gate}" for gate in residual)
    return "\n".join(lines) + "\n"
