# Track 90 Plan

## Phase 1: Materialization
- [x] Add dataset builders, partitioning, joins, and Dataset Viewer tests.
- [x] Add rights-aware projection and completeness reports.

## Phase 2: Publication
- [x] Add staged/idempotent Hugging Face publication and generated cards.
- [x] Add release manifests, checksums, attestations, and Zenodo handoff.

## Phase 3: Acceptance
- [x] Run local smoke publication, streaming, rollback, and restricted-content tests.
- [x] Record endpoint and content-completeness evidence separately.

### Acceptance Boundary
- Repo-side verification is implemented in `verify_materialized_publication()` and covered by `tests/test_hf_archive_publication.py`.
- The live `edithatogo/fyi-archive-nz` dataset was verified with a 33,217-record
  manifest, Parquet, DuckDB, provenance, SBOM, schemas, and metadata artifacts.
- Repo-side implementation checkpoint: `ee9bc59`.
- Maintainer handoff: `docs/hf-archive-publication-runbook.md`.
- GitHub issue #96 is closed after verifying publication/materialization.
- Stale hosted dataset-card wording is an upstream `fyi-archive` metadata
  follow-up and does not keep this `nlp-policy-nz` milestone open.
