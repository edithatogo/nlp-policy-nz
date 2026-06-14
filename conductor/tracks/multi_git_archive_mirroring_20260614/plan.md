# Plan - Multi-Git and Multi-Archive Mirroring

## Phase 1: Git Remote Mirror Setup
- [x] Task: Write `.github/workflows/mirror_sync.yml` to support automated SSH mirroring to secondary Git remotes (GitLab/Codeberg).
- [ ] Task: Configure repository secrets `GIT_MIRROR_URL` and `GIT_MIRROR_SSH_PRIVATE_KEY` on GitHub.
- [ ] Task: Verify successful manual and push triggers for mirror sync.

## Phase 2: Zenodo & OSF Mirroring Integration
- [ ] Task: Document Zenodo archival publication schema and script requirements.
- [ ] Task: Design OSF optional mirror convenience policy matching sister Hansard/Legislation corpora.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Zenodo & OSF Mirroring Integration' (Protocol in workflow.md)
