# Plan: FOI-O Australian jurisdiction extraction adapter

**Status**: contract milestone complete; promotion reviewed and rejected
**Issue**: #101
**Track ID**: `foio_au_jurisdiction_adapter_20260714`

## Phase 1: Profile and routing contract

- [x] Define immutable Commonwealth/NSW profile snapshots and legal/model pins.
- [x] Implement deterministic routing with explicit abstention for unsupported
  and ambiguous sources.
- [x] Enforce one-profile-per-bundle and reject cross-profile contamination.

## Phase 2: Candidate handoff and evaluation

- [x] Emit candidate-only profile-isolated archive bundles with provenance.
- [x] Report per-jurisdiction precision, recall, F1, calibration, coverage,
  disagreement, and abstention.
- [x] Add bounded Commonwealth/NSW fixtures and focused tests.

## Phase 3: Evidence and gates

- [x] Run focused tests, ruff, and basedpyright.
- [x] Record deterministic evidence and remaining human promotion gates.
- [x] Record separate fail-closed no-promotion decisions for Commonwealth and NSW.

## Evidence

- `21` focused tests pass across the existing FOI-O adapter, Australian
  routing/bundle/evaluation tests, and cloud OCR orchestration/workflow tests.
- Ruff and basedpyright pass for the changed extraction and orchestration
  modules.
- Australian output remains candidate-only; no legal label promotion is made.
- Remaining gate: human review of Commonwealth/NSW profile pins and empirical
  promotion evidence before adding other Australian jurisdictions.
- The 2026-07-15 independent panel rejected promotion because the pilot inputs
  are synthetic and the pins are placeholders. Track 93 / issue #129 owns the
  real empirical and human-review evidence required for any future promotion.
