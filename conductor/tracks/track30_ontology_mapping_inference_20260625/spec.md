# Track 30: Ontology Mapping Inference

**Dependencies**: Track 29  
**Parallelization Node**: Mapping Inference  
**Status**: In Progress

## Goal

Create reviewable candidate mappings between ontologies where authoritative mappings do not exist.

## Scope

- Direct lexical matching and normalized matching.
- Fuzzy matching and SKOS label/synonym matching.
- Structural graph similarity and triangulation through third-party ontologies.
- Embedding/vector similarity.
- LLM-assisted interpretation with traceable prompts and reviewer notes.

## Acceptance Criteria

- [x] Candidate mappings include method, evidence, confidence, and review status.
- [x] No inferred mapping is treated as authoritative before review.
- [x] Evaluation fixtures include known positive and negative mapping examples.
- [x] Outputs feed Track 29 as inferred, reviewable graph edges.
