# Track 19: OpenTelemetry Observability & Performance Benchmarks

**Dependencies**: Track 1, Track 6
**Parallelization Node**: Infrastructure & Quality
**Status**: Pending

---

## Phase 1: OpenTelemetry Instrumentation

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Add OpenTelemetry SDK deps to pyproject.toml and pixi.toml | [ ] | |
| 1.2 | Create `src/nlp_policy_nz/telemetry/tracer.py` with OTel setup | [ ] | |
| 1.3 | Instrument all pipeline components with spans | [ ] | |
| 1.4 | Implement console and file trace exporters | [ ] | |
| 1.5 | Write tracing instrumentation tests | [ ] | |

## Phase 2: Profiling Suite

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Create `scripts/profile_pipeline.py` (Scalene runner) | [ ] | |
| 2.2 | Create `scripts/memray_trace.py` (Memray runner) | [ ] | |
| 2.3 | Run baseline profiles on 1GB sample corpus | [ ] | |
| 2.4 | Document results in `docs/profiling.md` | [ ] | |

## Phase 3: Benchmark Harness & CI

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Create pytest-benchmark test for pipeline throughput | [ ] | |
| 3.2 | Add `.github/workflows/benchmark.yml` | [ ] | |
| 3.3 | Document baselines in `docs/perf.md` | [ ] | |
| 3.4 | Run full test suite and benchmark pass | [ ] | |

## Files

| File | Action |
|------|--------|
| `src/nlp_policy_nz/telemetry/__init__.py` | Create |
| `src/nlp_policy_nz/telemetry/tracer.py` | Create |
| `.github/workflows/benchmark.yml` | Create |
| `scripts/profile_pipeline.py` | Create |
| `scripts/memray_trace.py` | Create |
| `tests/benchmarks/test_pipeline_benchmark.py` | Create |
