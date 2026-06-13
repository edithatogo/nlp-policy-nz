# Track 15: PROV-O Provenance Ontology for Pipeline Traces

**Dependencies**: Track 6, Track 9
**Parallelization Node**: Provenance & Reproducibility
**Status**: Pending

---

## Phase 1: Provenance Recorder Core

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Create `src/nlp_policy_nz/provenance/` module with provenance data structures | [ ] | |
| 1.2 | Implement `ProvenanceRecorder` class capturing pipeline context | [ ] | |
| 1.3 | Implement PROV-O JSON-LD serializer | [ ] | |
| 1.4 | Write tests for recording and serialization | [ ] | |

## Phase 2: Pipeline Integration & Sidecar Files

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Integrate provenance recording into process_legislation() and process_hansard() | [ ] | |
| 2.2 | Implement sidecar `.prov.json` file writer alongside Parquet output | [ ] | |
| 2.3 | Add `provenance` CLI subcommand | [ ] | |
| 2.4 | Write integration tests for sidecar files | [ ] | |

## Phase 3: Zenodo & Documentation

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add provenance metadata to Zenodo deposit payload | [ ] | |
| 3.2 | Update `design.md` with provenance architecture | [ ] | |
| 3.3 | Write tests for Zenodo provenance integration | [ ] | |
| 3.4 | Run full test suite | [ ] | |

## Files to Create/Modify

| File | Action |
|------|--------|
| `src/nlp_policy_nz/provenance/__init__.py` | Create |
| `src/nlp_policy_nz/provenance/recorder.py` | Create |
| `src/nlp_policy_nz/provenance/serializer.py` | Create |
| `src/nlp_policy_nz/cli/main.py` | Modify |
| `src/nlp_policy_nz/api.py` | Modify |
| `src/nlp_policy_nz/integrations/zenodo_archive.py` | Modify |
| `tests/test_provenance.py` | Create |
