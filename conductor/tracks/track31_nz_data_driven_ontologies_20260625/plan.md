# Track 31: New Zealand Data-Driven Ontologies

**Dependencies**: Tracks 25-30
**Parallelization Node**: NZ Ontology Induction
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Gather ontology coverage (Track 25), explicit mappings (Track 29), inferred mappings (Track 30), and dataset statistics (Track 32) as input to NZ ontology induction | [ ] | conductor_orchestrator |
| 2 | Define application areas for NZ-specific ontology outputs: Act structure ontology, Hansard debate topic ontology, NZ court hierarchy ontology, Māori legal concept ontology, NZ government agency ontology | [ ] | conductor_orchestrator |
| 3 | Generate candidate classes and properties from corpus evidence: frequent entity types, relationship patterns, temporal periods, jurisdictional markers | [ ] | conductor_orchestrator |
| 4 | Create `src/nlp_policy_nz/ontology/nz_ontologies.py` with NZActOntology, NZHansardOntology, NZCourtOntology generators | [ ] | conductor_orchestrator |
| 5 | Create controlled vocabulary exports: SKOS concept schemes for NZ Act types, Hansard topics, court levels, government agencies | [ ] | conductor_orchestrator |
| 6 | Export NZ ontologies as OWL/Turtle with provenance tracing to source corpus evidence and confidence per class/property | [ ] | conductor_orchestrator |
| 7 | Write tests: ontology consistency, class hierarchy acyclicity, label uniqueness, URI stability, corpus-evidence traceability | [ ] | conductor_orchestrator |
| 8 | Document NZ ontology design decisions in `docs/nz_ontologies.md` | [ ] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
