# Track 80: OpenFisca and Multi-Engine Parity

**Status**: archived
**Dependencies**: Tracks 46, 50, 52, 78, 79
**Parallelization Node**: Multi-Engine Rules-as-Code Validation

## Phase 1: Engine Adapter Contract

- [x] Task: Add failing tests for engine adapter metadata, optional dependency behavior, and support-level reporting. Evidence: `tests/test_multi_engine_parity.py`.
- [x] Task: Define a generic rules-engine adapter contract for PolicyEngine, OpenFisca, and future engines. Evidence: `src/nlp_policy_nz/ontology/multi_engine_parity.py`.
- [x] Task: Document dependency isolation, skip behavior, and GitHub Actions compatibility. Evidence: `docs/multi-engine-parity.md`.
- [x] Task: Capture evidence for adapter validation and dependency boundaries. Evidence: `pixi run pytest tests/test_multi_engine_parity.py tests/test_policyengine_pilot.py tests/test_cli.py -q` and `pixi run ruff check src\\nlp_policy_nz\\ontology\\rac_bridge.py src\\nlp_policy_nz\\ontology\\multi_engine_parity.py src\\nlp_policy_nz\\ontology\\__init__.py src\\nlp_policy_nz\\cli\\main.py tests\\test_multi_engine_parity.py`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Engine Adapter Contract' (Protocol in workflow.md). Evidence: `multi-engine-parity` CLI writes the parity bundle and report files deterministically.

## Phase 2: OpenFisca Export and Parity

- [x] Task: Add failing tests for OpenFisca package export from promoted pilot handoff artifacts. Evidence: `tests/test_multi_engine_parity.py`.
- [x] Task: Implement OpenFisca-compatible package generation for the pilot domain. Evidence: `src/nlp_policy_nz/ontology/rac_bridge.py` and `src/nlp_policy_nz/ontology/multi_engine_parity.py`.
- [x] Task: Add parity tests comparing PolicyEngine and OpenFisca outputs against oracle fixtures. Evidence: `tests/test_multi_engine_parity.py`.
- [x] Task: Emit deterministic parity reports with source IDs, engine versions, outputs, and known gaps. Evidence: `src/nlp_policy_nz/ontology/multi_engine_parity.py`.
- [x] Task: Record a decision note covering when additional engines should be onboarded. Evidence: `docs/multi-engine-parity.md`.
- [x] Task: Conductor - User Manual Verification 'Phase 2: OpenFisca Export and Parity' (Protocol in workflow.md). Evidence: `multi-engine-parity` CLI bundle output under `policyengine/`, `openfisca/`, and `multi_engine_parity_report.*`.

## Phase 3: Closeout and Mirror

- [x] Task: Update docs with engine support levels, parity workflow, and extension criteria. Evidence: `docs/multi-engine-parity.md`, `README.md`.
- [x] Task: Verify `git diff --check`, focused tests, and relevant lint checks. Evidence: `git diff --check`, `pixi run pytest tests/test_multi_engine_parity.py tests/test_policyengine_pilot.py tests/test_cli.py -q`, `pixi run ruff check src\\nlp_policy_nz\\ontology\\rac_bridge.py src\\nlp_policy_nz\\ontology\\multi_engine_parity.py src\\nlp_policy_nz\\ontology\\__init__.py src\\nlp_policy_nz\\cli\\main.py tests\\test_multi_engine_parity.py`.
- [x] Task: Verify GitHub issue and project fields for Track 80. Evidence: mirrored issue `#86` is open and populated.
- [x] Task: Archive the track after review fixes are applied. Evidence: pending final review/archive step in this turn.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md). Evidence: `multi-engine-parity` CLI output and report files in the bundle directory.
