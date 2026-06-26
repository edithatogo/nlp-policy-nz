# Track 27: Rules-as-Code Semantic Bridge

**Dependencies**: Tracks 25-26
**Parallelization Node**: Rules-as-Code Bridge
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Inventory existing source anchoring (Act citation extraction), norm semantics (deontic modality), temporal validity, and OpenFisca/PolicyEngine prototype emitters from Tracks 10, 11, 27 | [ ] | conductor_orchestrator |
| 2 | Define RaC bridge schema connecting source text anchor -> norm statement -> temporal scope -> jurisdiction -> provenance | [ ] | conductor_orchestrator |
| 3 | Create `src/nlp_policy_nz/ontology/rac_bridge.py` with source anchoring, norm extraction, and temporal validity composition | [ ] | conductor_orchestrator |
| 4 | Add OpenFisca/PolicyEngine model stub: read NZ Act parameters and emit deployable rule package skeleton | [ ] | conductor_orchestrator |
| 5 | Integrate with PROV-O provenance recorder from Track 15 for rule authorship chain | [ ] | conductor_orchestrator |
| 6 | Add linked-data discoverability: schema.org/Legislation JSON-LD export for each RaC rule | [ ] | conductor_orchestrator |
| 7 | Write tests for anchor->norm->temporal round-trip and provenance tracing | [ ] | conductor_orchestrator |
| 8 | Add CLI command `nlp-policy-nz rac-export` that emits the full RaC bridge as JSON-LD | [ ] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
