# Track 23: Quality Tooling & Testing Infrastructure Overhaul

**Dependencies**: Track 1 (Environment Setup)
**Parallelization Node**: Infrastructure & Quality
**Status**: In Progress

---

## Goal

Complete the full quality and testing tooling stack for the nlp-policy-nz project. The current state has good foundations but is missing several critical tools and configurations that the project specifies in its tech-stack and workflow documents.

## Gap Analysis

### Testing Pyramid — Current Coverage

```
        ╱  E2E  ╲          ← ❌ Missing
       ╱Integration╲        ← ⚠️ Partial (ad-hoc, no dedicated dir)
      ╱  Smoke  ╲           ← ❌ Missing
     ╱  Unit + Property  ╲  ← ✅ Present (16 files, hypothesis configured)
    ╱   Mutation   ╲        ← ⚠️ mutatest dep listed, config exists, not run in CI
```

### Tooling — Current vs Required

| Tool | Required | Current | Action |
|------|:--------:|:-------:|--------|
| **ruff** | Strict + ANN (annotations) + D (docstrings) + TCH (typing) | Strict-ish but missing ANN/D/TCH/YTT/RET | Upgrade ruff config |
| **mypy/basedpyright** | Strict type checking | ❌ Not configured | Add pyproject.toml config |
| **`ty` module** | Consistent `ty.` pattern for all typing imports | ⚠️ Partial adoption | Standardise `from __future__ import annotations` + `ty.` |
| **`uv` build backend** | `uv_build` for PEP 517 builds | ❌ Using hatchling | Evaluate switching to `uv_build` |
| **Scalene** | CPU/memory profiling | ❌ Not installed | Add dep + profile scripts |
| **Codecov** | Coverage reporting in CI | ❌ Not configured | Add coverage config + CI step |
| **Vale** | Prose linting | ✅ Configured | Verify it runs in CI |
| **Pydantic v2** | For API validation | ❌ Using msgspec | Evaluate; msgspec is faster but pydantic v2 may be needed for FastAPI |
| **Mutatest** | Mutation testing | ⚠️ dep listed, config exists | Wire into CI |
| **Hypothesis** | Property-based tests | ✅ Configured | Expand to cover edge cases |
| **Smoke tests** | Quick startup checks | ❌ Missing | Create test_smoke.py |
| **E2E tests** | Full pipeline end-to-end | ❌ Missing | Create tests/e2e/ |
| **Integration tests** | Cross-module tests | ⚠️ Ad-hoc | Create tests/integration/ |

## Acceptance Criteria

- [ ] Ruff config upgraded to include ANN, D, TCH, YTT, RET rule sets (strict annotations, docstrings, typing)
- [ ] All source files pass `ruff check --select ANN,D,TCH,YTT,RET` (or are explicitly suppressed with `# noqa`)
- [ ] `pyproject.toml` configured with `[tool.basedpyright] strict = true` or `[tool.mypy] strict = true`
- [ ] All source files use consistent `ty.` typing pattern (`from __future__ import annotations` + `import typing as ty`)
- [ ] `uv_build` evaluated as build backend; decision documented
- [ ] Scalene profiling script created and verified
- [ ] Codecov CI step added to `.github/workflows/ci.yml` with coverage config
- [ ] Smoke tests created and passing (`tests/test_smoke.py`)
- [ ] End-to-end tests created (`tests/e2e/test_pipeline_e2e.py`)
- [ ] Integration tests created (`tests/integration/`)
- [ ] Mutation tests wired into CI (optional gate)
- [ ] Pydantic v2 evaluation documented with recommendation

## Repo-Side Evidence Boundary

The 2026-06-22 evidence lane adds deterministic helpers that separate scaffold
presence from measured quality gates. Config files, CI wiring, tests, docs, and
script scaffolds can satisfy `repo_side_contracts`, but they do not
satisfy:

- strict Ruff passing across the agreed full source scope;
- basedpyright strict passing across the agreed full source scope;
- measured coverage meeting the agreed threshold;
- mutation testing producing a recorded passing result.
