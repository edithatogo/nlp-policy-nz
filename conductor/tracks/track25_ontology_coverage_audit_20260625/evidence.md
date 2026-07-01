# Track 25 Evidence - Ontology Coverage Audit

## Status

- track_status: completed
- implementation_scope: deterministic repo-side ontology coverage audit, data blocker register, and prioritized backlog
- external_data_boundary: live external ontology acquisition remains follow-on work for Tracks 26-31

## Implemented artifacts

- `src/nlp_policy_nz/quality/track25_ontology_coverage.py` enumerates ontology-facing systems, upstream standards, local files, coverage status, blocker type, missing features, and follow-on tracks.
- `data/ontologies/coverage_manifest.json` materializes the full audit bundle with system rows, flattened coverage matrix, blocker register, prioritized backlog, and summary counts.
- `data/ontologies/data_blocker_register.json` separates implementation gaps from source-data, specification, validation, and integration blockers.
- `data/ontologies/ontology_implementation_backlog.json` prioritizes follow-on implementation work for Tracks 26-31.
- `tests/test_track25_ontology_coverage.py` verifies deterministic generation, schema shape, implemented and missing standards, blocker ordering, and checked-in artifact parity.

## Coverage matrix scope

The audit covers the standards requested by the Track 25 specification, including:

- Akoma Ntoso / LegalDocML, FRBR, TLC, ELI, ELI-DL, and ECLI.
- PROV-O provenance.
- FOAF and SIOC linked-data graph exports.
- Wikidata, schema.org, schema.org/Legislation, EuroVoc, SKOS, Popolo, W3C ORG, DCAT, and DCAT-AP.
- LKIF, TimeML, OWL-Time, LegalRuleML, Catala, OpenFisca, and PolicyEngine-adjacent surfaces.

## Validation commands

```powershell
pixi run python -m pytest -q tests\test_track25_ontology_coverage.py tests\test_track26_standards_registry.py
pixi run python -m ruff check --no-cache src\nlp_policy_nz\quality\track25_ontology_coverage.py tests\test_track25_ontology_coverage.py tests\test_track26_standards_registry.py
```

## Residual scope

Track 25 records what is implemented versus blocked. It does not claim to download or validate every external ontology live. Those external-source and expanded-implementation gates are intentionally routed into Tracks 26-31.
