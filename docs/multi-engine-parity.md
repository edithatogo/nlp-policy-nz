# Multi-Engine Parity

Track 80 turns the reviewed PolicyEngine pilot into a deterministic parity
bundle for PolicyEngine and OpenFisca-compatible export paths.

## Support Levels

- `primary`: the reviewed repo-local reference adapter that already passed the
  pilot oracle checks.
- `export-only`: a downstream-compatible package skeleton that can be written in
  CI without requiring a live OpenFisca runtime.
- `optional`: future adapters that remain behind feature detection or optional
  extras.

## Repo Boundary

This repository owns:

- reviewed source handoff artifacts;
- deterministic package skeletons for downstream engines;
- parity reports that compare repo-local reference outputs against oracle
  fixtures;
- skip behavior for optional runtime dependencies.

This repository does not own:

- a live OpenFisca runtime installation;
- production deployment of any downstream rules engine;
- broad all-engine formula coverage.

## CLI

Generate the parity bundle from the reviewed Track 79 manifest:

```bash
nlp-policy-nz multi-engine-parity \
  --manifest data/track79/policyengine_pilot_manifest.json \
  --output-dir output/multi-engine-parity
```

The command writes both package skeletons and a parity report:

- `policyengine_nz_commencement_pilot/`
- `openfisca_nz_commencement_pilot/`
- `multi_engine_parity_report.json`
- `multi_engine_parity_report.md`

## Promotion Criteria

Future engines should only be promoted after:

1. source provenance remains stable;
2. oracle outputs remain deterministic;
3. the exported package skeleton is reproducible in GitHub Actions;
4. any runtime-specific dependency stays optional until a real execution path is
   reviewed.
