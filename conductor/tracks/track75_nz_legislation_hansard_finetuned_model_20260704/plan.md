# Track 75: NZ Legislation/Hansard Fine-Tuned Model

**Status**: planned
**Dependencies**: Tracks 74, 20, 53
**Parallelization Node**: Model Fine-Tuning and Evaluation

## Phase 1: Training Readiness

- [ ] Task: Freeze the Track 74 held-out evaluation set and select the baseline model.
- [ ] Task: Define the training recipe, seeds, and artifact layout for the fine-tuning run.
- [ ] Task: Write failing tests for configuration loading, artifact naming, and deterministic inputs.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Training Readiness' (Protocol in workflow.md)

## Phase 2: Fine-Tuning and Comparison

- [ ] Task: Implement the fine-tuning pipeline for the selected model.
- [ ] Task: Evaluate the trained model on the Track 74 held-out set.
- [ ] Task: Compare the trained model against the baseline and record the deltas.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Fine-Tuning and Comparison' (Protocol in workflow.md)

## Phase 3: Release Decision and Fallback

- [ ] Task: Package the resulting artifact, model card, and run record.
- [ ] Task: Document the promotion or deferral decision and the rollback or fallback path.
- [ ] Task: Update the conductor registry and any required project mirror records for the new track.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Release Decision and Fallback' (Protocol in workflow.md)
