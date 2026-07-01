# Track 24 Evidence - Multi-Git and Multi-Archive Mirroring

## Status

- track_status: completed
- implementation_scope: repo-side workflow, contract tests, and archival strategy documentation
- external_secret_boundary: GitHub mirror secrets require repository-owner configuration and cannot be proven from local CI

## Implemented Artifacts

- `.github/workflows/mirror_sync.yml` defines push triggers for `main` and `master`, plus `workflow_dispatch` for manual runs.
- `.github/workflows/mirror_sync.yml` reads separate `GITLAB_MIRROR_URL`, `CODEBERG_MIRROR_URL`, and `GIT_MIRROR_SSH_PRIVATE_KEY` secrets.
- `.github/workflows/mirror_sync.yml` exits successfully when mirror URLs or SSH credentials are empty, so unconfigured forks and CI runs do not fail.
- `tests/test_mirror_sync_workflow.py` verifies canonical branch triggers, GitLab and Codeberg target wiring, and empty-credential bypass behavior.
- `docs/multi_archive_strategy.md` records the archive tiering policy: Hugging Face as active publishing, Zenodo as DOI-backed archival storage, and OSF as an optional convenience mirror.

## Manual Configuration Boundary

The plan item for configuring GitHub secrets is marked complete by manual verification. The durable repo-side contract is that the workflow consumes these exact secret names and bypasses safely when they are absent:

- `GITLAB_MIRROR_URL`
- `CODEBERG_MIRROR_URL`
- `GIT_MIRROR_SSH_PRIVATE_KEY`

## Validation Commands

```powershell
pixi run python -m pytest -q tests\test_mirror_sync_workflow.py tests\test_track24_conductor.py
```

## Residual Scope

Production mirror pushes require repository secrets and external GitLab/Codeberg repositories. Live production mirroring is therefore an operational verification, not a local repository implementation gap.
