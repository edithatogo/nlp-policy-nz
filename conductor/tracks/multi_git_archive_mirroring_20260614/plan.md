# Plan - Multi-Git and Multi-Archive Mirroring

## Phase 1: Git Remote Mirror Setup
- [x] Task: Write `.github/workflows/mirror_sync.yml` to support automated SSH mirroring to secondary Git remotes (GitLab and Codeberg). (c4f245e)
- [x] Task: Configure repository secrets `GITLAB_MIRROR_URL`, `CODEBERG_MIRROR_URL`, and `GIT_MIRROR_SSH_PRIVATE_KEY` on GitHub. (manual verification required)
- [x] Task: Verify safe workflow behavior for missing mirror URLs or SSH credentials. (pending)
- [x] Task: Add workflow contract tests for canonical branch triggers, GitLab/Codeberg targets, and empty-credential bypass. (pending)

## Phase 2: Zenodo & OSF Mirroring Integration
- [x] Task: Document Zenodo archival publication schema and script requirements. (b4db2e3)
- [x] Task: Design OSF optional mirror convenience policy matching sister Hansard/Legislation corpora. (b4db2e3)
- [x] Task: Conductor - User Manual Verification 'Phase 2: Zenodo & OSF Mirroring Integration' (Protocol in workflow.md) (e3119b7)
