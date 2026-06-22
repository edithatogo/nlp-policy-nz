# Track 19: OpenTelemetry Observability & Performance Benchmarks

**Dependencies**: Track 1 (Environment Setup), Track 6 (Storage Layer)
**Parallelization Node**: Infrastructure & Quality
**Status**: In Progress

---

## Goal

Instrument the full pipeline with OpenTelemetry tracing, create a Scalene/Memray profiling suite, and establish performance benchmarks on the full 6.5GB Hansard corpus. Completes the tech-stack observability layer.

## Scope

### Key Deliverables

1. **OpenTelemetry Instrumentation**: Spans, metrics, and logging across all pipeline components (guard, syntactic, semantic, storage, integrations).
2. **Trace Export**: Console and OTLP file exporters, trace sidecar files alongside Parquet outputs.
3. **Profiling Suite**: Scalene CPU/memory profiles and Memray allocation traces on full corpus pipeline.
4. **Benchmark Harness**: Configurable runner measuring throughput (docs/sec), memory peak, latency percentiles.
5. **CI Benchmark Gate**: GitHub Actions workflow running benchmarks and alerting on regressions.

## Standards & Tools

- **OpenTelemetry**: Distributed tracing SDK
- **Scalene**: CPU, GPU, memory profiler
- **Memray**: Memory allocation flamegraphs
- **pytest-benchmark**: Regression detection

## Acceptance Criteria

- [x] OTel spans created for all major pipeline components
- [x] Trace context propagates through entire pipeline
- [ ] Scalene profile produces CPU/memory report on full corpus
- [ ] Memray trace produces allocation flamegraph
- [ ] Benchmark harness reports throughput and latency metrics in an unskipped run
- [x] CI benchmark workflow runs on PRs to master
- [x] Test coverage > 90% for repo-side telemetry surfaces

The unchecked criteria require external/runtime evidence: a local 1GB or
full-corpus Hansard run for Scalene and Memray artifacts, plus a refreshed
environment where `pytest-benchmark` is installed so the benchmark harness runs
instead of skipping.
