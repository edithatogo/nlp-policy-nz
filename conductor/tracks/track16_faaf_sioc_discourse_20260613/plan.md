# Track 16: FOAF & SIOC Ontologies for Parliamentary Discourse

**Dependencies**: Track 7, Track 12
**Parallelization Node**: Semantic Web & Discourse
**Status**: Complete

---

## Phase 1: FOAF Profile Generator

**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Add rdflib dependency to pyproject.toml | [x] | codex_gpt5_engineer |
| 1.2 | Create `src/nlp_policy_nz/linked_data/foaf.py` | [x] | codex_gpt5_engineer |
| 1.3 | Generate FOAF profiles from KB entity data | [x] | codex_gpt5_engineer |
| 1.4 | Write FOAF RDF output tests | [x] | codex_gpt5_engineer |

## Phase 2: SIOC Debate Exporter

**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Create `src/nlp_policy_nz/linked_data/sioc.py` | [x] | codex_gpt5_engineer |
| 2.2 | Implement Hansard-to-SIOC converter | [x] | codex_gpt5_engineer |
| 2.3 | Add RDF/Turtle serialization | [x] | codex_gpt5_engineer |
| 2.4 | Write SIOC RDF tests | [x] | codex_gpt5_engineer |

## Phase 3: CLI & Integration

**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add `export-rdf` CLI subcommand | [x] | codex_gpt5_engineer |
| 3.2 | Implement basic SPARQL query interface | [x] | codex_gpt5_engineer |
| 3.3 | Update design.md with linked data architecture | [x] | codex_gpt5_engineer |
| 3.4 | Run full test suite | [x] | codex_gpt5_engineer |

## Files

| File | Action |
|------|--------|
| `src/nlp_policy_nz/linked_data/__init__.py` | Create |
| `src/nlp_policy_nz/linked_data/foaf.py` | Create |
| `src/nlp_policy_nz/linked_data/sioc.py` | Create |
| `src/nlp_policy_nz/cli/main.py` | Modify |
| `tests/test_linked_data.py` | Create |

## Implementation Audit

- Added `rdflib` as the RDF graph dependency.
- Added `src/nlp_policy_nz/linked_data/` with FOAF profile generation, SIOC Hansard discourse graph generation, Turtle sidecar writing, and SPARQL query helpers.
- Added `export-rdf` and `sparql` CLI subcommands.
- Updated `design.md` with the linked-data architecture.
- Validation evidence: red phase failed on missing `nlp_policy_nz.linked_data`; `tests/test_linked_data.py` passed (`6 passed`); `tests/test_cli.py tests/test_linked_data.py` passed (`42 passed, 1 warning`); Ruff passed for linked-data, CLI, and tests; linked-data package coverage was 96%.
- Full-suite caveat: full pytest could not be completed in this sandbox because pytest-managed `tmp_path` roots under the Windows temp directory and workspace temp override returned `PermissionError`; this also affects existing storage/release/Zenodo tests. One unrelated current dirty-tree failure was observed in `tests/test_provenance.py` from temporal-expression integration, outside Track 16.
