# Track 74: NZ Legal/Hansard Held-Out Evaluation Set

**Status**: planned
**Dependencies**: Tracks 13, 19, 20, 23, 53
**Parallelization Node**: Model Evaluation Data Infrastructure

## Phase 1: Split Design and Provenance Rules

- [ ] Task: Define the held-out split policy for legislation and Hansard sources.
- [ ] Task: Specify provenance fields, hashes, and split metadata required for each example.
- [ ] Task: Write failing tests that prove split determinism and leakage rejection.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Split Design and Provenance Rules' (Protocol in workflow.md)

## Phase 2: Dataset Build and Validation Harness

- [ ] Task: Implement the dataset builder for the held-out evaluation set.
- [ ] Task: Add validation checks for source overlap, schema drift, and missing provenance.
- [ ] Task: Implement a reproducible evaluation harness that consumes the held-out split.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Dataset Build and Validation Harness' (Protocol in workflow.md)

## Phase 3: Baseline Evidence and Promotion Gate

- [ ] Task: Record baseline scores for the current model candidates on the held-out set.
- [ ] Task: Document the promotion threshold and decision criteria for the future fine-tuning track.
- [ ] Task: Update the conductor registry and any required project mirror records for the new track.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Baseline Evidence and Promotion Gate' (Protocol in workflow.md)
