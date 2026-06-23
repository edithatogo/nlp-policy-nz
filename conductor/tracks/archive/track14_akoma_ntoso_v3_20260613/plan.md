# Track 14: Akoma-Ntoso v3 Schema Compliance & Enrichment

**Dependencies**: Track 4
**Parallelization Node**: Schema Standards Compliance
**Status**: Complete

---

## Phase 1: Schema Research & Validator

**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Download OASIS AKN v3 XSD schemas | [x] | codex_gpt5_engineer |
| 1.2 | Create AKN XML validation utility | [x] | codex_gpt5_engineer |
| 1.3 | Audit existing emitter against v3 | [x] | codex_gpt5_engineer |
| 1.4 | Write schema validation tests | [x] | codex_gpt5_engineer |

## Phase 2: FRBR & Document Types

**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Implement full FRBR hierarchy (4 levels) | [x] | codex_gpt5_engineer |
| 2.2 | Add amendment, judgment, bill, debate emitters | [x] | codex_gpt5_engineer |
| 2.3 | Implement TLCEvent and analysis metadata | [x] | codex_gpt5_engineer |
| 2.4 | Add references metadata for citations | [x] | codex_gpt5_engineer |

## Phase 3: CI Integration

**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add AKN validation to CI pipeline | [x] | codex_gpt5_engineer |
| 3.2 | Create AKN output examples | [x] | codex_gpt5_engineer |
| 3.3 | Update design.md | [x] | codex_gpt5_engineer |
| 3.4 | Run full test suite | [x] | codex_gpt5_engineer |

## Files

| File | Action |
|------|--------|
| `src/nlp_policy_nz/schema/__init__.py` | Create |
| `src/nlp_policy_nz/schema/akn_v3.py` | Create |
| `src/nlp_policy_nz/universal_framework_v4.py` | Create |
| `tests/test_akn_v3.py` | Create |

## Implementation Audit

- Added `src/nlp_policy_nz/schema/akn_v3.py` with XSD-backed validation, schema provenance, FRBR Work/Expression/Manifestation/Item emission, lifecycle, references, and analysis metadata.
- Added `src/nlp_policy_nz/universal_framework_v4.py` so AKN v3 support is opt-in and does not alter the v3 framework API.
- Added checked-in examples under `examples/akn/` and a dedicated CI test step for `tests/test_akn_v3.py`.
- Validation evidence: on 2026-06-22, focused Track 14 pytest passed (`7 passed`), targeted Ruff passed on Track 14 Python files, all four emitters validated against the live OASIS AKN v3 XSD (`bill`, `amendment`, `judgment`, `debate`: valid), and the full test suite passed with `--basetemp C:\tmp\nlp-policy-nz-track14-xsd-full` (`550 passed, 1 skipped, 2 warnings`).
