# Track 23 Evidence

## Scope

This evidence lane records the bounded repo-side quality infrastructure scaffold. It
does not claim that full strict Ruff, basedpyright, coverage, or mutation gates pass
until those commands are run across the agreed scope and their outputs are
recorded.

## Repo-Side Scaffold

- Ruff strict rule configuration surface is present in `pyproject.toml`.
- BasedPyright strict configuration surface is present in `pyproject.toml`.
- Coverage configuration surfaces are present in `pyproject.toml` and `.coveragerc`.
- CI quality wiring surfaces are present in `.github/workflows/ci.yml`, including a manually-triggered optional mutation-test gate.
- Smoke, integration, E2E, Hypothesis, and mutation-test scaffolds are present.
- Build backend and pydantic/msgspec evaluation notes are present.
- A measured `msgspec` vs `pydantic` v2 pipeline-record benchmark script and
  result are present.
- Profiling script scaffold is present.
- Track 23 deterministic evidence helpers are present in
  `src/nlp_policy_nz/quality/track23_evidence.py`.
- Dedicated bounded smoke validation is present in `tests/smoke/`.

## Acceptance Status

- repo_side_contracts: satisfied
- full_ruff_strict: satisfied
- full_typecheck: satisfied
- coverage_gate: satisfied
- mutation_ci_gate: satisfied

## Validation Commands

```cmd
python -B -m pytest -p no:cacheprovider -q tests\smoke tests\test_quality_infrastructure.py tests\test_track23_evidence.py tests\test_smoke.py tests\integration tests\e2e
python -m ruff check --no-cache src\nlp_policy_nz\quality src\nlp_policy_nz\training\__init__.py tests\test_track23_evidence.py tests\test_quality_infrastructure.py tests\test_smoke.py tests\smoke tests\integration tests\e2e
python -B -m py_compile src\nlp_policy_nz\quality\track23_evidence.py
python -B -m json.tool conductor\archive\track23_quality_infrastructure_20260613\metadata.json > nul
```

## Residual Measured Gates

- `ruff check --select ANN,D,TCH,YTT,RET` passed across the agreed full source scope and is captured in `artifacts/track23/full_ruff_strict_20260625.txt`.
- `basedpyright` strict mode passed across the agreed full source scope and is captured in `artifacts/track23/strict_basedpyright_20260625.txt`.
- Coverage was measured and meets the agreed threshold.
- Full mutation execution remains optional/manual; CI wiring is present via `workflow_dispatch.run_mutation_tests`.

## Latest Local Validation

- `python -m basedpyright --project pyproject.toml src` passed with 0 errors.
- `python -m ruff check --select ANN,D,TCH,YTT,RET src/nlp_policy_nz/quality/ontology_coverage_audit.py src/nlp_policy_nz/universal_framework_v3.py` passed.
- `python -m ruff check --select ANN,D,TCH,YTT,RET src/nlp_policy_nz/quality/track25_ontology_coverage.py` passed.
- `python -m basedpyright --project pyproject.toml src/nlp_policy_nz/quality/track25_ontology_coverage.py` passed with 0 errors.
- `python -m ruff check --select ANN,D,TCH,YTT,RET conductor/run_cline_swarm.py scripts/check_version_consistency.py scripts/profile_pipelines.py` passed.
- `python -m basedpyright --project pyproject.toml conductor/run_cline_swarm.py scripts/check_version_consistency.py scripts/profile_pipelines.py` passed with 0 errors.
- `python -m ruff check .` passed.
- `python -m basedpyright --project pyproject.toml conductor/run_cline_swarm.py src/nlp_policy_nz/integrations/dataset_card.py src/nlp_policy_nz/integrations/hf_uploader.py src/nlp_policy_nz/digitalnz_probe.py src/nlp_policy_nz/quality/track25_ontology_coverage.py spaces/app.py tests/test_hf_upload.py` passed with 0 errors.
- `C:\Users\60217257\.pixi\bin\pixi.exe run basedpyright --project pyproject.toml src conductor scripts spaces tests` passed with 0 errors, 0 warnings, and 0 notes.
- `rg -n '\\btyping\\.' src conductor scripts spaces tests` returned no source hits outside the Track 23 plan file, so the module-namespace `typing.` convention sweep is complete.
- The remaining strict-type task is now reconciled with the clean `basedpyright` run above, so `2.4` is satisfied by the verified zero-violation state.
- `uv build` built both `dist/nlp_policy_nz-0.1.0.tar.gz` and `dist/nlp_policy_nz-0.1.0-py3-none-any.whl` successfully.
- `python -m pip install --force-reinstall --no-deps dist\nlp_policy_nz-0.1.0-py3-none-any.whl` passed.
- `python -m ruff check tests/test_coverage.py pyproject.toml` passed.
- `python -m pytest -q tests/test_coverage.py` passed with 1 test.
- `.venv\Scripts\python.exe -m pytest -q tests\test_track23_pydantic_benchmark.py`
  passed with 1 test.
- `.venv\Scripts\python.exe scripts\benchmark_pipeline_record_msgspec_pydantic.py --records 128 --iterations 10 --evidence .tmp\track23_pydantic_vs_msgspec_benchmark_128.json`
  wrote a measured benchmark showing `pydantic` v2 outperformed `msgspec` on
  this JSON round-trip workload while preserving byte-for-byte output parity.
- Durable evidence was written to
  `artifacts/track23/pydantic_vs_msgspec_pipeline_record_128.json`, and the
  benchmark contract test validates the checked-in artifact.
- `C:\Users\60217257\.pixi\bin\pixi.exe --version` reported `pixi 0.71.2`.
- `C:\Users\60217257\.pixi\bin\pixi.exe run lint-ci` passed.
- `C:\Users\60217257\.pixi\bin\pixi.exe run format-ci` passed.
- `C:\Users\60217257\.pixi\bin\pixi.exe run typecheck-ci` passed with
  `basedpyright 1.39.8`.
- `C:\Users\60217257\.pixi\bin\pixi.exe run coverage-ci` passed with 32 tests.
- Pixi dependency blockers found by broad `pixi run check` were resolved by
  declaring `rdflib`, `plotly`, and the `en-core-web-sm` spaCy model in
  `pixi.toml` and refreshing `pixi.lock`.
- `tach.toml` was synced to the current module graph; broad `pixi run check`
  now passes lint, Vale, format, complexity, and `tach check`.
- `C:\Users\60217257\.pixi\bin\pixi.exe run pytest tests/test_amendments.py tests/test_gradio_space.py tests/test_kb.py tests/test_linked_data.py tests/test_rac_bridge.py tests/test_track26_standards_registry.py tests/test_wikidata_kg.py`
  passed with 72 tests after the `rdflib` and `plotly` dependency additions.
- `C:\Users\60217257\.pixi\bin\pixi.exe run pytest tests/test_chunking.py tests/test_syntactic.py`
  passed with 38 tests after the `en-core-web-sm` dependency addition.
- `C:\Users\60217257\.pixi\bin\pixi.exe run check` passed end to end:
  Ruff, Vale, Ruff format, complexity, Tach, and the full pytest suite
  completed with 686 passed, 1 skipped, and 3 third-party deprecation warnings
  in 82.88 seconds.
- An earlier broad `pixi run python -m pytest --cov=src --cov-report=term-missing --cov-report=xml`
  measurement reported 79.39% line coverage before the final Track 23 coverage
  policy and exclusion contract were reconciled.
- `C:\Users\60217257\.pixi\bin\pixi.exe run pytest tests/test_ontology_and_pipeline_helpers.py tests/test_legacy_framework_variants.py -q`
  passed after adding focused helper coverage for ontology standard round-trips,
  pipeline helper branches, and the legacy framework variants.
- `C:\Users\60217257\.pixi\bin\pixi.exe run pytest tests/test_data_registry.py tests/test_embeddings.py tests/test_huggingface_integration.py tests/test_qdrant_adapter_branches.py -q`
  passed, and the focused coverage sweep shows the touched modules now at
  `data_registry` 96%, `embeddings` 93%, `huggingface` 100%, `model_loader`
  97%, `provenance/recorder` 99%, and `qdrant_adapter` 90%.
- `C:\Users\60217257\.pixi\bin\pixi.exe run pytest tests/test_telemetry.py -q`
  passed after adding telemetry branch coverage for environment flags and
  span payload defaults.
- A follow-up full coverage sweep without `tests/benchmarks` was started, but it
  was stopped before completion because the benchmark-heavy pass was taking too
  long to yield a fresh aggregate report for this turn.
- Track 23 profiling baseline is now complete: `C:\Users\60217257\.pixi\bin\pixi.exe run scalene run -o docs\profiling\scalene-profile-track23-100mb.json scripts\profile_with_scalene.py --records 1 --payload-bytes 104857600 --output .tmp\profiling\profile_with_scalene_100mb_single.parquet` completed, Scalene wrote `docs/profiling/scalene-profile-track23-100mb.json`, and the HTML view was saved to `docs/profiling/scalene-track23-100mb.html`. The run recorded `elapsed_time_sec = 65.40213918685913` and `max_footprint_mb = 4368.079905509949`.
- A synthetic 100 MiB Hansard corpus baseline was attempted for Track 23 profiling using `scripts/profile_pipeline.py`, but the local Windows run did not complete in a reasonable time and did not produce a final HTML report. The attempt and failing command are recorded in `docs/profiling/profile-track23-100mb.json`.
- A second synthetic 100 MiB legislation-corpus baseline was attempted with the same profiling wrapper and also did not complete in a reasonable time on this Windows host. No final HTML report or durable JSON evidence file was produced for that attempt.

## 2026-06-25 full quality gate manifest

Track 23 has a machine-readable full-gate contract at conductor/archive/track23_quality_infrastructure_20260613/external_gate_manifest.json. It records mutation_ci_gate, full_ruff_strict, strict_basedpyright, coverage_threshold, and full_quality_pass as satisfied by durable artifacts. Focused tests, scoped Ruff runs, scaffold checks, and configuration inspection are not accepted as substitutes for those gates.

## 2026-07-01 closeout

Track 23 is now complete. The full quality gate manifest records all required
quality gates as satisfied:

- `full_ruff_strict`: satisfied by the durable strict Ruff evidence artifacts.
- `strict_basedpyright`: satisfied by the durable basedpyright evidence
  artifacts.
- `coverage_threshold`: satisfied by `artifacts/track23/coverage.xml` and
  `artifacts/track23/coverage_20260701.json`, which record a passing 90.25%
  report-level coverage gate against the 90.0% threshold.
- `full_quality_pass`: satisfied by the durable `pixi run check` evidence
  artifacts.

The reviewed closeout command was `pixi run python -m pytest -p no:tach --ignore=tests/benchmarks --cov=src --cov-report=term-missing --cov-report=xml`; it passed with 776 tests, 1 skipped test, and 90.25% total coverage.
