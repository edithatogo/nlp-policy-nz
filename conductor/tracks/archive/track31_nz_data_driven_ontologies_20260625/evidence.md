# Track 31 Evidence: New Zealand Data-Driven Ontologies

## Repo-Side Implementation

- Added `src/nlp_policy_nz/ontology/nz_ontologies.py` to build deterministic, reviewable New Zealand ontology candidates from Track 25 coverage evidence and Track 29 mapping records, while recording Track 30 and Track 32 as evidence-boundary inputs.
- Exported checked-in ontology artifacts under `data/ontologies/`: `nz_ontology_candidates.json`, `nz_ontology_candidates.ttl`, `nz_ontology_candidates.jsonld`, and `nz_controlled_vocabularies.json`.
- Added `tests/test_track31_nz_ontologies.py` to validate application-area coverage, evidence traceability, URI stability, hierarchy acyclicity, label uniqueness, RDF parseability, and checked-in artifact synchronization.
- Added `nlp-policy-nz export-nz-ontologies` and top-level lazy package exports for the Track 31 builders and writer.
- Documented the review-bounded ontology design and full-corpus boundary in `docs/nz_ontologies.md`.

## Boundaries

- Track 31 does not claim full-corpus ontology induction until Track 32 produces whole-corpus descriptive statistics.
- Locally induced New Zealand concepts remain `needs_review`; only authoritative external crosswalk concepts are marked `approved`.
- Live publication and authenticated external-source reconciliation remain future work outside this deterministic repo-side layer.

## Closeout Validation

- Fixed a semantic mapping issue so `NZActOntology` no longer carries the Hansard-only `sioc-post-to-akn-debate` mapping ID.
- `pixi run python -m pytest -q tests\test_track31_nz_ontologies.py tests\test_track31_conductor.py tests\test_cli.py` passed: 52 tests.
- `pixi run python -m pytest -q tests\test_track31_nz_ontologies.py tests\test_track31_conductor.py tests\test_track30_mapping_inference.py tests\test_track30_conductor.py tests\test_track29_mapping_graph.py tests\test_track29_conductor.py tests\test_track28_ontology_discovery.py tests\test_track28_conductor.py tests\test_track26_standards_registry.py tests\test_cli.py` passed: 87 tests.
- `pixi run python -m ruff check --no-cache src\nlp_policy_nz\ontology\nz_ontologies.py src\nlp_policy_nz\ontology\__init__.py src\nlp_policy_nz\__init__.py src\nlp_policy_nz\cli\main.py tests\test_track31_nz_ontologies.py tests\test_track31_conductor.py tests\test_cli.py` passed.
- `data/ontologies/nz_ontology_candidates.json` and `data/ontologies/nz_controlled_vocabularies.json` parse as JSON.
- `data/ontologies/nz_ontology_candidates.ttl` and `data/ontologies/nz_ontology_candidates.jsonld` parse as RDF.
- Fresh `write_nz_ontology_artifacts()` output matches checked-in Track 31 artifacts.
- `git diff --check` passed.
