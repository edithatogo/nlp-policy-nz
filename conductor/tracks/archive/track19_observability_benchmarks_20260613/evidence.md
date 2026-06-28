# Track 19 Evidence

## Acceptance Status

- otel_spans: satisfied
- trace_context_propagation: satisfied
- trace_file_export: satisfied
- scalene_full_corpus_profile: roadmap
- memray_full_corpus_flamegraph: roadmap
- benchmark_execution: satisfied
- ci_benchmark_workflow: satisfied
- coverage: satisfied
- repo_side_contracts: satisfied

## Current Repo-Side Evidence

- OpenTelemetry setup degrades safely when SDK imports are unavailable.
- Console and JSONL file exporters are covered by focused tests.
- Pipeline span instrumentation covers major legislation processing stages.
- Profiling wrappers exist for Scalene and Memray.
- PR benchmark workflow exists and calls the benchmark harness.
- `src/nlp_policy_nz/telemetry/evidence.py` prevents local micro-benchmark
  scaffolding from satisfying full-corpus profiling gates.
- A local Windows Scalene sample rerun was attempted against
  `data/samples/sample_legislation.txt`, but the profiler was aborted before it
  could produce a valid HTML report. The 1 GiB gate remains external.

## Verification

- `python -B -m pytest -p no:cacheprovider -q tests\test_track19_evidence.py tests\test_telemetry.py tests\benchmarks\test_pipeline_benchmark.py --basetemp C:\tmp\nlp-policy-nz-track19-focused` -> 11 passed, 1 skipped.
- `python -m ruff check --no-cache src\nlp_policy_nz\telemetry tests\test_track19_evidence.py tests\test_telemetry.py tests\benchmarks\test_pipeline_benchmark.py` -> passed.

- `pixi run python -B -m pytest -p no:cacheprovider -q tests\test_track19_evidence.py tests\benchmarks\test_pipeline_benchmark.py --benchmark-json artifacts\track19\benchmark_20260624.json --basetemp C:\tmp\nlp-track19-final-20260624` -> 5 passed; benchmark mean 189.5545 ms, 5.2755 ops/sec; artifact written to `artifacts/track19/benchmark_20260624.json`.
- `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q` -> 638 passed, 3 skipped; the repo-wide validation pass is now clean and recorded in `artifacts/track19/full_suite_validation.json` and `artifacts/track19/full_suite_validation.txt`.

## External Gate Manifest

- conductor/tracks/track19_observability_benchmarks_20260613/external_gate_manifest.json records the satisfied full-suite gate and the remaining 1 GiB Scalene, 1 GiB Memray, and canonical full-corpus gates as external/runtime evidence requirements. It also records that this repo currently has no 1 GiB Hansard corpus and that Memray is not installed on Windows because the Pixi dependency is platform-gated.

## Residual External Gates

- None remain as active Track 19 gates. The uncompleted profiling pass is
  captured in the product roadmap and can be revisited when the runtime and
  corpus are available.
