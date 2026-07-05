# Track 45: Release Engineering & Automated Publishing

**Dependencies**: Tracks 8, 9, 24, 36
**Parallelization Node**: CI/CD Automation
**Status**: Planned

## Goal

Implement a fully automated release pipeline that semantically versions every merge, generates changelogs, and publishes dynamically versioned incremental updates to Hugging Face (datasets + spaces), Zenodo (DOIs), and OSF (archives) — all driven by GitHub Actions.

## Scope

### 1. Semantic Versioning & Release Metadata
- Conventional commits enforcement (already in pre-commit scope via Track 39)
- Automated version bump from commit history (`commit-and-tag-version` or `semantic-release`)
- Version manifest JSON at `VERSION.json` with semver, build-timestamp, commit-sha
- Dataset version aligned to code version (or independently versioned with cross-reference)

### 2. CI/CD Hugging Face Auto-Publish
- `.github/workflows/publish-hf-datasets.yml` — on every master merge, incrementally push new/changed Parquet datasets to HF Hub with auto-incremented dataset revision tag
- `.github/workflows/publish-hf-models.yml` — on successful Track 20/21 fine-tuning completion, push model checkpoints to HF Hub
- `.github/workflows/publish-hf-space.yml` — on every master merge, auto-deploy the Gradio exploration Space to HF Spaces

### 3. CI/CD Zenodo Auto-Deposit
- `.github/workflows/publish-zenodo.yml` — on version tag (v*), create Zenodo deposition with dataset snapshot, model archive, and provenance metadata
- Auto-generate CITATION.cff from VERSION.json and metadata
- DOI badge auto-update in README.md on release

### 4. CI/CD OSF Auto-Archive
- `.github/workflows/publish-osf.yml` — on version tag (v*), push dataset + model archive to OSF project storage
- OSF project skeleton with README, data, and code subdirectories

### 5. Automated Changelog & Release Notes
- `.github/release-drafter.yml` (from Track 39) generates release notes from conventional commits
- CHANGELOG.md auto-updated on every release tag
- GitHub Release created with auto-generated notes, SBOM, and checksums

### 6. Package Publishing
- `.github/workflows/publish-pypi.yml` — on version tag, build and publish to PyPI

## Acceptance Criteria

- [ ] `git commit -m "feat: ..."` auto-bumps minor version; `fix:` bumps patch; `BREAKING CHANGE:` bumps major
- [ ] `VERSION.json` exists at repo root with semver, timestamp, and commit SHA
- [ ] Master merge triggers HF dataset upload workflow with incremental revision tags
- [ ] Master merge triggers HF Space deploy workflow
- [ ] `v*` tag triggers Zenodo deposition with dataset + model + provenance
- [ ] `v*` tag triggers OSF archive push
- [ ] `v*` tag triggers PyPI publish
- [ ] CHANGELOG.md is auto-generated on every version tag
- [ ] GitHub Release created with auto-notes, SBOM, and checksums
- [ ] CITATION.cff auto-generated on release
- [ ] All CI/CD workflows pass end-to-end in a dry-run sandbox environment
