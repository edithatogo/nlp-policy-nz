# Track 30 Evidence: Ontology Mapping Inference

## Repo-Side Implementation

- Added `src/nlp_policy_nz/ontology/mapping_inference.py` with deterministic inference helpers for exact normalized alias overlap, `difflib`, Levenshtein, and Jaro-Winkler fuzzy lexical similarity, supplied synonym groups, structural neighbourhood overlap, triangulation through reviewed third-party bridge mappings, embedding-vector cosine similarity, method-agreement scoring, candidate manifests, and optional LLM prompt contracts.
- Added `InferredMappingCandidate.to_mapping_record()` so candidates can feed Track 29 as `OntologyMappingRecord` edges with `review_status="needs_review"` and `inferred=true` provenance notes.
- Added `data/ontologies/inferred_mapping_candidates.json` as a checked-in review queue generated from deterministic Track 30 fixtures.
- Added `data/ontologies/inference_prompts/mapping_interpretation_prompt.json` as an offline structured-output contract for future LLM-assisted interpretation.
- Added `tests/test_track30_mapping_inference.py` covering positive mappings, negative exact-match behavior, Levenshtein/Jaro-Winkler fuzzy variants, synonym/structural/triangulation evidence, embedding-vector inference, Track 29 export, and artifact round trips.
- Added `tests/test_track30_conductor.py` covering registry state, metadata, evidence links, and checked-in review-only artifacts.

## Boundaries

- Inferred mappings are deliberately non-authoritative until reviewed.
- Fuzzy matching uses deterministic standard-library implementations. Dedicated Levenshtein/Jaro-Winkler libraries can still be adopted later if Track 30 needs externally calibrated edit-distance metrics.
- Embedding inference accepts precomputed vectors or an injected text encoder. Persisted vector artifacts, FAISS/LanceDB nearest-neighbour indexes, and corpus-scale evaluation remain follow-up analysis work.
- LLM-assisted interpretation is represented as a prompt and JSON schema contract only; no live model call is required for offline CI.

## Closeout Validation

- `pixi run python -m pytest -q tests\test_track30_mapping_inference.py tests\test_track30_conductor.py tests\test_track29_mapping_graph.py tests\test_track29_conductor.py` passed: 23 tests.
- `pixi run python -m ruff check --no-cache src\nlp_policy_nz\ontology\mapping_inference.py src\nlp_policy_nz\ontology\__init__.py tests\test_track30_mapping_inference.py` passed.
- Fresh `write_track30_inference_artifacts()` output byte-matches checked-in Track 30 generated artifacts.
- `data/ontologies/inferred_mapping_candidates.json` and `data/ontologies/inference_prompts/mapping_interpretation_prompt.json` parse as JSON.

## Archive Validation

- Track 30 reviewed cleanly after implementation fixes and was archived under `conductor/tracks/archive/track30_ontology_mapping_inference_20260625`.
- `pixi run python -m pytest -q tests\test_track30_mapping_inference.py tests\test_track30_conductor.py tests\test_track29_mapping_graph.py tests\test_track29_conductor.py tests\test_track28_ontology_discovery.py tests\test_track28_conductor.py tests\test_track26_standards_registry.py tests\test_track55_56_conductor.py tests\test_track56_extraction_runtime.py tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_track54_axiom_conductor.py` passed: 64 tests.
- `pixi run python -m ruff check --no-cache ...` passed for the Track 30 ontology, adjacent ontology, extraction, Axiom, and conductor test paths.
- Fresh `write_track30_inference_artifacts()` output still byte-matches checked-in Track 30 artifacts after archiving.
- `git diff --check` passed.
