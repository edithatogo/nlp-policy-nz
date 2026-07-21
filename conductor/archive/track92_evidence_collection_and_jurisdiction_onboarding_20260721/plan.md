# Implementation Plan

## Phase I: Shared Evidence Contract

- [x] Task: Define the shared provenance-bearing evidence manifest (`6275c2f`).
  - [x] Map artifact IDs, hashes, source commits, rights, access, review, and promotion fields.
  - [x] Cross-reference `foi-o`, `rac-conformance`, and issues #132, #133, #143, #144.
- [x] Task: Write validation tests before implementation (`6275c2f`).
- [x] Task: Implement deterministic fail-closed validation and no-promotion reporting (`6275c2f`).
- [x] Task: Phase Verification & Checkpoint (`6275c2f`; 5 focused tests pass).

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

- [x] Task: Assemble mixed-access and inconsistent-access assurance fixtures (existing Track 133 harness).
- [x] Task: Run serializer canary, compatibility, performance, and mutation lanes (repository harness; mutation remains CI-authoritative).
- [x] Task: Link restricted sources to rights bases and reviewers in the intake contracts.
- [ ] Task: Obtain independent adversarial review of public projections (external gate; issue #133 remains open).
- [ ] Task: Archive immutable CI run IDs and closeout approval (external closeout gate; issue #133 remains open).
- [x] Task: Phase Verification & Checkpoint (repository lanes pass; external gates recorded as no-promotion).

## Phase IV: Concept-Pack and Feedback Contract (#143)

- [x] Task: Define the jurisdiction-neutral export schema against `foi-o` (`3c3fc25`).
  - [x] Add immutable artifact IDs, jurisdiction/profile/version, source, dates, rights, and review state.
  - [x] Add candidate-only status, uncertainty, conflict, and unsupported-surface fields.
- [x] Task: Define feedback submission, review, disposition, and promotion states (`3c3fc25`).
- [ ] Task: Add independent fixtures and conformance checks in `rac-conformance` (cross-repository follow-up).
- [x] Task: Integrate candidate export and feedback references into `nlp-policy-nz` (`3c3fc25`).
- [ ] Task: Obtain rights, legal, and profile-owner review (external gate; issue #143 remains open).
- [x] Task: Phase Verification & Checkpoint (5 focused tests pass).

## Phase V: Incremental Jurisdiction Onboarding (#144)

- [x] Task: Inventory roadmap jurisdictions and source regimes (`6275c2f`).
  - [ ] Legislation: `corpus-legislation-nz`, `legislation`, and `anz-legislation`.
  - [ ] FOI cases and processes: `foi-process`, `alaveteli`, and `fyi-archive`.
  - [ ] Process semantics: `process-mappings`.
- [ ] Task: Pin legislation, Gazette, guidance, and case manifests per jurisdiction (external source collection; issue #144 remains open).
- [ ] Task: Implement one jurisdiction/profile adapter at a time (follow-up implementation track; no adapter is claimed here).
- [ ] Task: Extract candidate concepts, duties, clocks, exemptions, tests, review pathways, and case events (depends on pinned sources).
- [ ] Task: Add positive, negative, temporal, and non-equivalence fixtures per jurisdiction (depends on source packs).
- [ ] Task: Run independent evaluation and retain unsupported/conflicting outputs (depends on fixtures).
- [ ] Task: Obtain jurisdiction/profile and legal review before promotion (external gate).
- [x] Task: Phase Verification & Checkpoint (empty fail-closed jurisdiction manifest committed).

## Phase VI: Closeout

- [x] Task: Publish cross-repository provenance index and evidence inventory (`6275c2f`).
- [x] Task: Update issues #132, #133, #143, and #144 with artifact links and gate status (external issue closeout remains separate).
- [x] Task: Close only issues whose acceptance criteria and human gates are demonstrably complete; leave #132, #133, #143, and #144 open where gates remain outstanding.
- [x] Task: Phase Verification & Checkpoint (repository-side implementation complete; external gates explicitly not promoted).

## Completion Boundary

Track 92 is complete as a repository-side evidence-collection and fail-closed
contract implementation. The unchecked tasks above are intentionally retained
as external or follow-up implementation gates in issues #132, #133, #143, and
#144; archiving this Conductor track does not close or promote those issues.

## Review Fixes

- [x] Task: Require explicit blocker explanations in the collection validator (`324cde2`).
