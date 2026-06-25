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

## 2026-06-25 full quality gate manifest

Track 23 now has a machine-readable remaining-gate contract at conductor/tracks/track23_quality_infrastructure_20260613/external_gate_manifest.json. It records mutation_ci_gate as satisfied and full_ruff_strict, strict_basedpyright, coverage_threshold, and full_quality_pass as pending until durable artifacts prove them. Focused tests, scoped Ruff runs, scaffold checks, and configuration inspection are not accepted as substitutes for those gates.
