# Track 96 Evidence

## Repository-side implementation

- `HistoricalParliamentManifest` records split membership, source/page hashes,
  annotation references, annotator/adjudicator roles, authority evidence, and
  signed review decisions without embedding restricted page text.
- Validation rejects duplicate pages, hash/source/volume leakage, invalid
  split metadata, annotator/adjudicator overlap, and incomplete test evidence.
- Evaluation covers hierarchy, speaker attribution, links, abstention recall,
  and source-span fidelity against declared thresholds.
- Reports remain `no-promotion` when held-out records, authority evidence,
  signed review decisions, or measured metrics are missing.

## Verification

- `tests/test_track132_historical_held_out.py` covers empty scaffolds, leakage,
  role separation, missing evidence, threshold failures, and successful
  contract-shaped evaluation.
- `tests/test_track132_intake_contract.py` verifies the persisted intake/report
  boundary and rejects synthetic or incomplete promotion evidence.
- Existing Parliament structure/evaluation tests cover page identity,
  abstention, links, source spans, and metric scoring.

## Remaining external gates

No real rights-safe annotation package, temporal authority records,
independent adjudication signatures, or measured historical held-out run is in
this checkout. The repository therefore makes no empirical quality or
promotion claim; issue #132 remains open for those external deliverables.
