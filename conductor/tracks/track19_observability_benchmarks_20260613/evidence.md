# Track 19 Evidence

## Acceptance Status

- otel_spans: satisfied
- trace_context_propagation: satisfied
- trace_file_export: satisfied
- scalene_full_corpus_profile: pending
- memray_full_corpus_flamegraph: pending
- benchmark_execution: pending
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

## Verification

- `python -B -m pytest -p no:cacheprovider -q tests\test_track19_evidence.py tests\test_telemetry.py tests\benchmarks\test_pipeline_benchmark.py --basetemp C:\tmp\nlp-policy-nz-track19-focused` -> 11 passed, 1 skipped.
- `python -m ruff check --no-cache src\nlp_policy_nz\telemetry tests\test_track19_evidence.py tests\test_telemetry.py tests\benchmarks\test_pipeline_benchmark.py` -> passed.

## Residual External Gates

- Generate a Scalene CPU/memory profile over at least 1 GiB of Hansard input.
- Generate a Memray allocation trace and flamegraph over at least 1 GiB of
  Hansard input.
- Run the benchmark harness in an environment where `pytest-benchmark` is
  installed so the benchmark is not skipped.
- Record a full-suite plus benchmark validation pass after dependency refresh.
