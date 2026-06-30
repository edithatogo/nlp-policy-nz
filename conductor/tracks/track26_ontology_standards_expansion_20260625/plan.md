# Track 26: Legislative and Parliamentary Ontology Standards Expansion

**Dependencies**: Track 25
**Parallelization Node**: Standards Implementation
**Status**: Completed

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Create `data/ontologies/standards_registry.schema.json` defining required registry fields and enum constraints | [x] | conductor_orchestrator |
| 2 | Populate registry entries for AKN/LegalDocML, PROV-O, FOAF, SIOC, LKIF, TimeML/OWL-Time, Popolo, schema.org/Legislation, DCAT/DCAT-AP, ELI/ELI-DL, ECLI, EuroVoc/SKOS, CEN MetaLex, USLM, LexML, LegalRuleML, OpenFisca/PolicyEngine | [x] | conductor_orchestrator |
| 3 | For implementable standards: add URI builders, namespace resolvers, or thin parsers in `src/nlp_policy_nz/ontology/standards.py` | [x] | conductor_orchestrator |
| 4 | Add ELI / ELI-DL URI templates and NZ document ID extraction helpers | [x] | conductor_orchestrator |
| 5 | Add ECLI templates for NZ court decision identifiers | [x] | conductor_orchestrator |
| 6 | Add EuroVoc/SKOS concept record builders and load/round-trip helpers | [x] | conductor_orchestrator |
| 7 | Add fixture-level tests for each standards helper and registry validation | [x] | conductor_orchestrator |
| 8 | Add checked-in schema validation contract for `track26_standards_registry.json` | [x] | conductor_orchestrator |

## Implementation Note - 2026-06-29

Repo-side Track 26 closeout is implemented:

- Added/validated `data/ontologies/track26_standards_registry.json`.
- Added `data/ontologies/standards_registry.schema.json`.
- Added deterministic registry and manifest helpers in `src/nlp_policy_nz/ontology/registry.py`.
- Added implementable standard helpers in `src/nlp_policy_nz/ontology/standards.py` for ELI, ELI-DL, ECLI, SKOS/EuroVoc, and schema.org/Legislation.
- Added tests for registry coverage, deterministic manifest writing, schema contract, controlled-concept round trips, and schema.org/Legislation round trips.
- Focused validation passed:
  - `.\.venv\Scripts\python.exe -m pytest tests\test_track25_ontology_coverage.py tests\test_track26_standards_registry.py`
  - `.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\quality\track25_ontology_coverage.py tests\test_track25_ontology_coverage.py tests\test_track26_standards_registry.py`

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
