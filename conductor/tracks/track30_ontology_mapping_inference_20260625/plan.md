# Track 30: Ontology Mapping Inference

**Dependencies**: Track 29  
**Parallelization Node**: Mapping Inference  
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Implement exact, normalized, fuzzy, synonym, structural, and vector candidate generation. | [ ] | conductor_orchestrator |
| 2 | Add LLM-assisted interpretation prompts with stored evidence. | [ ] | conductor_orchestrator |
| 3 | Score candidates by method agreement and evidence quality. | [ ] | conductor_orchestrator |
| 4 | Export inferred mappings into the Track 29 graph with inferred status and tests. | [ ] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
