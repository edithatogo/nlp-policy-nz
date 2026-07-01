# Track 26 Evidence - Ontology Standards Expansion

## Status

- track_status: completed
- implementation_scope: deterministic standards registry, JSON schema, URI helpers, namespace mappings, and fixture round trips
- external_data_boundary: standards without source data or complete formal specifications remain explicit blockers

## Implemented artifacts

- `data/ontologies/track26_standards_registry.json` records standards, source URLs, source licenses, local representation paths, implementation status, blocker type, and blocker source.
- `data/ontologies/standards_registry.schema.json` defines the checked-in registry contract and enum constraints.
- `src/nlp_policy_nz/ontology/registry.py` builds and writes the deterministic Track 26 registry manifest.
- `src/nlp_policy_nz/ontology/standards.py` exposes stable ontology IDs, namespace mappings, ELI and ELI-DL URI helpers, ECLI identifiers, EuroVoc/SKOS concept round trips, and schema.org/Legislation round trips.
- `tests/test_track26_standards_registry.py` verifies registry coverage, deterministic manifest writing, schema contract alignment, controlled concept round trips, and schema.org/Legislation round trips.

## Standards scope

The registry covers the Track 26 standards set:

- ELI, ELI-DL, and ECLI.
- EuroVoc and SKOS.
- CEN MetaLex, USLM, LexML, and schema.org/Legislation.
- LKIF and LegalRuleML, including explicit full-standard blockers.
- Popolo and W3C ORG.
- DCAT and DCAT-AP.
- OpenFisca, PolicyEngine, and the formal OpenFisca/PolicyEngine ontology bridge.

## Validation commands

```powershell
pixi run python -m pytest -q tests\test_track26_standards_registry.py tests\test_track26_conductor.py
pixi run python -m ruff check --no-cache src\nlp_policy_nz\ontology\registry.py src\nlp_policy_nz\ontology\standards.py tests\test_track26_standards_registry.py tests\test_track26_conductor.py
```

## Residual scope

Track 26 intentionally distinguishes implementable repo-side helpers from standards that require external source data, formal crosswalks, or live publication validation. Those standards are represented as explicit blockers rather than omitted from the registry.
