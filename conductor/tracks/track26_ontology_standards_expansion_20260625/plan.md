# Track 26: Legislative and Parliamentary Ontology Standards Expansion

**Dependencies**: Track 25
**Parallelization Node**: Standards Implementation
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Create `data/ontologies/standards_registry.schema.json` defining fields: standard_id, name, namespace, namespace_prefix, upstream_uri, version, license, authority, local_dir, coverage_status, notes | [ ] | conductor_orchestrator |
| 2 | Populate registry entries for AKN/LegalDocML, PROV-O, FOAF, SIOC, LKIF, TimeML/OWL-Time, Popolo, schema.org/Legislation, DCAT/DCAT-AP, ELI/ELI-DL, ECLI, EuroVoc/SKOS, CEN MetaLex, USLM, LexML, LegalRuleML, OpenFisca/PolicyEngine | [ ] | conductor_orchestrator |
| 3 | For implementable standards: add URI builders, namespace resolvers, or thin parsers in `src/nlp_policy_nz/ontology/standards/` | [ ] | conductor_orchestrator |
| 4 | Create `src/nlp_policy_nz/ontology/standards/eli.py` with ELI URI templates and NZ document ID extraction | [ ] | conductor_orchestrator |
| 5 | Create `src/nlp_policy_nz/ontology/standards/ecli.py` with ECLI templates for NZ court decisions | [ ] | conductor_orchestrator |
| 6 | Create `src/nlp_policy_nz/ontology/standards/eurovoc.py` with SKOS concept lookup fixture | [ ] | conductor_orchestrator |
| 7 | Add fixture-level tests for each standards module and registry validation | [ ] | conductor_orchestrator |
| 8 | Add CI step validating `standards_registry.json` against schema | [ ] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
