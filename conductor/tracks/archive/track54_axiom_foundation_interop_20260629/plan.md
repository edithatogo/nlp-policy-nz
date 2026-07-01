# Track 54: Axiom Foundation Interoperability

**Dependencies**: Tracks 18, 22, 27
**Parallelization Node**: External Legal Source and Rules-as-Code Interoperability
**Status**: Completed

## Phase 1: Source Identity and Provenance

**Status**: Complete

| # | Task | Status | Evidence |
|---|------|--------|----------|
| 1.1 | Add source-section metadata model for authoritative NZ legal text artifacts | [x] | `src/nlp_policy_nz/axiom/source.py` |
| 1.2 | Add exact normalized source SHA-256 stamping | [x] | `source_sha256()` |
| 1.3 | Add non-mutating source staleness comparison for current/stale/missing states | [x] | `compare_source_staleness()` |
| 1.4 | Convert source sections into existing `PipelineRecord` rows without schema churn | [x] | `source_section_to_pipeline_record()` |
| 1.5 | Add fixture-based tests for metadata, checksum, staleness, and conversion | [x] | `tests/test_axiom_integration.py` |
| 1.6 | Task: Conductor - User Manual Verification 'Phase 1: Source Identity and Provenance' (Protocol in workflow.md) | [x] | Focused pytest and Ruff passed |

## Phase 2: RuleSpec Bridge

**Status**: Complete

| # | Task | Status | Evidence |
|---|------|--------|----------|
| 2.1 | Add durable `nz:<path>#<concept>` reference model without runtime dependency | [x] | `src/nlp_policy_nz/axiom/rulespec.py` |
| 2.2 | Map `PipelineRecord` or NZ provision identifiers to RuleSpec references | [x] | `pipeline_record_rulespec_reference()` |
| 2.3 | Export `rulespec-nz` compatible source-verification metadata for future modules | [x] | `source_verification_metadata()` |
| 2.4 | Add tests for durable IDs and source-verification blocks | [x] | `test_rulespec_reference_and_source_verification_metadata` |
| 2.5 | Task: Conductor - User Manual Verification 'Phase 2: RuleSpec Bridge' (Protocol in workflow.md) | [x] | Focused pytest and Ruff passed |

## Phase 3: Bill and Hansard Linkage

**Status**: Complete

| # | Task | Status | Evidence |
|---|------|--------|----------|
| 3.1 | Add normalized NZ bill lifecycle status vocabulary | [x] | `normalise_bill_status()` |
| 3.2 | Add bill action and bill version metadata records | [x] | `BillAction`, `BillVersion` |
| 3.3 | Add Hansard debate to bill/provision link record | [x] | `BillHansardLink` |
| 3.4 | Add tests for lifecycle normalization and link serialization | [x] | `test_bill_status_and_hansard_linkage_scaffold` |
| 3.5 | Task: Conductor - User Manual Verification 'Phase 3: Bill and Hansard Linkage' (Protocol in workflow.md) | [x] | Focused pytest and Ruff passed |

## Phase 4: Documentation and Conductor Integration

**Status**: Complete

| # | Task | Status | Evidence |
|---|------|--------|----------|
| 4.1 | Document Axiom Foundation repo relevance tiers and integration decision | [x] | `docs/axiom-foundation-relevance.md` |
| 4.2 | Document shared source identity convention and future tracks | [x] | `docs/axiom-foundation-relevance.md` |
| 4.3 | Add Conductor track metadata, specification, plan, and index | [x] | `conductor/tracks/track54_axiom_foundation_interop_20260629/` |
| 4.4 | Register Track 54 in `conductor/tracks.md` | [x] | `conductor/tracks.md` |
| 4.5 | Task: Conductor - User Manual Verification 'Phase 4: Documentation and Conductor Integration' (Protocol in workflow.md) | [x] | Track files and registry validated by focused checks |

## Verification

Focused automated verification passed:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_rac_bridge.py tests\test_axiom_integration.py
.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\axiom\rulespec.py tests\test_rac_bridge.py tests\test_axiom_integration.py
```

Cross-repo `rulespec-nz` layout compatibility was also verified:

```powershell
& 'C:\Users\60217257\.pixi\bin\pixi.exe' run pytest tests/test_repository_layout.py -q
```

## External Gates

- Track 18 dependency is satisfied by the completed voting/amendment parser and pipeline enrichment track.
- Track 22 dependency is satisfied for repo-side contracts by the offline Isaacus adapter, local NZ-MLEB fixture, and fail-closed external gates; live Isaacus downloads and model runs remain external.
- Track 27 dependency is satisfied for repo-side bridge integration by `ontology/rac_bridge.py`, `rac-export`, and offline OpenFisca/PolicyEngine package skeleton generation; live executable parity remains external.
- Live execution through `axiom-rules-engine` remains out of scope until there is a concrete NZ encoded-rule use case.
- `rulespec-nz` content generation belongs in `rulespec-nz`, not in this repository.
- Axiom UI, graph viewer, oracle, and microsimulation ideas remain future tracks unless a user-facing RuleSpec or knowledge-graph explorer is added.
