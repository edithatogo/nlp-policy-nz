"""Track 23 quality infrastructure evidence contract tests."""

from __future__ import annotations

from nlp_policy_nz.quality.track23_evidence import (
    Track23EvidenceReport,
    evaluate_track23_acceptance,
    render_track23_evidence_markdown,
    track23_acceptance_contract,
    track23_residual_external_gates,
)


def test_repo_side_contracts_do_not_satisfy_strict_gates() -> None:
    """Config and test scaffolds are separate from measured strict gate results."""
    report = Track23EvidenceReport(
        ruff_strict_configured=True,
        pyright_strict_configured=True,
        coverage_configured=True,
        ci_quality_steps=5,
        smoke_tests_present=True,
        integration_tests_present=True,
        e2e_tests_present=True,
        property_tests_present=True,
        mutation_config_present=True,
        profiling_script_present=True,
        build_backend_documented=True,
        pydantic_eval_documented=True,
        focused_tests_passing=True,
        full_ruff_strict_passing=False,
        full_typecheck_passing=False,
        coverage_gate_passing=False,
        mutation_ci_gate_enabled=False,
    )

    status = evaluate_track23_acceptance(report)
    contract = track23_acceptance_contract(report)

    assert status["repo_side_contracts"] is True
    assert status["full_ruff_strict"] is False
    assert status["full_typecheck"] is False
    assert status["coverage_gate"] is False
    assert contract["repo_side_contracts"]["scope"] == "repo"
    assert contract["full_ruff_strict"]["scope"] == "repo-wide"
    assert contract["coverage_gate"]["observed_metric"] is False


def test_measured_quality_report_satisfies_track23_gates() -> None:
    """A full report requires actual strict tool and coverage results."""
    report = Track23EvidenceReport(
        ruff_strict_configured=True,
        pyright_strict_configured=True,
        coverage_configured=True,
        ci_quality_steps=5,
        smoke_tests_present=True,
        integration_tests_present=True,
        e2e_tests_present=True,
        property_tests_present=True,
        mutation_config_present=True,
        profiling_script_present=True,
        build_backend_documented=True,
        pydantic_eval_documented=True,
        focused_tests_passing=True,
        full_ruff_strict_passing=True,
        full_typecheck_passing=True,
        coverage_gate_passing=True,
        mutation_ci_gate_enabled=True,
    )

    status = evaluate_track23_acceptance(report)

    assert all(status.values())
    assert track23_residual_external_gates(report) == []


def test_track23_evidence_markdown_lists_pending_strict_gates() -> None:
    """Rendered evidence names unresolved strict gate work explicitly."""
    report = Track23EvidenceReport(
        ruff_strict_configured=True,
        pyright_strict_configured=True,
        coverage_configured=True,
        ci_quality_steps=5,
        smoke_tests_present=True,
        integration_tests_present=True,
        e2e_tests_present=True,
        property_tests_present=True,
        mutation_config_present=True,
        profiling_script_present=True,
        build_backend_documented=True,
        pydantic_eval_documented=True,
        focused_tests_passing=True,
        full_ruff_strict_passing=False,
        full_typecheck_passing=False,
        coverage_gate_passing=False,
        mutation_ci_gate_enabled=False,
    )

    markdown = render_track23_evidence_markdown(report)
    residual = track23_residual_external_gates(report)

    assert "- repo_side_contracts: satisfied" in markdown
    assert "- full_ruff_strict: pending" in markdown
    assert any("ruff" in gate for gate in residual)
    assert any("pyright" in gate for gate in residual)
    assert any("Coverage" in gate for gate in residual)
