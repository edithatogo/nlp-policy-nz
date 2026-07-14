# Track 88 Specification: Historical Parliament Structure Reconstruction

## Goal

Recover analysis-ready hierarchy and speaker attribution from historical New Zealand parliamentary documents.

## Requirements

- Segment volume, session, sitting, date, page, debate, question, speech, interjection, division, table, and appendix.
- Resolve speaker strings to stable people/role identifiers with temporal validity and uncertainty.
- Preserve page/block/token source spans and OCR alternatives for every assertion.
- Link debates to legislation, agencies, places, iwi/hapu, committees, petitions, and cited publications using existing semantic and graph layers.
- Add abstention and review queues for ambiguous hierarchy or attribution.

## Acceptance

Held-out evaluation covers structure, speaker attribution, entity/relation extraction, and source-span fidelity without evaluation leakage.
