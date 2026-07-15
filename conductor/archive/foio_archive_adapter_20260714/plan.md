# Plan: FOI-O archive extraction adapter

Consumer gate: `tests/test_foio_extraction_contract.py` validates the pinned
FOI-O extraction-contract shape before adapter execution. The full repository
gate must run under a supported Python/spaCy environment.

**Status**: contract milestone complete; promotion reviewed and rejected
**Dependencies**: FOI-O V2 extraction contract; existing ingestion, entity,
ontology mapping, serialization, and provenance tracks
**Parallelization Node**: FOI-O archive integration

## Phase 1: Versioned adapter contract

- [x] Pin FOI-O and `fyi-archive-nz` revisions in a reproducibility manifest. [adapter contract]
- [x] Map FOI-O labels onto existing pipeline components without duplicating ontology ownership. [adapter contract]
- [x] Define candidate output and provenance serialization accepted by `fyi-archive`. [adapter contract]
- [x] Add positive, negative, and unknown-label contract fixtures. [adapter contract]

## Phase 2: Extraction and evaluation

- [x] Implement the adapter over a bounded pinned sample. [bounded_evaluation_fixture.json]
- [x] Preserve source spans, raw labels, uncertainty, and conflicting candidates. [fixture contract]
- [x] Compare with the initial ontology-based extraction and emit a structured delta. [compare_foio_baseline]
- [x] Evaluate label-family precision, recall, F1, calibration, and coverage. [bounded_evaluation_report.json]

## Phase 3: Re-extraction handoff

- [x] Produce a dry-run derived bundle for `fyi-archive` validation. [dry_run_derived_bundle.json]
- [x] Review disagreements and record the fail-closed no-promotion decision.
- [x] Run focused adapter tests and record their evidence. [6 tests passed]
- [x] Record exact source/model/ontology revisions in the fixture and derived bundle.

### Phase 1 evidence

The adapter contract is implemented in `src/nlp_policy_nz/extraction/foio_adapter.py`
and covered by `tests/test_foio_archive_adapter.py`. It sorts records by stable
ID, requires a 40-character immutable archive revision and matching content
digest, enriches records with FOI-O/pipeline provenance, emits candidate-only
bundles, and reports baseline deltas. Full repository tests remain blocked in
the default Python 3.14 environment because the current spaCy 3.x lock cannot
resolve a cp314 wheel; the isolated compatibility environment also lacks the
repository's optional LanceDB dependency.

### Phase 2 evidence

`data/foio/bounded_evaluation_fixture.json` pins a bounded sample to an
immutable archive revision and content digest. The adapter validates the
fixture with Pydantic, preserves source spans and candidate uncertainty, and
evaluates exact family/label matches. The deterministic report in
`artifacts/foio/bounded_evaluation_report.json` records precision, recall, F1,
calibration error, and coverage independently for obligation and permission
families. The permission disagreement remains a candidate-review item; no
legal assertion is promoted automatically.

### Phase 3 decision

The 2026-07-15 independent panel found the contract implementation suitable as
a candidate-only pilot but found no evidence basis for legal-label promotion.
All promotion work is transferred to Track 93 / issue #129. No human legal
approval is claimed.
