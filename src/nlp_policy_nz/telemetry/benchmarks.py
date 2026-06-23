"""Benchmark evidence contracts for Track 19 validation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkEvidenceContract:
    """Stable metadata for repo-side pipeline benchmark evidence."""

    name: str
    corpus_mode: str
    requires_pytest_benchmark: bool
    uses_full_corpus: bool
    metrics: tuple[str, ...]
    external_gates: tuple[str, ...]


PIPELINE_BENCHMARK_CONTRACT = BenchmarkEvidenceContract(
    name="pipeline.process_legislation.throughput",
    corpus_mode="deterministic-fixture",
    requires_pytest_benchmark=True,
    uses_full_corpus=False,
    metrics=(
        "throughput_docs_per_second",
        "latency_distribution",
        "record_count",
    ),
    external_gates=(
        "pytest-benchmark plugin installed in the active test environment",
        "full Hansard corpus available for non-fixture baseline runs",
    ),
)


__all__ = ["PIPELINE_BENCHMARK_CONTRACT", "BenchmarkEvidenceContract"]
