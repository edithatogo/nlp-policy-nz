# Track 27: Rules-as-Code Semantic Bridge

**Dependencies**: Tracks 25-26
**Parallelization Node**: Rules-as-Code Bridge
**Status**: Completed

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Inventory existing source anchoring, norm semantics, temporal validity, and RuleSpec source-verification hooks from Tracks 10, 11, 27, and 54 | [x] | conductor_orchestrator |
| 2 | Define RaC bridge schema connecting source text anchor -> norm statement -> temporal scope -> jurisdiction -> provenance | [x] | conductor_orchestrator |
| 3 | Create `src/nlp_policy_nz/ontology/rac_bridge.py` with source anchoring, norm extraction, and temporal validity composition | [x] | conductor_orchestrator |
| 4 | Add OpenFisca/PolicyEngine model stub: read NZ Act parameters and emit deployable rule package skeleton | [x] | conductor_orchestrator |
| 5 | Integrate with provenance metadata for rule authorship and source derivation chain | [x] | conductor_orchestrator |
| 6 | Add linked-data discoverability: schema.org/Legislation JSON-LD export for each RaC rule | [x] | conductor_orchestrator |
| 7 | Write tests for anchor->norm->temporal JSON export and provenance preservation | [x] | conductor_orchestrator |
| 8 | Add CLI command `nlp-policy-nz rac-export` that emits the full RaC bridge as JSON-LD | [x] | conductor_orchestrator |

## Implementation Note - 2026-06-29

Repo-side rules-as-code bridge scaffolding is implemented:

- Added `src/nlp_policy_nz/ontology/rac_bridge.py`.
- Added source anchor, norm semantics, temporal validity, policy taxonomy, RuleSpec source verification, schema.org/Legislation JSON-LD, and provenance fields.
- Added stable JSON rendering and disk writer helpers.
- Added `nlp-policy-nz rac-export` CLI command.
- Added `tests/test_rac_bridge.py`.
- Focused verification passed:
  - `.\.venv\Scripts\python.exe -m pytest tests\test_rac_bridge.py tests\test_axiom_integration.py`
  - `.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\ontology\rac_bridge.py src\nlp_policy_nz\ontology\__init__.py src\nlp_policy_nz\cli\main.py tests\test_rac_bridge.py src\nlp_policy_nz\axiom tests\test_axiom_integration.py`

## Implementation Note - 2026-06-29, package skeleton closeout

The remaining repo-side package-generation blocker is implemented:

- Added `PolicyEnginePackageSkeleton`, `build_policyengine_package_skeleton`, and `write_policyengine_package_skeleton`.
- Added optional `rac-export --package-output-dir --package-name` support.
- The generated package includes `pyproject.toml`, package init files, a source-grounded placeholder variable module, parameter YAML, and README.
- Placeholder formulas raise `NotImplementedError` until legal formulas and oracle fixtures are reviewed.
- Focused verification passed:
  - `.\.venv\Scripts\python.exe -m pytest tests\test_rac_bridge.py tests\test_axiom_integration.py tests\test_cli.py`
  - `.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\ontology\rac_bridge.py src\nlp_policy_nz\ontology\__init__.py src\nlp_policy_nz\cli\main.py tests\test_rac_bridge.py src\nlp_policy_nz\axiom tests\test_axiom_integration.py`

Track 27 is complete for repo-side scaffolding. Live executable parity with OpenFisca/PolicyEngine remains an external gate.

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
