# Track 25: Ontology Coverage Audit for Existing Systems

**Dependencies**: Tracks 10-18, 22
**Parallelization Node**: Ontology Discovery & Gap Analysis
**Status**: Completed

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Search all `src/nlp_policy_nz/` modules for ontology-adjacent code: parsers, exporters, mappings, URI builders, SPARQL queries, RDF writers | [x] | conductor_orchestrator |
| 2 | Catalogue each data file in `data/ontologies/` by format, namespace, domain, and upstream standard | [x] | conductor_orchestrator |
| 3 | Map each track (10-18, 22) evidence folder to the ontology family it implements or references | [x] | conductor_orchestrator |
| 4 | Identify the authoritative upstream ontology for each system (AKN, PROV-O, FOAF, SIOC, LKIF, TimeML, Popolo, schema.org, LegalRuleML, OpenFisca, ELI, ECLI, EuroVoc, etc.) | [x] | conductor_orchestrator |
| 5 | Create `data/ontologies/coverage_manifest.json` with per-standard fields: local path, coverage status, upstream standard, blocker type, and notes | [x] | conductor_orchestrator |
| 6 | Create `data/ontologies/data_blocker_register.json` with each blocker's required dataset, source URL, access method, priority, and unblocking criteria | [x] | conductor_orchestrator |
| 7 | Write tests validating coverage manifest and blocker register schemas | [x] | conductor_orchestrator |
| 8 | Generate prioritized implementation backlog feeding Tracks 26-31; cross-reference each task to specific blockers | [x] | conductor_orchestrator |

## Implementation Note - 2026-06-29

Repo-side Track 25 closeout is implemented:

- Added deterministic artifact writer `write_track25_ontology_coverage_artifacts`.
- Materialized `data/ontologies/coverage_manifest.json`.
- Materialized `data/ontologies/data_blocker_register.json`.
- Materialized `data/ontologies/ontology_implementation_backlog.json`.
- Added tests proving generated artifacts match checked-in JSON.
- Focused validation passed:
  - `.\.venv\Scripts\python.exe -m pytest tests\test_track25_ontology_coverage.py tests\test_track26_standards_registry.py`
  - `.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\quality\track25_ontology_coverage.py tests\test_track25_ontology_coverage.py tests\test_track26_standards_registry.py`

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
