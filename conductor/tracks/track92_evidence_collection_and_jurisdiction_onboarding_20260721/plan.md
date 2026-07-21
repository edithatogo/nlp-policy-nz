# Implementation Plan

## Phase I: Shared Evidence Contract

- [ ] Task: Define the shared provenance-bearing evidence manifest.
  - [ ] Map artifact IDs, hashes, source commits, rights, access, review, and promotion fields.
  - [ ] Cross-reference `foi-o`, `rac-conformance`, and issues #132, #133, #143, #144.
- [ ] Task: Write validation tests before implementation.
- [ ] Task: Implement deterministic fail-closed validation and no-promotion reporting.
- [ ] Task: Phase Verification & Checkpoint (Refer to `conductor/workflow.md`).

## Phase II: Historical Parliament Evidence (#132)

- [ ] Task: Inventory eligible volumes and page identifiers from `corpus-nz-hansard` and `hathi-nz`.
  - [ ] Record source URI, volume, page, retrieval, access, and hash metadata only.
  - [ ] Select volume-isolated train/dev/test splits.
- [ ] Task: Obtain rights clearance and controlled storage for page images and annotations.
- [ ] Task: Register separate annotators and adjudicators with identity evidence.
- [ ] Task: Create temporal authority records for speakers and roles.
- [ ] Task: Capture signed adjudication decisions and disagreements.
- [ ] Task: Run the Track 132 evaluator and archive metrics and leakage results.
- [ ] Task: Phase Verification & Checkpoint (Refer to `conductor/workflow.md`).

## Phase III: Archive Assurance Closeout (#133)

- [ ] Task: Assemble mixed-access and inconsistent-access assurance fixtures.
- [ ] Task: Run serializer canary, compatibility, performance, and mutation lanes.
- [ ] Task: Link restricted sources to rights bases and reviewers.
- [ ] Task: Obtain independent adversarial review of public projections.
- [ ] Task: Archive immutable CI run IDs and closeout approval.
- [ ] Task: Phase Verification & Checkpoint (Refer to `conductor/workflow.md`).

## Phase IV: Concept-Pack and Feedback Contract (#143)

- [ ] Task: Define the jurisdiction-neutral export schema against `foi-o`.
  - [ ] Add immutable artifact IDs, jurisdiction/profile/version, source, dates, rights, and review state.
  - [ ] Add candidate-only status, uncertainty, conflict, and unsupported-surface fields.
- [ ] Task: Define feedback submission, review, disposition, and promotion states.
- [ ] Task: Add independent fixtures and conformance checks in `rac-conformance`.
- [ ] Task: Integrate candidate export and feedback references into `nlp-policy-nz`.
- [ ] Task: Obtain rights, legal, and profile-owner review.
- [ ] Task: Phase Verification & Checkpoint (Refer to `conductor/workflow.md`).

## Phase V: Incremental Jurisdiction Onboarding (#144)

- [ ] Task: Inventory roadmap jurisdictions and source regimes.
  - [ ] Legislation: `corpus-legislation-nz`, `legislation`, and `anz-legislation`.
  - [ ] FOI cases and processes: `foi-process`, `alaveteli`, and `fyi-archive`.
  - [ ] Process semantics: `process-mappings`.
- [ ] Task: Pin legislation, Gazette, guidance, and case manifests per jurisdiction.
- [ ] Task: Implement one jurisdiction/profile adapter at a time.
- [ ] Task: Extract candidate concepts, duties, clocks, exemptions, tests, review pathways, and case events.
- [ ] Task: Add positive, negative, temporal, and non-equivalence fixtures per jurisdiction.
- [ ] Task: Run independent evaluation and retain unsupported/conflicting outputs.
- [ ] Task: Obtain jurisdiction/profile and legal review before promotion.
- [ ] Task: Phase Verification & Checkpoint (Refer to `conductor/workflow.md`).

## Phase VI: Closeout

- [ ] Task: Publish cross-repository provenance index and evidence inventory.
- [ ] Task: Update issues #132, #133, #143, and #144 with artifact links and gate status.
- [ ] Task: Close only issues whose acceptance criteria and human gates are demonstrably complete.
- [ ] Task: Phase Verification & Checkpoint (Refer to `conductor/workflow.md`).
