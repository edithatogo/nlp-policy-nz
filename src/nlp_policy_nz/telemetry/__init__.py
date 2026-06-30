"""OpenTelemetry helpers for the NLP policy pipeline."""

from __future__ import annotations

from nlp_policy_nz.telemetry.benchmarks import (
    PIPELINE_BENCHMARK_CONTRACT,
    BenchmarkEvidenceContract,
)
from nlp_policy_nz.telemetry.evidence import (
    Track19EvidenceReport,
    evaluate_track19_acceptance,
    render_track19_evidence_markdown,
    track19_residual_external_gates,
)
from nlp_policy_nz.telemetry.tracer import (
    TelemetryHandle,
    TraceConfig,
    configure_tracing,
    pipeline_span,
    record_span_exception,
    set_span_attribute,
)

__all__ = [
    "PIPELINE_BENCHMARK_CONTRACT",
    "BenchmarkEvidenceContract",
    "TelemetryHandle",
    "TraceConfig",
    "Track19EvidenceReport",
    "configure_tracing",
    "evaluate_track19_acceptance",
    "pipeline_span",
    "record_span_exception",
    "render_track19_evidence_markdown",
    "set_span_attribute",
    "track19_residual_external_gates",
]
