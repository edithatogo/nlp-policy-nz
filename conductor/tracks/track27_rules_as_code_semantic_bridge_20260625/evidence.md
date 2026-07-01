# Track 27 Evidence - Rules-as-Code Semantic Bridge

## Status

- track_status: completed
- implementation_scope: repo-side rules-as-code bridge schema, source anchoring, norm semantics, temporal validity, linked-data export, CLI export, and offline package skeleton generation
- external_gate_boundary: live executable parity with OpenFisca or PolicyEngine remains blocked until reviewed formulas and oracle fixtures are supplied

## Implemented artifacts

- `src/nlp_policy_nz/ontology/rac_bridge.py` defines the source anchor, norm semantics, temporal validity, policy taxonomy, RuleSpec reference, schema.org/Legislation, provenance, JSON-LD rendering, and OpenFisca/PolicyEngine package skeleton helpers.
- `src/nlp_policy_nz/cli/main.py` exposes `nlp-policy-nz rac-export` with optional package skeleton output.
- `tests/test_rac_bridge.py` verifies source-provenance preservation, norm/temporal JSON export, CLI export, package skeleton generation, placeholder formula boundaries, and safe package write paths.
- `tests/test_axiom_integration.py` covers the Axiom/RuleSpec source-verification surfaces used by the bridge.
- `tests/test_cli.py` covers CLI parser and command wiring.

## Bridge coverage

The repo-side bridge covers:

- ELI/ELI-DL-compatible source anchors through stable citation paths, source URLs, checksums, jurisdiction, document type, and titles.
- LKIF/LegalRuleML-adjacent norm semantics through legal effect, deontic modality, trigger, and scope fields.
- OWL-Time/TimeML-adjacent temporal validity through start, end, and expression fields.
- Local policy taxonomy hooks for later SKOS/EuroVoc or NZ-specific controlled vocabulary alignment.
- RuleSpec source-verification metadata without leaking source URLs into the durable module identity.
- PROV-O-compatible provenance fields and schema.org/Legislation JSON-LD discoverability.
- Offline OpenFisca/PolicyEngine-style package skeletons with explicit non-executable placeholder formulas.

## Validation commands

```powershell
pixi run python -m pytest -q tests\test_rac_bridge.py tests\test_axiom_integration.py tests\test_cli.py
pixi run python -m ruff check --no-cache src\nlp_policy_nz\ontology\rac_bridge.py src\nlp_policy_nz\ontology\__init__.py src\nlp_policy_nz\cli\main.py tests\test_rac_bridge.py src\nlp_policy_nz\axiom tests\test_axiom_integration.py tests\test_cli.py
```

## Residual scope

Track 27 intentionally does not claim executable parity with OpenFisca or PolicyEngine. Generated package skeletons raise `NotImplementedError` until legal formulas, target entities, periods, parameters, and oracle fixtures are reviewed.
