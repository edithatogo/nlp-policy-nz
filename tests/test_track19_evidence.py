"""Tests for Track 19 observability evidence reporting."""

from __future__ import annotations

from nlp_policy_nz.telemetry.evidence import (
    Track19EvidenceReport,
    evaluate_track19_acceptance,
    render_track19_evidence_markdown,
    track19_residual_external_gates,
)


def test_repo_side_observability_does_not_satisfy_full_corpus_gates() -> None:
    """Micro-benchmarks and wrappers must not claim full-corpus profiling."""
    report = Track19EvidenceReport(
        spans_for_major_components=True,
        trace_context_propagates=True,
        trace_file_export=True,
        scalene_report_path=None,
        scalene_corpus_bytes=0,
        memray_flamegraph_path=None,
        memray_corpus_bytes=0,
        benchmark_harness=True,
        benchmark_plugin_available=True,
        ci_benchmark_workflow=True,
        coverage_percent=96.0,
    )

    status = evaluate_track19_acceptance(report)

    assert status["repo_side_contracts"]
    assert not status["scalene_full_corpus_profile"]
    assert not status["memray_full_corpus_flamegraph"]
    assert status["benchmark_execution"]


def test_full_corpus_report_satisfies_track19_thresholds() -> None:
    """A full report with generated artifacts should satisfy all gates."""
    report = Track19EvidenceReport(
        spans_for_major_components=True,
        trace_context_propagates=True,
        trace_file_export=True,
        scalene_report_path="docs/profiling/scalene.html",
        scalene_corpus_bytes=1_073_741_824,
        memray_flamegraph_path="docs/profiling/memray-flamegraph.html",
        memray_corpus_bytes=1_073_741_824,
        benchmark_harness=True,
        benchmark_plugin_available=True,
        ci_benchmark_workflow=True,
        coverage_percent=91.0,
    )

    status = evaluate_track19_acceptance(report)

    assert all(status.values())


def test_track19_evidence_markdown_lists_external_gates() -> None:
    """Rendered evidence should preserve the remaining profiling blockers."""
    report = Track19EvidenceReport(
        spans_for_major_components=True,
        trace_context_propagates=True,
        trace_file_export=True,
        scalene_report_path=None,
        scalene_corpus_bytes=0,
        memray_flamegraph_path=None,
        memray_corpus_bytes=0,
        benchmark_harness=True,
        benchmark_plugin_available=True,
        ci_benchmark_workflow=True,
        coverage_percent=96.0,
    )

    markdown = render_track19_evidence_markdown(report)
    residual = track19_residual_external_gates(report)

    assert "repo_side_contracts: satisfied" in markdown
    assert "scalene_full_corpus_profile: pending" in markdown
    assert "memray_full_corpus_flamegraph: pending" in markdown
    assert any("Scalene" in item for item in residual)
    assert any("Memray" in item for item in residual)
