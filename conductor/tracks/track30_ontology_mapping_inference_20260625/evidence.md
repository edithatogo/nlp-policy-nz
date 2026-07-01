# Track 30 Evidence: Ontology Mapping Inference

## Repo-Side Implementation

- Added `src/nlp_policy_nz/ontology/mapping_inference.py` with deterministic inference helpers for exact normalized alias overlap, fuzzy lexical similarity, supplied synonym groups, structural neighbourhood overlap, method-agreement scoring, candidate manifests, and optional LLM prompt contracts.
- Added `InferredMappingCandidate.to_mapping_record()` so candidates can feed Track 29 as `OntologyMappingRecord` edges with `review_status="needs_review"` and `inferred=true` provenance notes.
- Added `data/ontologies/inference_prompts/mapping_interpretation_prompt.json` as an offline structured-output contract for future LLM-assisted interpretation.
- Added `tests/test_track30_mapping_inference.py` covering positive mappings, negative exact-match behavior, synonym/structural evidence, Track 29 export, and artifact round trips.

## Boundaries

- Inferred mappings are deliberately non-authoritative until reviewed.
- Fuzzy matching currently uses deterministic standard-library similarity. Dedicated Levenshtein/Jaro-Winkler libraries can be adopted later if Track 30 needs calibrated edit-distance metrics.
- Embedding nearest-neighbour inference remains open pending a selected model/index, persisted vector artifacts, and corpus-scale evaluation.
- LLM-assisted interpretation is represented as a prompt and JSON schema contract only; no live model call is required for offline CI.
