# Performance regression gates

Track 42 adds a deterministic CI gate for repo-side performance regressions.
It compares current `pytest-benchmark` output against a committed baseline and
fails pull requests when a benchmark slows down beyond its configured threshold.

## Artifacts

- `artifacts/baselines/pytest-benchmark.json`: committed benchmark baseline.
- `config/benchmark_thresholds.json`: default and per-test slowdown thresholds.
- `scripts/compare_benchmarks.py`: comparison CLI used by CI and local checks.
- `.github/workflows/benchmark.yml`: pull request benchmark gate.
- `.github/workflows/benchmark-update.yml`: master-branch baseline refresh.

## Local usage

Run the benchmark harness:

```bash
pixi run pytest tests/benchmarks -q \
  --benchmark-only \
  --benchmark-disable-gc \
  --benchmark-sort=mean \
  --benchmark-json=.tmp/benchmarks/pytest-benchmark.json
```

Compare against the committed baseline:

```bash
pixi run python scripts/compare_benchmarks.py \
  --baseline artifacts/baselines/pytest-benchmark.json \
  --current .tmp/benchmarks/pytest-benchmark.json \
  --thresholds config/benchmark_thresholds.json \
  --default-threshold 0.10 \
  --json-report .tmp/benchmarks/benchmark-regression.json \
  --html-report .tmp/benchmarks/benchmark-regression.html
```

The command exits with status `1` when a current benchmark is missing or when a
current mean runtime exceeds the baseline mean by more than its threshold.

## CI behavior

Pull requests to `master` run `.github/workflows/benchmark.yml`. The workflow:

- runs the existing benchmark harness;
- compares `.tmp/benchmarks/pytest-benchmark.json` with
  `artifacts/baselines/pytest-benchmark.json`;
- fails on configured regressions; and
- uploads raw benchmark JSON plus JSON and HTML comparison reports.

Pushes to `master` run `.github/workflows/benchmark-update.yml`. The workflow
refreshes `artifacts/baselines/pytest-benchmark.json` from the latest benchmark
run and commits the file only when the generated baseline changes.

## Threshold policy

The default slowdown threshold is `10%`. Per-test overrides live in
`config/benchmark_thresholds.json` and should use full pytest benchmark names,
for example:

```json
{
  "thresholds": {
    "tests/benchmarks/test_pipeline_benchmark.py::test_process_legislation_throughput_benchmark": 0.1
  }
}
```

Lower thresholds are appropriate for stable pure-Python fixture benchmarks.
Higher thresholds are acceptable only when external systems or optional native
libraries make timing noisier, and the reason should be documented in the
threshold file or the relevant track evidence.

## Scope limits

This gate uses repo-side micro-benchmarks. It does not replace Track 19's
full-corpus Scalene or Memray profiling gates. Treat the committed baseline as
a CI regression guard for deterministic fixtures, not as publication evidence
for whole-corpus throughput.
