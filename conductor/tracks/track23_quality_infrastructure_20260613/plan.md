# Track 23: Quality Tooling & Testing Infrastructure Overhaul

**Dependencies**: Track 1
**Parallelization Node**: Infrastructure & Quality
**Status**: Repo-Side Complete; Full Gates Pending

---

## Phase 1: Ruff Strict Mode — Annotations, Docstrings, Typing

**Estimated Effort**: Medium
**Status**: Partially Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Add ANN (annotation), D (docstring), TCH (typing imports), YTT (sys.version checks), RET (return) to ruff lint `select` in pyproject.toml | [x] |  |
| 1.2 | Run `ruff check --fix` across entire codebase; fix auto-fixable issues | [x] | 6d12509 |
| 1.3 | Manually fix remaining ANN/D/TCH/YTT/RET violations (missing return types, missing docstrings, etc.) | [x] | 6d12509 |
| 1.4 | Add `[tool.ruff.lint.per-file-ignores]` for tests (relax ANN in test files) | [x] |  |
| 1.5 | Add `ruff format` check to CI pipeline (currently only `ruff check`) | [x] |  |
| 1.6 | Verify `ruff check .` passes with zero violations | [x] | 6d12509 |

## Phase 2: Strict Typing with `ty` Module Convention

**Estimated Effort**: Medium
**Status**: Partially Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Add `[tool.basedpyright]` or `[tool.mypy]` strict config to pyproject.toml | [x] |  |
| 2.2 | Audit all source files for `from __future__ import annotations` (add where missing) | [ ] | |
| 2.3 | Standardise on `import typing as ty` convention; replace bare `typing.` imports with `ty.` | [ ] | |
| 2.4 | Fix all type annotation violations found by basedpyright/mypy strict mode | [ ] | |
| 2.5 | Add basedpyright/mypy check to CI pipeline | [x] |  |
| 2.6 | Verify strict type checking passes with zero violations | [ ] | |

## Phase 3: Testing Pyramid — Smoke, Integration, E2E

**Estimated Effort**: Medium
**Status**: Partially Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Create `tests/test_smoke.py` — quick checks: spacy loads, imports work, config files parse | [x] |  |
| 3.2 | Create `tests/integration/test_guard_to_syntactic.py` — guard output -> syntactic input round-trip | [x] |  |
| 3.3 | Create `tests/integration/test_pipeline_record_roundtrip.py` — PipelineRecord -> Parquet -> load | [x] |  |
| 3.4 | Create `tests/integration/test_integrations_zenodo.py` — mock Zenodo API wiring | [x] |  |
| 3.5 | Create `tests/e2e/test_pipeline_e2e.py` — full pipeline: sample XML -> process -> Parquet -> search | [x] |  |
| 3.6 | Add hypothesis property-based tests: `test_hypothesis_normalizer.py`, `test_hypothesis_citations.py` | [x] |  |
| 3.7 | Wire mutation tests: configure `mutatest` to run on core modules, add to CI as optional step | [x] |  |

## Phase 4: Build Backend & uv_build Evaluation

**Estimated Effort**: Low
**Status**: Partially Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 4.1 | Research `uv_build` build backend vs current `hatchling`; test `uv build` on current config | [x] | 7255e72 |
| 4.2 | If switching: update `[build-system]` in pyproject.toml to use `uv_build` | [x] | Decision: no switch |
| 4.3 | Verify package builds and installs correctly with new backend | [x] | 7255e72 |
| 4.4 | Document decision in `docs/build_backend.md` | [x] |  |

## Phase 5: Scalene Profiling & Codecov

**Estimated Effort**: Low-Medium
**Status**: Partially Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 5.1 | Add `scalene` to pixi.toml dev dependencies | [x] |  |
| 5.2 | Create `tests/test_coverage.py` marker and `.coveragerc` config for pytest-cov | [x] | 6ea3797 |
| 5.3 | Add Codecov step to `.github/workflows/ci.yml` (after test run) | [x] |  |
| 5.4 | Create `scripts/profile_with_scalene.py` — basic CPU/memory profiling script | [x] |  |
| 5.5 | Run baseline profile on 100MB corpus; document in `docs/profiling.md` | [ ] | |

## Phase 6: Pydantic v2 Evaluation

**Estimated Effort**: Low
**Status**: Partially Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 6.1 | Benchmark msgspec vs pydantic v2 for our PipelineRecord schema (serialization/deserialization speed) | [ ] | |
| 6.2 | Evaluate pydantic v2 for FastAPI server payload validation (currently using raw BaseModel) | [x] |  |
| 6.3 | Document recommendation: keep msgspec for pipeline, optionally add pydantic v2 for API | [x] |  |

## Phase 7: CI Enhancement

**Estimated Effort**: Low-Medium
**Status**: Partially Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 7.1 | Add format check to CI: `ruff format --check .` | [x] |  |
| 7.2 | Add type-check step to CI (basedpyright or mypy) | [x] |  |
| 7.3 | Add coverage + Codecov step | [x] |  |
| 7.4 | Add smoke test step (fast, runs first) | [x] |  |
| 7.5 | Verify `pixi run check` passes on local machine | [ ] | |

## Files to Create/Modify

| File | Action |
|------|--------|
| `pyproject.toml` | Modify (ruff rules, basedpyright/mypy config, coverage config) |
| `pixi.toml` | Modify (scalene dep) |
| `.github/workflows/ci.yml` | Modify (format, type-check, coverage, smoke steps) |
| `.coveragerc` | Create |
| `docs/build_backend.md` | Create |
| `docs/pydantic_vs_msgspec.md` | Create |
| `tests/test_smoke.py` | Create |
| `tests/integration/__init__.py` | Create |
| `tests/integration/test_guard_to_syntactic.py` | Create |
| `tests/integration/test_pipeline_record_roundtrip.py` | Create |
| `tests/e2e/__init__.py` | Create |
| `tests/e2e/test_pipeline_e2e.py` | Create |
| `tests/test_hypothesis_normalizer.py` | Create |
| `tests/test_hypothesis_citations.py` | Create |
| `tests/.mutatest.toml` | Create |
| `scripts/profile_with_scalene.py` | Create |

---

## Implementation Note - 2026-06-22

Bounded repo-side evidence/bookkeeping lane implemented:

- Added deterministic Track 23 evidence contract in
  `src/nlp_policy_nz/quality/track23_evidence.py`.
- Added focused tests in `tests/test_track23_evidence.py` proving repo-side
  config/test scaffolds do not satisfy measured strict Ruff, basedpyright, coverage,
  or mutation gates.
- Added bounded smoke validation in `tests/smoke/`.
- Added `evidence.md` with residual measured gates.

Validation:

- `python -B -m pytest -p no:cacheprovider -q tests\smoke tests\test_quality_infrastructure.py tests\test_track23_evidence.py tests\test_smoke.py tests\integration tests\e2e`
  passed with 29 tests and 2 existing semantic-import SWIG deprecation warnings.
- `python -m ruff check --no-cache src\nlp_policy_nz\quality src\nlp_policy_nz\training\__init__.py tests\test_track23_evidence.py tests\test_quality_infrastructure.py tests\test_smoke.py tests\smoke tests\integration tests\e2e`
  passed.

Repo-side scaffold checkboxes above are now reconciled with the present files. Full-gate checkboxes remain unchecked unless and until the corresponding
full-scope quality command or artifact is actually verified.
