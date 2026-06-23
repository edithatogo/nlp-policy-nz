# Performance Benchmarks

Track 19 introduces a `pytest-benchmark` harness under `tests/benchmarks`.
The benchmark suite is intentionally lightweight by default: it stubs model
loading and storage writes so CI can track pipeline orchestration regressions
without downloading large models or corpora.

Run locally:

```bash
pytest tests/benchmarks -q
```

Run through Pixi:

```bash
pixi run benchmark
```

Run the same benchmark command used by CI:

```bash
pytest tests/benchmarks -q \
  --benchmark-only \
  --benchmark-disable-gc \
  --benchmark-sort=mean \
  --benchmark-json=.tmp/benchmarks/pytest-benchmark.json
```

## Metrics

- Throughput: processed records per benchmark iteration.
- Latency: pytest-benchmark mean, median, and percentile timing.
- Memory: use `scripts/memray_trace.py` for allocation traces.
- CPU and mixed memory attribution: use `scripts/profile_pipeline.py`.

## Baseline Status

No full-corpus threshold is enforced yet because the 6.5 GB Hansard corpus is
not committed to the repository. The CI workflow runs the micro-benchmark on
pull requests to `master`; full-corpus baselines should be added here after a
controlled local run on the canonical corpus.

Current local validation is dependency-gated: if `pytest-benchmark` is not
installed in the active interpreter, `tests/benchmarks/test_pipeline_benchmark.py`
is skipped. After refreshing dev dependencies, rerun:

```bash
python -m pytest tests/benchmarks -q --benchmark-only --benchmark-disable-gc --benchmark-sort=mean
```

Record the benchmark table and environment details here before treating the
throughput/latency gate as satisfied.

CI uploads `.tmp/benchmarks/pytest-benchmark.json` as the `benchmark-evidence`
artifact. Treat that artifact as micro-benchmark evidence only; it does not
replace Scalene or Memray profiling on a controlled 1 GB or full Hansard corpus.
