# Track 45: Release Engineering & Automated Publishing

**Dependencies**: Tracks 8, 9, 24, 36
**Parallelization Node**: CI/CD Automation
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Add `commit-and-tag-version` or `semantic-release` as dev dependency; configure `VERSION` file and conventional commit enforcement in pre-commit | [ ] | conductor_orchestrator |
| 2 | Create `VERSION.json` generator script: outputs `{version, build_timestamp, commit_sha, dataset_revision}` | [ ] | conductor_orchestrator |
| 3 | Create `.github/workflows/publish-hf-datasets.yml`: on push to master, increment dataset revision, upload new Parquet snapshots to HF Hub | [ ] | conductor_orchestrator |
| 4 | Create `.github/workflows/publish-hf-space.yml`: on push to master, auto-deploy Gradio Space to HF Spaces | [ ] | conductor_orchestrator |
| 5 | Create `.github/workflows/publish-zenodo.yml`: on v* tag, build dataset archive, create Zenodo deposition with DOI, upload archive | [ ] | conductor_orchestrator |
| 6 | Create `.github/workflows/publish-osf.yml`: on v* tag, push dataset + model archive to OSF project storage via osfclient | [ ] | conductor_orchestrator |
| 7 | Create `.github/workflows/publish-pypi.yml`: on v* tag, build and publish to PyPI | [ ] | conductor_orchestrator |
| 8 | Create `CITATION.cff` template and auto-generator from VERSION.json | [ ] | conductor_orchestrator |
| 9 | Wire release-drafter (Track 39) to auto-update CHANGELOG.md and create GitHub Release with SBOM + checksums | [ ] | conductor_orchestrator |
| 10 | Test all workflows in sandbox (HF sandbox org, Zenodo sandbox, OSF test project) before production enablement | [ ] | conductor_orchestrator |

## Evidence Boundary

CI/CD workflow YAML files, VERSION.json generator, CITATION.cff template, and sandbox test results satisfy repo-side evidence. Live publishing to production HF/Zenodo/OSF/PyPI requires API tokens, org access, and credentials which are runtime secrets.
