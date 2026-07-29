# Plan: Track 104 CI tiering & publish honesty

Track issue: [#201](https://github.com/edithatogo/nlp-policy-nz/issues/201)

## Phase 0: PR fast lane ([#216](https://github.com/edithatogo/nlp-policy-nz/issues/216))

- [ ] Task: Red — workflow contract tests / documented matrix assertions
- [ ] Task: Green — split `ci.yml` (or add workflow) for PR fast vs full matrix
- [ ] Task: Keep SAST/SBOM on Ubuntu 3.12 PR path
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 1: Publish honesty ([#217](https://github.com/edithatogo/nlp-policy-nz/issues/217))

- [ ] Task: Document HF/Zenodo/PyPI/OSF sandbox vs production gates
- [ ] Task: Cross-link Track 45/release workflows; no false hosted claims
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Self-heal & experimental policy ([#218](https://github.com/edithatogo/nlp-policy-nz/issues/218))

- [ ] Task: Require label/approval for self-heal merge path
- [ ] Task: Move Mojo/experimental off PR critical path
- [ ] Task: Note Dependabot vs Renovate policy
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
