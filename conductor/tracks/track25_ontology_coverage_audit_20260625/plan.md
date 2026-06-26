# Track 25: Ontology Coverage Audit for Existing Systems

**Dependencies**: Tracks 10-18, 22
**Parallelization Node**: Ontology Discovery & Gap Analysis
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Search all `src/nlp_policy_nz/` modules for ontology-adjacent code: parsers, exporters, mappings, URI builders, SPARQL queries, RDF writers | [ ] | conductor_orchestrator |
| 2 | Catalogue each data file in `data/ontologies/` by format, namespace, domain, and upstream standard | [ ] | conductor_orchestrator |
| 3 | Map each track (10-18, 22) evidence folder to the ontology family it implements or references | [ ] | conductor_orchestrator |
| 4 | Identify the authoritative upstream ontology for each system (AKN, PROV-O, FOAF, SIOC, LKIF, TimeML, Popolo, schema.org, LegalRuleML, OpenFisca, ELI, ECLI, EuroVoc, etc.) | [ ] | conductor_orchestrator |
| 5 | Create `data/ontologies/coverage_manifest.json` with per-standard fields: local path, coverage status (full/partial/missing), upstream URL, blocker type (data/access/knowledge), and notes | [ ] | conductor_orchestrator |
| 6 | Create `data/ontologies/data_blocker_register.json` with each blocker's required dataset, source URL, access method, priority, and unblocking criteria | [ ] | conductor_orchestrator |
| 7 | Write tests validating coverage manifest and blocker register schemas | [ ] | conductor_orchestrator |
| 8 | Generate prioritized implementation backlog feeding Tracks 26-31; cross-reference each task to specific blockers | [ ] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
