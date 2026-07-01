# Track 31: New Zealand Data-Driven Ontologies

**Dependencies**: Tracks 25-30
**Parallelization Node**: NZ Ontology Induction
**Status**: Complete

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Gather ontology coverage (Track 25), explicit mappings (Track 29), inferred mappings (Track 30), and dataset statistics (Track 32) as input to NZ ontology induction | [x] | conductor_orchestrator |
| 2 | Define application areas for NZ-specific ontology outputs: Act structure ontology, Hansard debate topic ontology, NZ court hierarchy ontology, Māori legal concept ontology, NZ government agency ontology | [x] | conductor_orchestrator |
| 3 | Generate candidate classes and properties from corpus evidence: frequent entity types, relationship patterns, temporal periods, jurisdictional markers | [x] | conductor_orchestrator |
| 4 | Create `src/nlp_policy_nz/ontology/nz_ontologies.py` with NZActOntology, NZHansardOntology, NZCourtOntology generators | [x] | conductor_orchestrator |
| 5 | Create controlled vocabulary exports: SKOS concept schemes for NZ Act types, Hansard topics, court levels, government agencies | [x] | conductor_orchestrator |
| 6 | Export NZ ontologies as OWL/Turtle with provenance tracing to source corpus evidence and confidence per class/property | [x] | conductor_orchestrator |
| 7 | Write tests: ontology consistency, class hierarchy acyclicity, label uniqueness, URI stability, corpus-evidence traceability | [x] | conductor_orchestrator |
| 8 | Document NZ ontology design decisions in `docs/nz_ontologies.md` | [x] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.

## Implementation Note - 2026-07-01

Track 31 is implemented as a deterministic repo-side ontology induction layer:

- `src/nlp_policy_nz/ontology/nz_ontologies.py` builds reviewable NZ ontology
  candidates from Track 25 coverage rows and Track 29 mapping records, while
  recording Track 30 and Track 32 as evidence-boundary inputs.
- `data/ontologies/nz_ontology_candidates.json`, `.ttl`, `.jsonld`, and
  `nz_controlled_vocabularies.json` provide checked-in JSON, RDF, and SKOS
  artifacts.
- `tests/test_track31_nz_ontologies.py` validates application-area coverage,
  evidence traceability, URI stability, hierarchy acyclicity, label uniqueness,
  RDF parseability, and checked-in artifact synchronization.
- `docs/nz_ontologies.md` records the design decisions and boundary: full
  corpus-wide induction remains pending until Track 32 statistics exist.
