# Track 42 Evidence: Performance Regression CI and Benchmark Baselines

## Implemented artifacts

- `artifacts/baselines/pytest-benchmark.json`: committed baseline derived from Track 19 benchmark evidence.
- `config/benchmark_thresholds.json`: default and per-test slowdown thresholds.
- `scripts/compare_benchmarks.py`: CLI and reusable functions for comparing pytest-benchmark JSON files.
- `.github/workflows/benchmark.yml`: PR benchmark workflow with comparison gate and JSON/HTML report upload.
- `.github/workflows/benchmark-update.yml`: master push and manual baseline update workflow.
- `docs/perf_regression.md`: local and CI workflow documentation.
- `tests/test_track42_performance_regression.py`: comparison, config, and workflow contract tests.
- `tests/test_track42_conductor.py`: conductor registry, metadata, plan/spec, and evidence tests.

## Acceptance evidence

- Baseline benchmark JSON is committed under `artifacts/baselines/`.
- PR benchmark workflow runs pytest-benchmark and invokes `scripts/compare_benchmarks.py`.
- Regression thresholds are configurable in `config/benchmark_thresholds.json` and mirrored in `pyproject.toml`.
- Regressions beyond `10%` fail via the comparison script exit code.
- Master push workflow refreshes `artifacts/baselines/pytest-benchmark.json`.
- HTML comparison report is generated at `.tmp/benchmarks/benchmark-regression.html` and uploaded as a CI artifact.
- Documentation is available in `docs/perf_regression.md`.

## Validation

- `.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track42_performance_regression.py tests\test_track42_conductor.py` passed: 9 tests.
- `.\.venv\Scripts\python.exe -m ruff check scripts\compare_benchmarks.py tests\test_track42_performance_regression.py tests\test_track42_conductor.py` passed.
- `pixi run python -B -m pytest -q tests\benchmarks\test_pipeline_benchmark.py --benchmark-only --benchmark-disable-gc --benchmark-sort=mean --benchmark-json=.tmp\benchmarks\pytest-benchmark-current.json` passed: 1 benchmark passed, 1 non-benchmark contract test skipped by `--benchmark-only`.
- `.\.venv\Scripts\python.exe scripts\compare_benchmarks.py --baseline artifacts\baselines\pytest-benchmark.json --current .tmp\benchmarks\pytest-benchmark-current.json --thresholds config\benchmark_thresholds.json --default-threshold 0.10 --json-report .tmp\benchmarks\benchmark-regression.json --html-report .tmp\benchmarks\benchmark-regression.html` passed with `-28.10%` delta against the committed baseline.
- `.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track42_performance_regression.py tests\test_track42_conductor.py tests\test_quality_infrastructure.py tests\test_track19_evidence.py tests\test_track19_external_gate_manifest.py tests\test_track56_extraction_runtime.py tests\test_track55_56_conductor.py` passed: 24 tests.

## Review and archive validation

- Review fix applied: `scripts/compare_benchmarks.py` now honors `default_threshold` from `config/benchmark_thresholds.json` when no CLI override is supplied.
- `.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track42_performance_regression.py tests\test_track42_conductor.py` passed: 10 tests.
- `.\.venv\Scripts\python.exe -m ruff check scripts\compare_benchmarks.py tests\test_track42_performance_regression.py tests\test_track42_conductor.py` passed.
- `.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track42_performance_regression.py tests\test_track42_conductor.py tests\test_quality_infrastructure.py tests\test_track19_evidence.py tests\test_track19_external_gate_manifest.py tests\test_track56_extraction_runtime.py tests\test_track55_56_conductor.py` passed after archive: 25 tests.
