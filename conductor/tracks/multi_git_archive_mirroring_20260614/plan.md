# Plan - Multi-Git and Multi-Archive Mirroring

## Phase 1: Git Remote Mirror Setup
- [x] Task: Write `.github/workflows/mirror_sync.yml` to support automated SSH mirroring to secondary Git remotes (GitLab/Codeberg). (abdcf8b)
- [x] Task: Configure repository secrets `GIT_MIRROR_URL` and `GIT_MIRROR_SSH_PRIVATE_KEY` on GitHub. (abdcf8b)
- [x] Task: Verify successful manual and push triggers for mirror sync. (abdcf8b)

## Phase 2: Zenodo & OSF Mirroring Integration
- [x] Task: Document Zenodo archival publication schema and script requirements. (b4db2e3)
- [x] Task: Design OSF optional mirror convenience policy matching sister Hansard/Legislation corpora. (b4db2e3)
- [x] Task: Conductor - User Manual Verification 'Phase 2: Zenodo & OSF Mirroring Integration' (Protocol in workflow.md) (e3119b7)
