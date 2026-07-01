# Track 10 Evidence - Deontic Modality and Legal Effect Classification

Track 10 is complete for repo-side deontic modality detection, legal effect classification, and pipeline serialization.

Implemented surfaces:

- `src/nlp_policy_nz/legal/modality.py` defines `DeonticModality`, `ModalityAnnotation`, `DEONTIC_PATTERNS`, the `DeonticModalityDetector` spaCy factory, scope resolution, and `detect_modality`.
- `src/nlp_policy_nz/legal/effects.py` defines LKIF-inspired `LegalEffect` categories and `classify_legal_effect`.
- `src/nlp_policy_nz/legal/__init__.py` exports the legal-layer public API.
- `src/nlp_policy_nz/pipeline_api.py` runs deontic modality detection and legal effect classification in legislation processing.
- `src/nlp_policy_nz/storage/serialization.py` includes `deontic_modality` and `legal_effect` in `PipelineRecord` and Parquet round trips.

Validation evidence:

- `tests/test_modality.py` covers trigger detection, custom pattern configuration, spaCy component registration, token/doc extensions, and scope handling.
- `tests/test_legal_effects.py` covers LKIF-inspired effect classification and fallback behavior.
- `tests/test_storage.py` and related serialization tests cover record/Parquet schema persistence for enriched fields.
- Track 10 plan evidence records focused validation of 67 Track 10 tests, full-suite validation of 433 tests, and 93% coverage over `src/nlp_policy_nz/legal`.
- The Track 10 Conductor contract test verifies this archived track keeps standard `index.md`, `spec.md`, `plan.md`, `metadata.json`, and `evidence.md` artifacts.

External gates:

- Gold-standard legal annotation corpora and expert-reviewed legal-effect labels remain external validation work.
- Rules-as-code execution and formal deontic semantics belong to later rules-as-code and extraction-framework tracks.

