# Track 42: Performance Regression CI & Benchmark Baselines

**Dependencies**: Track 19
**Parallelization Node**: Infrastructure & Quality
**Status**: Planned

## Goal

Automatically detect performance regressions in CI by storing benchmark baselines in git and comparing PR benchmarks against them, ensuring pipeline throughput, memory usage, and latency do not degrade unexpectedly.

## Scope

- Benchmark baseline JSON files stored in `artifacts/baselines/` (committed to git)
- CI workflow step that runs pytest-benchmark on PR and compares vs baseline
- Regression threshold configuration (e.g., >10% slowdown = fail)
- Automatic baseline update on merge to master (via separate workflow)
- Benchmark visualization as CI artifact (HTML report)
- Integration with Track 19 OTel spans for end-to-end latency regression detection

## Acceptance Criteria

- [ ] Baseline benchmark JSON committed to `artifacts/baselines/`
- [ ] CI benchmark step compares PR results against baseline
- [ ] CI fails if any benchmark regresses >10% (configurable per test)
- [ ] Master merge workflow updates baselines automatically
- [ ] HTML benchmark report uploaded as CI artifact
- [ ] Documentation in `docs/perf_regression.md`
