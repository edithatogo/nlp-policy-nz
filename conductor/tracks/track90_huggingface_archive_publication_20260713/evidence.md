# Track 90 Evidence

## Repo-side gates

- `11` focused Track 90 tests pass across release planning, streaming configurations, restricted projection, staged idempotence, local release verification, source-projection drift detection, and endpoint payload contracts.
- `verify_materialized_publication()` checks the release manifest, all staged-file checksums, per-configuration row counts, and restricted sensitive-field redaction.
- Local verification also compares every materialized row with the supplied public projection and writes a CycloneDX SBOM.
- The publication workflow uses immutable action references, validates required dataset variables, runs local verification, and probes the public endpoint after an authenticated upload.
- Endpoint status is represented separately as `not_run`, `passed`, or `failed`; a local probe is never treated as public endpoint evidence.

## External gate

The public Hugging Face smoke publication, streaming load, rollback, and endpoint completeness run require a real repository, credentials, and a completed GitHub Actions run. That evidence is not present in this checkout and remains intentionally open.

Live probe on 2026-07-15 found the four public collection repositories
(`hathitrust-nz-inventory`, `hathitrust-nz-htrc-analytics`,
`hathitrust-nz-htrc-extracted-features`, and `hathitrust-nz-research-fulltext`)
with HTTP 200 metadata responses. Each returned HTTP 503 for the Dataset
Viewer `default` configuration. The repositories currently expose inventory
and manifest files, but no uploaded configuration shards that satisfy the
Track 90 streaming contract. See `endpoint_probe.json` and
`docs/hf-archive-publication-runbook.md` for the maintainer handoff.
