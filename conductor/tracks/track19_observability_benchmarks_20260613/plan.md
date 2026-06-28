# Track 19: OpenTelemetry Observability & Performance Benchmarks

**Dependencies**: Track 1, Track 6
**Parallelization Node**: Infrastructure & Quality
**Status**: In Progress

---

## Phase 1: OpenTelemetry Instrumentation

**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Add OpenTelemetry SDK deps to pyproject.toml and pixi.toml | [x] | local |
| 1.2 | Create `src/nlp_policy_nz/telemetry/tracer.py` with OTel setup | [x] | local |
| 1.3 | Instrument all pipeline components with spans | [x] | local |
| 1.4 | Implement console and file trace exporters | [x] | local |
| 1.5 | Write tracing instrumentation tests | [x] | local |

## Phase 2: Profiling Suite

**Status**: External Gate

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Create `scripts/profile_pipeline.py` (Scalene runner) | [x] | local |
| 2.2 | Create `scripts/memray_trace.py` (Memray runner) | [x] | local |
| 2.3 | Run baseline profiles on 1GB sample corpus | [ ] | external: corpus/runtime required |
| 2.4 | Document results in `docs/profiling.md` | [x] | local |
| 2.5 | Add machine-readable evidence contracts for full-corpus profiling gates | [x] | local |
| 2.6 | Define JSON profiling evidence-note schema and wrapper outputs | [x] | local |

## Phase 3: Benchmark Harness & CI

**Status**: External Gate

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Create pytest-benchmark test for pipeline throughput | [x] | local |
| 3.2 | Add `.github/workflows/benchmark.yml` | [x] | local |
| 3.3 | Document baselines in `docs/perf.md` | [x] | local |
| 3.4 | Run full test suite and unskipped benchmark pass | [ ] | unskipped benchmark complete; full suite pending |
| 3.5 | Document benchmark skip/runtime gates without claiming full-corpus success | [x] | local |
| 3.6 | Upload benchmark JSON artifact from CI | [x] | local |

## Files

| File | Action |
|------|--------|
| `src/nlp_policy_nz/telemetry/__init__.py` | Create |
| `src/nlp_policy_nz/telemetry/tracer.py` | Create |
| `.github/workflows/benchmark.yml` | Create |
| `scripts/profile_pipeline.py` | Create |
| `scripts/memray_trace.py` | Create |
| `tests/benchmarks/test_pipeline_benchmark.py` | Create |
| `src/nlp_policy_nz/telemetry/evidence.py` | Create |
| `tests/test_track19_evidence.py` | Create |
| `conductor/tracks/track19_observability_benchmarks_20260613/evidence.md` | Create |
| `conductor/tracks/track19_observability_benchmarks_20260613/profiling_evidence.schema.json` | Create |
| `conductor/tracks/track19_observability_benchmarks_20260613/repo_evidence_20260622.json` | Create |

## Implementation Notes

| Date | Agent | Notes | Validation |
|------|-------|-------|------------|
| 2026-06-21 | codex_gpt5_engineer | Added OpenTelemetry dependency declarations, a safe telemetry facade with console and JSONL file exporter support, trace sidecar configuration for legislation/Hansard processing, Scalene and Memray runner scripts, profiling/performance docs, a PR benchmark workflow, and focused telemetry/benchmark tests. | `python -B -m pytest tests\test_telemetry.py tests\benchmarks\test_pipeline_benchmark.py -p no:cacheprovider -q --basetemp C:\tmp\nlp-policy-nz-track19-focused` passed with 8 passed, 1 skipped. Benchmark test skipped locally in the ambient interpreter, but the refreshed Pixi environment now runs the benchmark unskipped. `python -B -m coverage report --data-file=.tmp\coverage\track19c.coverage --include=src\nlp_policy_nz\telemetry\* -m` reported 96% telemetry coverage. Targeted Ruff `F,E9` passed. Profiling runner help commands passed. Remaining: 1GB/full-corpus profile execution and full-suite/benchmark pass after dependencies/corpus are available. |
| 2026-06-22 | codex_gpt5_engineer | Added Track 19 evidence helpers so repo-side telemetry, trace export, benchmark workflow, and coverage can be evaluated separately from external full-corpus profiling and unavailable benchmark-plugin gates. | `python -B -m pytest -p no:cacheprovider -q tests\test_track19_evidence.py tests\test_telemetry.py tests\benchmarks\test_pipeline_benchmark.py --basetemp C:\tmp\nlp-policy-nz-track19-focused` passed with 11 passed, 1 skipped. `python -m ruff check --no-cache src\nlp_policy_nz\telemetry tests\test_track19_evidence.py tests\test_telemetry.py tests\benchmarks\test_pipeline_benchmark.py` passed. |
| 2026-06-22 | codex_gpt5_implementer_b | Added JSON evidence-note emission to Scalene/Memray wrappers, a schema for those notes, CI benchmark JSON artifact upload, and docs that separate wrapper/CI evidence from 1GB or full-corpus profiling claims. Added `repo_evidence_20260622.json` for this repo-side pass. | `python -B -m py_compile scripts\profile_pipeline.py scripts\memray_trace.py` passed. Runner help commands passed. `python -m json.tool conductor\tracks\track19_observability_benchmarks_20260613\profiling_evidence.schema.json > NUL` passed. `python -B -m pytest tests\benchmarks\test_pipeline_benchmark.py -q -p no:cacheprovider` skipped because `pytest-benchmark` is not installed. Residual external gates remain: controlled 1GB/full-corpus Scalene and Memray runs, and full-suite benchmark pass with refreshed dependencies. |

| 2026-06-24 | codex_gpt5_engineer | Added missing Pixi/runtime dependency declarations required by the pipeline benchmark and changed the benchmark to use pytest-managed temp paths. Recorded an unskipped fixture benchmark JSON artifact. | pixi run python -B -m pytest -p no:cacheprovider -q tests\\test_track19_evidence.py tests\\benchmarks\\test_pipeline_benchmark.py --benchmark-json artifacts\\track19\\benchmark_20260624.json --basetemp C:\\tmp\\nlp-track19-final-20260624 passed with 5 passed; mean 189.5545 ms, 5.2755 ops/sec. pixi run python -m ruff check --no-cache tests\\benchmarks\\test_pipeline_benchmark.py passed. Remaining: full-suite validation and 1GB/full-corpus Scalene/Memray runs. |

| 2026-06-29 | codex_gpt5_engineer | Re-ran repo-wide validation under the local venv after fixing the ontology package import surface and resolved the remaining Track 13, Track 22, and Track 25 failures. The full suite now passes and the repo-wide validation artifact is recorded for Track 19. | `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q` passed with 638 passed, 3 skipped in 69.46s; report written to `artifacts/track19/full_suite_validation.json` and `artifacts/track19/full_suite_validation.txt`. |

| 2026-06-29 | codex_gpt5_engineer | Hardened the Scalene and Memray wrapper launchers so they profile the repo CLI through a temporary bootstrap script, fixed the empty resolved-entity context Parquet failure discovered during the sample Scalene rerun, and recorded the resulting evidence note and aborted local attempt on Windows. | `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_storage.py tests\test_track22_script_contracts.py` passed with 20 passed in 21.71s; `.\.venv\Scripts\python.exe -m ruff check --no-cache src\nlp_policy_nz\storage\serialization.py src\nlp_policy_nz\kb\resolver.py tests\test_storage.py` passed; `.\\.venv\\Scripts\\python.exe -m json.tool docs\\profiling\\profile-pipeline-evidence.json > NUL` passed; sample Scalene rerun was aborted on this Windows host before producing a valid HTML report. |
