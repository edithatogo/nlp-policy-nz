"""Track 23 quality-infrastructure acceptance evidence helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

MIN_CI_QUALITY_STEPS = 5


@dataclass(frozen=True)
class Track23EvidenceReport:
    """Evidence for Track 23 quality-infrastructure acceptance."""

    ruff_strict_configured: bool
    basedpyright_strict_configured: bool
    coverage_configured: bool
    ci_quality_steps: int
    smoke_tests_present: bool
    integration_tests_present: bool
    e2e_tests_present: bool
    property_tests_present: bool
    mutation_config_present: bool
    profiling_script_present: bool
    build_backend_documented: bool
    pydantic_eval_documented: bool
    focused_tests_passing: bool
    full_ruff_strict_passing: bool
    full_typecheck_passing: bool
    coverage_gate_passing: bool
    mutation_ci_gate_enabled: bool


def evaluate_track23_acceptance(report: Track23EvidenceReport) -> dict[str, bool]:
    """Evaluate Track 23 acceptance without overstating full-repo gates."""
    repo_side_contracts = (
        report.ruff_strict_configured
        and report.basedpyright_strict_configured
        and report.coverage_configured
        and report.ci_quality_steps >= MIN_CI_QUALITY_STEPS
        and report.smoke_tests_present
        and report.integration_tests_present
        and report.e2e_tests_present
        and report.property_tests_present
        and report.mutation_config_present
        and report.profiling_script_present
        and report.build_backend_documented
        and report.pydantic_eval_documented
        and report.focused_tests_passing
    )
    return {
        "repo_side_contracts": repo_side_contracts,
        "ruff_strict_config": report.ruff_strict_configured,
        "basedpyright_strict_config": report.basedpyright_strict_configured,
        "testing_pyramid": (
            report.smoke_tests_present
            and report.integration_tests_present
            and report.e2e_tests_present
            and report.property_tests_present
        ),
        "profiling_and_docs": (
            report.profiling_script_present
            and report.build_backend_documented
            and report.pydantic_eval_documented
        ),
        "full_ruff_strict": report.full_ruff_strict_passing,
        "full_typecheck": report.full_typecheck_passing,
        "coverage_gate": report.coverage_gate_passing,
        "mutation_ci_gate": report.mutation_ci_gate_enabled,
    }


def track23_acceptance_contract(
    report: Track23EvidenceReport,
) -> dict[str, dict[str, Any]]:
    """Return a JSON-ready Track 23 acceptance contract with stable gate names."""
    status = evaluate_track23_acceptance(report)
    return {
        "repo_side_contracts": {
            "satisfied": status["repo_side_contracts"],
            "required_metric": (
                "strict config, CI quality steps, testing pyramid, docs, profiling "
                "script, mutation config, and focused tests are present"
            ),
            "observed_metric": status["repo_side_contracts"],
            "ci_quality_steps": report.ci_quality_steps,
            "scope": "repo",
        },
        "full_ruff_strict": {
            "satisfied": status["full_ruff_strict"],
            "required_metric": "full_ruff_strict_passing == true",
            "observed_metric": report.full_ruff_strict_passing,
            "scope": "repo-wide",
        },
        "full_typecheck": {
            "satisfied": status["full_typecheck"],
            "required_metric": "full_typecheck_passing == true",
            "observed_metric": report.full_typecheck_passing,
            "scope": "repo-wide",
        },
        "coverage_gate": {
            "satisfied": status["coverage_gate"],
            "required_metric": "coverage_gate_passing == true",
            "observed_metric": report.coverage_gate_passing,
            "scope": "repo-wide",
        },
        "mutation_ci_gate": {
            "satisfied": status["mutation_ci_gate"],
            "required_metric": "mutation_ci_gate_enabled == true",
            "observed_metric": report.mutation_ci_gate_enabled,
            "scope": "repo-wide",
        },
    }


def track23_residual_external_gates(report: Track23EvidenceReport) -> list[str]:
    """Return residual quality gates that require repo-wide cleanup or CI evidence."""
    status = evaluate_track23_acceptance(report)
    residual: list[str] = []
    if not status["full_ruff_strict"]:
        residual.append("Full-repo strict ruff pass is still required")
    if not status["full_typecheck"]:
        residual.append("Full-repo basedpyright strict pass is still required")
    if not status["coverage_gate"]:
        residual.append("Coverage threshold evidence is still required")
    if not status["mutation_ci_gate"]:
        residual.append("Mutation testing needs a documented optional CI gate")
    return residual


def render_track23_evidence_markdown(report: Track23EvidenceReport) -> str:
    """Render a concise Track 23 evidence summary for Conductor notes."""
    status = evaluate_track23_acceptance(report)
    lines = [
        "# Track 23 Evidence",
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
            f"- CI quality steps: {report.ci_quality_steps}",
            f"- Smoke tests present: {report.smoke_tests_present}",
            f"- Integration tests present: {report.integration_tests_present}",
            f"- E2E tests present: {report.e2e_tests_present}",
            f"- Property tests present: {report.property_tests_present}",
            f"- Focused tests passing: {report.focused_tests_passing}",
            f"- Full ruff strict passing: {report.full_ruff_strict_passing}",
            f"- Full typecheck passing: {report.full_typecheck_passing}",
            f"- Coverage gate passing: {report.coverage_gate_passing}",
            f"- Mutation CI gate enabled: {report.mutation_ci_gate_enabled}",
        ]
    )
    residual = track23_residual_external_gates(report)
    if residual:
        lines.extend(["", "## Residual Quality Gates", ""])
        lines.extend(f"- {gate}" for gate in residual)
    return "\n".join(lines) + "\n"
