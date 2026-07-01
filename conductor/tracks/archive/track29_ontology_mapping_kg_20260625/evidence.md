# Track 29 Evidence: Ontology Mapping Knowledge Graph

## Implemented Artifacts

- `src/nlp_policy_nz/ontology/mapping_graph.py`: mapping record model, immutable CRUD helpers, validation, manifest builder, RDF graph builder, Turtle/JSON-LD serializers, summary generation, Mermaid rendering, and query helpers.
- `src/nlp_policy_nz/ontology/__init__.py`: package-level exports for the Track 29 mapping graph API.
- `data/ontologies/ontology_mappings.json`: canonical explicit mapping manifest.
- `data/ontologies/ontology_mappings.schema.json`: JSON Schema for mapping manifests.
- `data/ontologies/ontology_mappings.ttl`: RDF/Turtle export.
- `data/ontologies/ontology_mappings.jsonld`: JSON-LD export.
- `data/ontologies/ontology_mapping_summary.json`: mapping counts by predicate, standard, and review status.
- `data/ontologies/ontology_mapping_graph.mmd`: standards-level Mermaid mapping graph.
- `docs/ontology_mapping.md`: methodology, artifact inventory, query helper examples, and known gaps.
- `tests/test_track29_mapping_graph.py`: schema, validation, query, export, and artifact round-trip tests.
- `tests/test_track29_conductor.py`: conductor registry, metadata, plan/spec, evidence, and checked-in artifact tests.

## Acceptance Evidence

- Explicit mapping storage includes source and target standards, terms, predicate, confidence, method, provenance, review status, and notes in `ontology_mappings.json`.
- RDF/Turtle and JSON-LD exports are generated from the same manifest and parse with `rdflib`.
- Query helpers include `mappings_by_standard_pair`, `get_equivalent`, and `traverse_mappings`.
- Mapping record maintenance helpers include `add_mapping_record`, `replace_mapping_record`, `remove_mapping_record`, and `update_mapping_review_status`.
- JSON-LD export is canonicalized before writing so repeated artifact generation is stable.
- The visual graph artifact is `ontology_mapping_graph.mmd`.

## Validation

- `.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track29_mapping_graph.py tests\test_track29_conductor.py tests\test_track28_ontology_discovery.py tests\test_track28_conductor.py tests\test_track26_standards_registry.py` passed: 20 tests.
- `.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track29_mapping_graph.py tests\test_track29_conductor.py tests\test_track28_ontology_discovery.py tests\test_track28_conductor.py tests\test_track26_standards_registry.py tests\test_track55_56_conductor.py tests\test_track56_extraction_runtime.py tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py` passed: 57 tests.
- `.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\ontology\mapping_graph.py src\nlp_policy_nz\ontology\__init__.py src\nlp_policy_nz\quality\track28_ontology_discovery.py src\nlp_policy_nz\extraction src\nlp_policy_nz\axiom src\nlp_policy_nz\ontology\rac_bridge.py src\nlp_policy_nz\cli\main.py scripts\benchmark_extraction_manifest_runtime.py tests\test_track29_mapping_graph.py tests\test_track29_conductor.py tests\test_track28_ontology_discovery.py tests\test_track28_conductor.py tests\test_track26_standards_registry.py tests\test_track55_56_conductor.py tests\test_track56_extraction_runtime.py tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py` passed.

## Review and archive validation

- Review fix applied: added immutable mapping-record CRUD helpers and tests to satisfy the original `mapping_graph.py` plan item.
- `.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track29_mapping_graph.py tests\test_track29_conductor.py tests\test_track28_ontology_discovery.py tests\test_track28_conductor.py tests\test_track26_standards_registry.py` passed: 22 tests.
- `.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track29_mapping_graph.py tests\test_track29_conductor.py tests\test_track28_ontology_discovery.py tests\test_track28_conductor.py tests\test_track26_standards_registry.py tests\test_track55_56_conductor.py tests\test_track56_extraction_runtime.py tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py` passed: 59 tests.
- `.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\ontology\mapping_graph.py src\nlp_policy_nz\ontology\__init__.py src\nlp_policy_nz\quality\track28_ontology_discovery.py src\nlp_policy_nz\extraction src\nlp_policy_nz\axiom src\nlp_policy_nz\ontology\rac_bridge.py src\nlp_policy_nz\cli\main.py scripts\benchmark_extraction_manifest_runtime.py tests\test_track29_mapping_graph.py tests\test_track29_conductor.py tests\test_track28_ontology_discovery.py tests\test_track28_conductor.py tests\test_track26_standards_registry.py tests\test_track55_56_conductor.py tests\test_track56_extraction_runtime.py tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py` passed after archive.

## Implementation closeout validation

- Closeout fix applied: canonicalized JSON-LD serialization and added a checked-in artifact drift regression test covering JSON, schema, Turtle, JSON-LD, summary, and Mermaid outputs.
- `pixi run python -m pytest -q tests\test_track29_mapping_graph.py tests\test_track29_conductor.py tests\test_track28_ontology_discovery.py tests\test_track28_conductor.py tests\test_track26_standards_registry.py` passed: 23 tests.
- `pixi run python -m pytest -q tests\test_track29_mapping_graph.py tests\test_track29_conductor.py tests\test_track28_ontology_discovery.py tests\test_track28_conductor.py tests\test_track26_standards_registry.py tests\test_track55_56_conductor.py tests\test_track56_extraction_runtime.py tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py` passed: 60 tests.
- `pixi run python -m ruff check --no-cache src\nlp_policy_nz\ontology\mapping_graph.py src\nlp_policy_nz\ontology\__init__.py tests\test_track29_mapping_graph.py tests\test_track29_conductor.py` passed.
- Fresh `write_mapping_artifacts()` output now byte-matches the checked-in Track 29 generated artifacts.
