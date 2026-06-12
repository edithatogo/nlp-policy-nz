# Track 9: Establish Citable Zenodo Archives & Release Workflows

**Dependencies**: Track 8 (Hugging Face Datasets & Visualization Spaces)
**Parallelization Node**: Zenodo API Deposit Registry
**Status**: 🔄 In Progress

---

## Goal

Provide a polished, documented release workflow that allows researchers to create versioned, citable Zenodo archives of processed NZ legislative and Hansard corpora.

---

## Phase 1: Track Setup & Formalisation

**Estimated Effort**: Low
**Status**: ✅ Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Create `conductor/tracks/track9_zenodo_20260609/spec.md` with full spec | [x] | |
| 1.2 | Create `conductor/tracks/track9_zenodo_20260609/plan.md` with phased checklist | [x] | |
| 1.3 | Update `conductor/tracks.md` to mark Track 9 as in progress | [x] | |

---

## Phase 2: Zenodo Production API Support

**Estimated Effort**: Low
**Status**: ✅ Complete

Extend the existing Sandbox-only client to support production Zenodo.

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Add `ZENODO_PRODUCTION_API_URL` constant to `integrations/zenodo.py` | [x] | |
| 2.2 | Add `ZENODO_PRODUCTION_TOKEN` env-var name constant | [x] | |
| 2.3 | Update `create_sandbox_deposit`, `upload_file_to_deposit`, `publish_deposit` to accept an `environment` parameter | [x] | |
| 2.4 | Update `ZenodoArchiver` and `archive_to_zenodo` to accept `environment` parameter | [x] | |
| 2.5 | Update `integrations/__init__.py` to export new constants | [x] | |
| 2.6 | Write/update tests for production environment | [x] | |

---

## Phase 3: CLI Subcommand Tests

**Estimated Effort**: Low
**Status**: ✅ Complete

Add comprehensive tests for the `archive-to-zenodo` and `release` CLI subcommands.

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add test for `archive-to-zenodo` argument parsing (all flags) | [x] | |
| 3.2 | Add test for `release` argument parsing (all flags) | [x] | |
| 3.3 | Add test for `archive-to-zenodo` handler dispatch (mock ZenodoArchiver) | [x] | |
| 3.4 | Add test for `release` handler dispatch (mock ReleaseManager) | [x] | |
| 3.5 | Add test for `archive-to-zenodo` error handling (missing file, API error) | [x] | |
| 3.6 | Add test for `release` error handling (missing file, API error) | [x] | |

---

## Phase 4: GitHub Actions Release Workflow

**Estimated Effort**: Medium
**Status**: ✅ Complete

Create a CI/CD pipeline that publishes releases to Zenodo on tag pushes.

| # | Task | Status | Commit |
|---|------|--------|--------|
| 4.1 | Create `.github/workflows/release.yml` — trigger on `v*` tags | [x] | |
| 4.2 | Add job to build and verify the package | [x] | |
| 4.3 | Add job to create the release archive from pipeline test outputs | [x] | |
| 4.4 | Add job to upload to Zenodo Sandbox (dry-run) and Production (on real release) | [x] | |
| 4.5 | Add job to create a GitHub Release with the archive attached | [x] | |

---

## Phase 5: Release Script & Polish

**Estimated Effort**: Low
**Status**: ✅ Complete

Create a convenience script for local one-shot releases.

| # | Task | Status | Commit |
|---|------|--------|--------|
| 5.1 | Create `scripts/release.sh` — one-shot archive + Zenodo publish with dry-run mode | [x] | |
| 5.2 | Ensure script is executable and documented | [x] | |

---

## Phase 6: Documentation Update

**Estimated Effort**: Low-Medium
**Status**: ✅ Complete

Update project documentation to reflect the new Zenodo/release capabilities.

| # | Task | Status | Commit |
|---|------|--------|--------|
| 6.1 | Update `product.md` — add Zenodo archival to core features | [x] | |
| 6.2 | Update `requirements.md` — add `requests` dependency (already present) | [x] | |
| 6.3 | Update `README.md` — add "Archiving & Releases" section with usage examples | [x] | |
| 6.4 | Add Zenodo badge or citation info to `README.md` | [x] | |

---

## Phase 7: Verification & Finalisation

**Estimated Effort**: Low
**Status**: ✅ Complete

Run full test suite, fix any issues, and mark the track complete.

| # | Task | Status | Commit |
|---|------|--------|--------|
| 7.1 | Run full test suite (`pixi run test` or equivalent) | [x] | |
| 7.2 | Run linting/formatting check (`pixi run lint` or `ruff check`) | [x] | |
| 7.3 | Fix any failing tests or lint errors | [x] | |
| 7.4 | Mark Track 9 as complete in `conductor/tracks.md` | [x] | |

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `conductor/tracks/track9_zenodo_20260609/spec.md` | Create |
| `conductor/tracks/track9_zenodo_20260609/plan.md` | Create |
| `conductor/tracks.md` | Modify |
| `src/nlp_policy_nz/integrations/zenodo.py` | Modify |
| `src/nlp_policy_nz/integrations/zenodo_archive.py` | Modify |
| `src/nlp_policy_nz/integrations/__init__.py` | Modify |
| `tests/test_cli.py` | Modify |
| `.github/workflows/release.yml` | Create |
| `scripts/release.sh` | Create |
| `product.md` | Modify |
| `README.md` | Modify |
