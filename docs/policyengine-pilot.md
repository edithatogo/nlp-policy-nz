# PolicyEngine Pilot

Track 79 promotes one narrow reviewed commencement domain into a deterministic,
offline package layout that can execute in GitHub Actions.

## Selected Domain

- Source citation path: `nz/statutes/commencement/2026/1`
- Source excerpt: `This Act commences on the day after Royal assent.`
- Entity: `person`
- Period: `day`
- Parameter: `royal_assent_date`
- Formula: `assessment_date > royal_assent_date`
- Oracle fixtures: `data/track79/oracles/policyengine_oracles.json`

## Boundary

The generated package is PolicyEngine-compatible in shape and uses a
standard-library execution harness inside this repository. Broad executable-law
maintenance remains a downstream responsibility after the pilot is proven.

## CLI

```powershell
nlp-policy-nz policyengine-pilot `
  --manifest data/track79/policyengine_pilot_manifest.json `
  --output-dir output/policyengine-pilot
```

The command writes the generated package, reviewed handoff artifacts, and an
oracle execution report.
