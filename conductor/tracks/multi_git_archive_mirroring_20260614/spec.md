# Specification - Multi-Git and Multi-Archive Mirroring

## Overview
This track implements multi-git repository mirroring and backup publishing strategies for the `nlp-policy-nz` analysis framework and model outputs to guarantee durability and prevent censorship or single-point-of-failure repository/dataset takedowns.

## Requirements
1. **Multi-Git Mirroring**: Automatically push codebase updates to secondary Git remotes (GitLab and Codeberg) on every push to the canonical branches.
2. **Multi-Archive Datasets**: Redundantly archive datasets. In addition to Hugging Face, establish plans for publishing annual or periodic snapshots to Zenodo (requesting a DOI) and optional review/mirror packages to OSF.

## Acceptance Criteria
- `.github/workflows/mirror_sync.yml` exists and triggers on pushes to main/master branches.
- Workflow successfully executes dry-run or bypasses when credentials are empty.
- Multi-archive strategy defines Hugging Face (active), Zenodo (planned), and OSF (optional future) targets.
