"""Tests for Track 22 Isaacus evidence reporting."""

from __future__ import annotations

from nlp_policy_nz.training.track22_evidence import (
    Track22EvidenceReport,
    evaluate_track22_acceptance,
    render_track22_evidence_markdown,
    track22_acceptance_contract,
    track22_residual_external_gates,
)


def test_repo_side_isaacus_scaffold_does_not_satisfy_external_gates() -> None:
    """Offline manifests and fixtures must not be treated as completed integration."""
    report = Track22EvidenceReport(
        dataset_manifests=4,
        model_manifests=5,
        tool_manifests=2,
        normalization_tests_passing=True,
        dry_run_scripts=2,
        docs_present=True,
        open_au_corpus_downloaded=False,
        nz_au_corpus_merged=False,
        open_au_llm_finetuned=False,
        kanon_2_evaluated=False,
        nz_mleb_extended=False,
        nz_mleb_baselines_published=False,
        semchunk_evaluated=False,
        blackstone_graph_monitoring=True,
        mleb_fixture_queries=3,
        mleb_fixture_schema_valid=True,
    )

    status = evaluate_track22_acceptance(report)
    contract = track22_acceptance_contract(report)
    residual = track22_residual_external_gates(report)
    markdown = render_track22_evidence_markdown(report)

    assert status["repo_side_contracts"] is True
    assert status["open_au_corpus_integration"] is False
    assert status["kanon_2_retrieval"] is False
    assert status["nz_mleb_publication"] is False
    assert contract["repo_side_contracts"]["scope"] == "repo"
    assert contract["repo_side_contracts"]["mleb_fixture_queries"] == 3
    assert contract["open_au_corpus_integration"]["scope"] == "external"
    assert "repo_side_contracts: satisfied" in markdown
    assert "NZ-MLEB fixture schema valid: True" in markdown
    assert any("Hugging Face" in item for item in residual)
    assert any("Kanon 2" in item for item in residual)


def test_repo_side_contract_requires_local_mleb_fixture_schema() -> None:
    """Track 22 repo-side closeout requires a validated local MLEB fixture."""
    report = Track22EvidenceReport(
        dataset_manifests=4,
        model_manifests=5,
        tool_manifests=2,
        normalization_tests_passing=True,
        dry_run_scripts=2,
        docs_present=True,
        open_au_corpus_downloaded=False,
        nz_au_corpus_merged=False,
        open_au_llm_finetuned=False,
        kanon_2_evaluated=False,
        nz_mleb_extended=False,
        nz_mleb_baselines_published=False,
        semchunk_evaluated=False,
        blackstone_graph_monitoring=True,
        mleb_fixture_queries=3,
        mleb_fixture_schema_valid=False,
    )

    assert evaluate_track22_acceptance(report)["repo_side_contracts"] is False


def test_measured_isaacus_integration_satisfies_track22_gates() -> None:
    """Measured external evidence should satisfy Track 22 acceptance."""
    report = Track22EvidenceReport(
        dataset_manifests=4,
        model_manifests=5,
        tool_manifests=2,
        normalization_tests_passing=True,
        dry_run_scripts=2,
        docs_present=True,
        open_au_corpus_downloaded=True,
        nz_au_corpus_merged=True,
        open_au_llm_finetuned=True,
        kanon_2_evaluated=True,
        nz_mleb_extended=True,
        nz_mleb_baselines_published=True,
        semchunk_evaluated=True,
        blackstone_graph_monitoring=True,
        mleb_fixture_queries=3,
        mleb_fixture_schema_valid=True,
    )

    status = evaluate_track22_acceptance(report)

    assert all(status.values())
