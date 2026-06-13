# Track 16: FOAF & SIOC Ontologies for Parliamentary Discourse

**Dependencies**: Track 7, Track 12
**Parallelization Node**: Semantic Web & Discourse
**Status**: Pending

---

## Phase 1: FOAF Profile Generator

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Add rdflib dependency to pyproject.toml | [ ] | |
| 1.2 | Create `src/nlp_policy_nz/linked_data/foaf.py` | [ ] | |
| 1.3 | Generate FOAF profiles from KB entity data | [ ] | |
| 1.4 | Write FOAF RDF output tests | [ ] | |

## Phase 2: SIOC Debate Exporter

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Create `src/nlp_policy_nz/linked_data/sioc.py` | [ ] | |
| 2.2 | Implement Hansard-to-SIOC converter | [ ] | |
| 2.3 | Add RDF/Turtle serialization | [ ] | |
| 2.4 | Write SIOC RDF tests | [ ] | |

## Phase 3: CLI & Integration

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add `export-rdf` CLI subcommand | [ ] | |
| 3.2 | Implement basic SPARQL query interface | [ ] | |
| 3.3 | Update design.md with linked data architecture | [ ] | |
| 3.4 | Run full test suite | [ ] | |

## Files

| File | Action |
|------|--------|
| `src/nlp_policy_nz/linked_data/__init__.py` | Create |
| `src/nlp_policy_nz/linked_data/foaf.py` | Create |
| `src/nlp_policy_nz/linked_data/sioc.py` | Create |
| `src/nlp_policy_nz/cli/main.py` | Modify |
| `tests/test_linked_data.py` | Create |
