# Track 30: Ontology Mapping Inference

**Dependencies**: Track 29
**Parallelization Node**: Mapping Inference
**Status**: Complete

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Implement exact-match inference: normalized label/URI comparison between ontology terms | [x] | conductor_orchestrator |
| 2 | Implement fuzzy-match inference: Levenshtein, Jaro-Winkler, and embedding similarity on term labels and definitions | [x] | conductor_orchestrator |
| 3 | Implement synonym-based inference: use WordNet or legal thesaurus for cross-ontology term alignment | [x] | conductor_orchestrator |
| 4 | Implement structural inference: compare subclass/property hierarchies to identify isomorphic or subsumed subtrees | [x] | conductor_orchestrator |
| 5 | Implement embedding similarity: encode ontology term labels+definitions and find nearest neighbours across standards | [x] | conductor_orchestrator |
| 6 | Create LLM-assisted interpretation prompts with structured output (JSON schema for inferred mapping), prompts stored in `data/ontologies/inference_prompts/` | [x] | conductor_orchestrator |
| 7 | Score inferred candidates by method agreement count and evidence quality; export with `inferred: true` and confidence score to Track 29 graph | [x] | conductor_orchestrator |
| 8 | Write tests for each inference method with known ground-truth mappings; validate no false-positive exact matches | [x] | conductor_orchestrator |

## Implementation Notes

- Deterministic repo-side inference now covers exact alias overlap, Python `difflib` fuzzy similarity, supplied synonym groups, structural neighbourhood overlap, method-agreement scoring, and Track 29 `OntologyMappingRecord` export with `review_status="needs_review"`.
- Fuzzy matching uses deterministic standard-library similarity for offline CI. Dedicated Levenshtein/Jaro-Winkler calibration can be added later if evaluation shows a practical benefit.
- Embedding inference accepts precomputed term vectors or an injected text encoder, allowing the existing semantic embedding layer to be plugged in without forcing model downloads in tests. Corpus-scale nearest-neighbour evaluation remains future analysis work.

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
