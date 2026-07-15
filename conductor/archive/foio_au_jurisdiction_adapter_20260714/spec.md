# FOI-O Australian jurisdiction extraction adapter

## Objective

Extend the FOI-O archive handoff with a jurisdiction-aware Australian adapter.
The first pilot supports Commonwealth (`Cth`) and New South Wales (`NSW`). The
adapter must route only when a source has an unambiguous profile, abstain for
unsupported or ambiguous sources, and emit candidate-only records for review.

## Contract

- Every accepted input is pinned to the archive revision, source digest, legal
  profile revision, ontology revision, model revision, schema version, and
  extraction contract version.
- Routing is explicit and deterministic. A record cannot be emitted under a
  profile different from its source jurisdiction.
- A bundle contains one jurisdiction profile only. Mixed-profile records are a
  hard error (cross-profile contamination guard).
- Commonwealth and NSW are the only enabled profiles in this pilot. Other
  Australian jurisdictions abstain until their profile and evaluation gates
  pass.
- Outputs use the existing FOI-O ontology and `ExtractionRecord` schema; no
  jurisdiction-specific ontology is forked.
- All emitted records are `candidate` outputs and retain source spans,
  uncertainty, routing evidence, and provenance.
- Evaluation reports precision, recall, F1, calibration error, coverage,
  disagreement count, and abstention count independently per jurisdiction.

## Non-goals

This track does not download live legislation, promote legal labels, or claim
that the Commonwealth/NSW pilot validates the remaining Australian states and
territories.

## Acceptance evidence

- Deterministic routing and abstention tests.
- Cross-profile contamination rejection tests.
- Immutable provenance validation tests.
- Candidate-only Commonwealth and NSW bundle fixtures.
- Per-jurisdiction evaluation report fixture with disagreement and abstention
  counts.
