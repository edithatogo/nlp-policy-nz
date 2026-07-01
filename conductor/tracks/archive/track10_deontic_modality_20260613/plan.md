# Track 10: Deontic Modality & Legal Effect Classification

**Dependencies**: Track 4, Track 5
**Parallelization Node**: Legal Effect Analysis
**Status**: Complete

---

## Phase 1: Pattern Design & Component Scaffold

**Estimated Effort**: Medium
**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Research NZ legislative modality patterns: analyse 50 NZ Acts for "must", "shall", "may", "must not", "shall not", "need not" usage | [x] | general_coder |
| 1.2 | Create `src/nlp_policy_nz/legal/modality.py` with `DEONTIC_PATTERNS` dictionary and `DeonticModalityDetector` spaCy component | [x] | general_coder |
| 1.3 | Implement modality scope resolution using spaCy dependency tree (identify governed verb/clause) | [x] | codex_gpt55_engineer |
| 1.4 | Write unit tests for pattern matching and scope resolution | [x] | general_coder |

## Phase 2: Legal Effect Classification

**Estimated Effort**: Medium
**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Define `LegalEffect` enum with LKIF categories (obligation, prohibition, permission, power, liability, immunity, disability) | [x] | general_coder |
| 2.2 | Implement rule-based legal effect classifier for legislative sections | [x] | general_coder |
| 2.3 | Add `classify_legal_effect()` to section-level chunking pipeline | [x] | codex_gpt55_engineer |
| 2.4 | Write tests for classification accuracy on annotated NZ legislation | [x] | codex_gpt55_engineer |

## Phase 3: Pipeline Integration

**Estimated Effort**: Low-Medium
**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add `deontic_modality` and `legal_effect` fields to `PipelineRecord` in `storage/serialization.py` | [x] | codex_gpt55_engineer |
| 3.2 | Update `process_legislation()` in `api.py` to run modality detector | [x] | codex_gpt55_engineer |
| 3.3 | Update Parquet schema to include new fields | [x] | codex_gpt55_engineer |
| 3.4 | Run full test suite and fix any regressions | [x] | codex_gpt5_engineer |

## Files to Create/Modify

| File | Action |
|------|--------|
| `src/nlp_policy_nz/legal/__init__.py` | Create |
| `src/nlp_policy_nz/legal/modality.py` | Create |
| `src/nlp_policy_nz/legal/effects.py` | Create |
| `src/nlp_policy_nz/storage/serialization.py` | Modify |
| `src/nlp_policy_nz/api.py` | Modify |
| `tests/test_modality.py` | Create |
| `tests/test_legal_effects.py` | Create |

## Swarm Gate Audit

| Date | Lane | Evidence | Result |
|------|------|----------|--------|
| 2026-06-14 | chrome_operator | Checked `task_plan.md`, `subagents.yaml`, absent `swarm-config.yaml`, `conductor/tracks.md`, `.swarm/prompts/chrome_operator_subdir_swarm.md`, and `.swarm/runs/20260614-190038/manifest.json`. No explicit Chrome/browser-profile approval or Chrome-specific Track 10 task was present. | No local non-gated work for this lane. Track 10 implementation remains for code/validator lanes; Chrome/account work remains gated until specifically approved. |
| 2026-06-14 | architect_oracle | Reviewed codebase state. modality.py partially complete (126 lines — enum, patterns, dataclass exist but no spaCy component class, scope resolution, or extensions). effects.py, tests, pipeline integration not started. Created 8 tasks in swarm task list. | Architecture guidance issued. Handing off to general_coder for implementation, quality_validator for verification. |
| 2026-06-14 | chrome_operator | Rechecked `task_plan.md`, `subagents.yaml`, absent `swarm-config.yaml`, `conductor/tracks.md`, `.swarm/prompts/chrome_operator_subdir_swarm.md`, and `.swarm/runs/20260614-194645/manifest.json`. The latest lane prompt still requires explicit approval for Chrome/browser-profile/account work, and no such approval or Chrome-specific Track 10 task is present. | No local non-gated work remains for this lane. Chrome/account work remains gated; implementation and validation remain assigned to code/validator lanes. |
| 2026-06-14 | general_coder | Implemented `modality.py` (DEONTIC_PATTERNS, DeonticModalityDetector spaCy component, scope resolution), `effects.py` (LegalEffect enum with 7 LKIF categories, classify_legal_effect with rule-based + spaCy fallback), `tests/test_modality.py` (unit tests for detection + scope), `tests/test_legal_effects.py` (unit tests for classification + pipeline integration). Pipeline integration completed by codex_gpt55_engineer: serialization.py updated with deontic_modality + legal_effect fields, pipeline_api.py updated to run detect_modality + classify_legal_effect in process_legislation(). All source files compile and import successfully. Task 3.4 (full verification) remains. | Track 10 implementation complete (Phases 1-3). Remaining: Task 3.4 full test suite verification. Handing off to quality_validator for verification. |
| 2026-06-14 | codex_gpt55_engineer | Repaired concurrent partial writes in `modality.py` and `effects.py`; restored spaCy factory compatibility; added string-normalisation for custom pattern config; verified `tests/test_modality.py tests/test_legal_effects.py` with `python -m pytest -p no:cacheprovider` (67 passed); verified Parquet round-trip and `process_legislation(..., generate_embeddings=False)` with a direct local Python check; verified `python -m ruff check --no-cache tests/test_modality.py tests/test_legal_effects.py src/nlp_policy_nz/legal` (passed). Attempted broader pytest including `tests/test_storage.py`, but pytest `tmp_path` setup/cleanup failed with Windows sandbox permission errors under AppData, `.tmp`, and `C:\tmp`. | Local non-gated Track 10 implementation and focused validation complete. Task 3.4 remains open for full-suite validation in an environment where pytest temp directories are writable; no commit or external gated action performed. |
| 2026-06-21 | codex_gpt5_engineer | Re-ran focused Track 10 validation: `python -m pytest tests\test_modality.py tests\test_legal_effects.py -p no:cacheprovider -q` passed (67 passed). Full-suite validation required escalated temp-directory access and completed with `python -m pytest -p no:cacheprovider -q --basetemp C:\tmp\nlp-policy-nz-pytest-track10`: 413 passed, 20 failed, 1 warning. Remaining failures are outside Track 10, covering Track 18 amendment XML diffing, CLI argument handling/test imports, DigitalNZ raw capture, BeautifulSoup XML parser availability, release tests using missing `pytest.mock`, and server tests expecting patchable module-level symbols. Added a Gradio optional-import guard in `spaces/app.py` so pure helper tests can collect when the UI runtime dependency is absent. | Track 10 focused validation remains green, but Task 3.4 remains open because the full repo suite is still red on non-Track-10 failures. |
| 2026-06-21 | codex_gpt5_engineer | Addressed review blockers. Full-suite validation completed with `python -m pytest -p no:cacheprovider -q --basetemp C:\tmp\nlp-policy-nz-full`: 433 passed, 1 warning. Track 10 focused validation still passes: 67 passed. Track 10 coverage evidence collected with `COVERAGE_FILE=C:\tmp\nlp-policy-nz-track10.coverage python -m pytest tests\test_modality.py tests\test_legal_effects.py --cov=src\nlp_policy_nz\legal --cov-report=term-missing -p no:cacheprovider -q`: total coverage 93%. Track 10 test fixtures now fall back to `spacy.blank("en")` plus sentencizer if `en_core_web_sm` is not installed. | Track 10 Task 3.4 complete; review blockers cleared. |
