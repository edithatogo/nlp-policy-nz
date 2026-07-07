# Track 79 Pilot Review

The selected pilot domain is the commencement clause in `data/track74/sources/legislation_commencement.txt`.

- Source provision: "This Act commences on the day after Royal assent."
- Formula: `assessment_date > royal_assent_date`
- Entity: `person`
- Period: `day`
- Parameter: `royal_assent_date = 2026-06-30`
- Oracle fixtures: `data/track79/oracles/policyengine_oracles.json`
- Review evidence: `data/track79/reviews/policyengine_pilot_review.md`

This pilot is intentionally narrow. It demonstrates one reviewed executable
formula and does not claim complete PolicyEngine coverage for NZ legislation.
