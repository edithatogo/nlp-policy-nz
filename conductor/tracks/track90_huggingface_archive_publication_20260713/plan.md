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
- Public endpoint smoke remains an external gate: the collection repositories exist and are public, but Dataset Viewer-compatible files and a successful authenticated workflow run are still required.
- Repo-side implementation checkpoint: `ee9bc59`.
