# Track 30: Ontology Mapping Inference

**Dependencies**: Track 29
**Parallelization Node**: Mapping Inference
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Implement exact-match inference: normalized label/URI comparison between ontology terms | [ ] | conductor_orchestrator |
| 2 | Implement fuzzy-match inference: Levenshtein, Jaro-Winkler, and embedding similarity on term labels and definitions | [ ] | conductor_orchestrator |
| 3 | Implement synonym-based inference: use WordNet or legal thesaurus for cross-ontology term alignment | [ ] | conductor_orchestrator |
| 4 | Implement structural inference: compare subclass/property hierarchies to identify isomorphic or subsumed subtrees | [ ] | conductor_orchestrator |
| 5 | Implement embedding similarity: encode ontology term labels+definitions and find nearest neighbours across standards | [ ] | conductor_orchestrator |
| 6 | Create LLM-assisted interpretation prompts with structured output (JSON schema for inferred mapping), prompts stored in `data/ontologies/inference_prompts/` | [ ] | conductor_orchestrator |
| 7 | Score inferred candidates by method agreement count and evidence quality; export with `inferred: true` and confidence score to Track 29 graph | [ ] | conductor_orchestrator |
| 8 | Write tests for each inference method with known ground-truth mappings; validate no false-positive exact matches | [ ] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
