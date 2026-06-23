"""Track 19 observability and benchmark evidence helpers."""

from __future__ import annotations

from dataclasses import dataclass

MIN_FULL_CORPUS_BYTES = 1_073_741_824
MIN_COVERAGE_PERCENT = 90.0


@dataclass(frozen=True)
class Track19EvidenceReport:
    """Measured evidence for Track 19 acceptance criteria."""

    spans_for_major_components: bool
    trace_context_propagates: bool
    trace_file_export: bool
    scalene_report_path: str | None
    scalene_corpus_bytes: int
    memray_flamegraph_path: str | None
    memray_corpus_bytes: int
    benchmark_harness: bool
    benchmark_plugin_available: bool
    ci_benchmark_workflow: bool
    coverage_percent: float


def evaluate_track19_acceptance(report: Track19EvidenceReport) -> dict[str, bool]:
    """Evaluate Track 19 gates without overclaiming local micro-benchmarks."""
    scalene_gate = (
        report.scalene_report_path is not None
        and report.scalene_corpus_bytes >= MIN_FULL_CORPUS_BYTES
    )
    memray_gate = (
        report.memray_flamegraph_path is not None
        and report.memray_corpus_bytes >= MIN_FULL_CORPUS_BYTES
    )
    benchmark_gate = report.benchmark_harness and report.benchmark_plugin_available
    coverage_gate = report.coverage_percent >= MIN_COVERAGE_PERCENT
    repo_side_contracts = (
        report.spans_for_major_components
        and report.trace_context_propagates
        and report.trace_file_export
        and report.benchmark_harness
        and report.ci_benchmark_workflow
        and coverage_gate
    )
    return {
        "otel_spans": report.spans_for_major_components,
        "trace_context_propagation": report.trace_context_propagates,
        "trace_file_export": report.trace_file_export,
        "scalene_full_corpus_profile": scalene_gate,
        "memray_full_corpus_flamegraph": memray_gate,
        "benchmark_execution": benchmark_gate,
        "ci_benchmark_workflow": report.ci_benchmark_workflow,
        "coverage": coverage_gate,
        "repo_side_contracts": repo_side_contracts,
    }


def track19_residual_external_gates(report: Track19EvidenceReport) -> list[str]:
    """Return pending full-corpus and dependency gates."""
    status = evaluate_track19_acceptance(report)
    residual: list[str] = []
    if not status["scalene_full_corpus_profile"]:
        residual.append(
            "Scalene full-corpus profile requires a generated CPU/memory report "
            f"over at least {MIN_FULL_CORPUS_BYTES} input bytes"
        )
    if not status["memray_full_corpus_flamegraph"]:
        residual.append(
            "Memray full-corpus trace requires a generated allocation flamegraph "
            f"over at least {MIN_FULL_CORPUS_BYTES} input bytes"
        )
    if not status["benchmark_execution"]:
        residual.append(
            "Benchmark execution requires pytest-benchmark to be available and "
            "the benchmark harness to run without being skipped"
        )
    return residual


def render_track19_evidence_markdown(report: Track19EvidenceReport) -> str:
    """Render a concise Track 19 evidence summary for conductor notes."""
    status = evaluate_track19_acceptance(report)
    lines = [
        "# Track 19 Evidence",
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
            f"- Scalene corpus bytes: {report.scalene_corpus_bytes}",
            f"- Scalene report: {report.scalene_report_path or 'not generated'}",
            f"- Memray corpus bytes: {report.memray_corpus_bytes}",
            f"- Memray flamegraph: {report.memray_flamegraph_path or 'not generated'}",
            f"- Benchmark plugin available: {report.benchmark_plugin_available}",
            f"- Coverage: {report.coverage_percent:.1f}%",
        ]
    )
    residual = track19_residual_external_gates(report)
    if residual:
        lines.extend(["", "## Residual External Gates", ""])
        lines.extend(f"- {gate}" for gate in residual)
    return "\n".join(lines) + "\n"
