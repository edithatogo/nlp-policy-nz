# Track 15: PROV-O Provenance Ontology for Pipeline Traces

**Dependencies**: Track 6, Track 9
**Parallelization Node**: Provenance & Reproducibility
**Status**: Complete

---

## Phase 1: Provenance Recorder Core

**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Create `src/nlp_policy_nz/provenance/` module with provenance data structures | [x] | codex_gpt5_engineer |
| 1.2 | Implement `ProvenanceRecorder` class capturing pipeline context | [x] | codex_gpt5_engineer |
| 1.3 | Implement PROV-O JSON-LD serializer | [x] | codex_gpt5_engineer |
| 1.4 | Write tests for recording and serialization | [x] | codex_gpt5_engineer |

## Phase 2: Pipeline Integration & Sidecar Files

**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Integrate provenance recording into process_legislation() and process_hansard() | [x] | codex_gpt5_engineer |
| 2.2 | Implement sidecar `.prov.json` file writer alongside Parquet output | [x] | codex_gpt5_engineer |
| 2.3 | Add `provenance` CLI subcommand | [x] | codex_gpt5_engineer |
| 2.4 | Write integration tests for sidecar files | [x] | codex_gpt5_engineer |

## Phase 3: Zenodo & Documentation

**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add provenance metadata to Zenodo deposit payload | [x] | codex_gpt5_engineer |
| 3.2 | Update `design.md` with provenance architecture | [x] | codex_gpt5_engineer |
| 3.3 | Write tests for Zenodo provenance integration | [x] | codex_gpt5_engineer |
| 3.4 | Run full test suite | [x] | codex_gpt5_engineer |

## Files to Create/Modify

| File | Action |
|------|--------|
| `src/nlp_policy_nz/provenance/__init__.py` | Create |
| `src/nlp_policy_nz/provenance/recorder.py` | Create |
| `src/nlp_policy_nz/provenance/serializer.py` | Create |
| `src/nlp_policy_nz/cli/main.py` | Modify |
| `src/nlp_policy_nz/pipeline_api.py` | Modify |
| `src/nlp_policy_nz/integrations/release.py` | Modify |
| `src/nlp_policy_nz/integrations/zenodo.py` | Modify |
| `src/nlp_policy_nz/integrations/zenodo_archive.py` | Modify |
| `tests/test_provenance.py` | Create |

## Implementation Audit

- Added `src/nlp_policy_nz/provenance/` with a provenance recorder, sidecar helpers, and PROV-O JSON-LD serializer.
- Integrated `.prov.json` sidecar creation into `process_legislation()` and `process_hansard()`.
- Added `nlp-policy-nz provenance <parquet_path>` to inspect sidecar JSON-LD.
- Added provenance payload inclusion in release archive metadata and Zenodo deposit notes.
- Validation evidence: `tests/test_provenance.py`, `tests/test_release.py`, `tests/test_zenodo_archive.py`, `tests/test_cli.py`, and the full pytest suite passed on 2026-06-21; provenance package coverage was 95%.
- Reverification evidence: on 2026-06-22, focused Track 15 tests passed (`66 passed, 1 warning`) and scoped Ruff passed on provenance, CLI, pipeline, release, Zenodo, and related test files after cleaning test lint issues.
- Review fix evidence: on 2026-06-22, pipeline sidecars now record the loaded embedding model identity and `archive-to-zenodo` forwards sidecar provenance metadata; focused Track 15 tests passed (`68 passed, 1 warning`) and scoped Ruff passed.
