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
- Profiling script scaffold is present.
- Track 23 deterministic evidence helpers are present in
  `src/nlp_policy_nz/quality/track23_evidence.py`.
- Dedicated bounded smoke validation is present in `tests/smoke/`.

## Acceptance Status

- repo_side_contracts: satisfied
- full_ruff_strict: pending
- full_typecheck: pending
- coverage_gate: pending
- mutation_ci_gate: satisfied

## Validation Commands

```cmd
python -B -m pytest -p no:cacheprovider -q tests\smoke tests\test_quality_infrastructure.py tests\test_track23_evidence.py tests\test_smoke.py tests\integration tests\e2e
python -m ruff check --no-cache src\nlp_policy_nz\quality src\nlp_policy_nz\training\__init__.py tests\test_track23_evidence.py tests\test_quality_infrastructure.py tests\test_smoke.py tests\smoke tests\integration tests\e2e
python -B -m py_compile src\nlp_policy_nz\quality\track23_evidence.py
python -B -m json.tool conductor\tracks\track23_quality_infrastructure_20260613\metadata.json > nul
```

## Residual Measured Gates

- `ruff check --select ANN,D,TCH,YTT,RET` must pass across the agreed full source scope.
- `basedpyright` strict mode must pass across the agreed full source scope.
- Coverage must be measured and meet the agreed threshold.
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
- `uv build` built both `dist/nlp_policy_nz-0.1.0.tar.gz` and `dist/nlp_policy_nz-0.1.0-py3-none-any.whl` successfully.
- `python -m pip install --force-reinstall --no-deps dist\nlp_policy_nz-0.1.0-py3-none-any.whl` passed.
- `python -m ruff check tests/test_coverage.py pyproject.toml` passed.
- `python -m pytest -q tests/test_coverage.py` passed with 1 test.

## 2026-06-25 full quality gate manifest

Track 23 now has a machine-readable remaining-gate contract at conductor/tracks/track23_quality_infrastructure_20260613/external_gate_manifest.json. It records mutation_ci_gate as satisfied and full_ruff_strict, strict_basedpyright, coverage_threshold, and full_quality_pass as pending until durable artifacts prove them. Focused tests, scoped Ruff runs, scaffold checks, and configuration inspection are not accepted as substitutes for those gates.
