# Track 45: Release Engineering & Automated Publishing

**Dependencies**: Tracks 8, 9, 24, 36
**Parallelization Node**: CI/CD Automation
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Add release metadata generator and semantic version bump helper; conventional commit enforcement already exists via Track 39 | [x] | conductor_orchestrator |
| 2 | Create `VERSION.json` generator script: outputs `{version, build_timestamp, commit_sha, dataset_revision}` | [x] | conductor_orchestrator |
| 3 | Create `.github/workflows/publish-hf-datasets.yml`: on push to master, increment dataset revision, upload new Parquet snapshots to HF Hub | [x] | conductor_orchestrator |
| 4 | Create `.github/workflows/publish-hf-space.yml`: on push to master, auto-deploy Gradio Space to HF Spaces | [x] | conductor_orchestrator |
| 5 | Create `.github/workflows/publish-zenodo.yml`: on v* tag, build dataset archive, create Zenodo deposition with DOI, upload archive | [x] | conductor_orchestrator |
| 6 | Create `.github/workflows/publish-osf.yml`: on v* tag, push dataset + model archive to OSF project storage via osfclient | [x] | conductor_orchestrator |
| 7 | Create `.github/workflows/publish-pypi.yml`: on v* tag, build and publish to PyPI | [x] | conductor_orchestrator |
| 8 | Create `CITATION.cff` template and auto-generator from VERSION.json | [x] | conductor_orchestrator |
| 9 | Wire release-drafter (Track 39) to auto-update CHANGELOG.md and create GitHub Release with SBOM + checksums | [x] | conductor_orchestrator |
| 10 | Test all workflows with contract tests, YAML parsing, and local dry-run metadata generation before production enablement | [x] | conductor_orchestrator |
| 11 | Create `.github/workflows/publish-hf-models.yml`: on manual dispatch, upload model artifacts to Hugging Face Hub | [x] | conductor_orchestrator |

## Evidence Boundary

CI/CD workflow YAML files, VERSION.json generator, CITATION.cff template, and sandbox test results satisfy repo-side evidence. Live publishing to production HF/Zenodo/OSF/PyPI requires API tokens, org access, and credentials which are runtime secrets.
