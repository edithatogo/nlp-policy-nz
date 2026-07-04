# Track 75: NZ Legislation/Hansard Fine-Tuned Model

**Status**: archived
**Dependencies**: Tracks 74, 20, 53
**Parallelization Node**: Model Fine-Tuning and Evaluation

## Phase 1: Training Readiness

- [x] Task: Freeze the Track 74 held-out evaluation set and select the baseline model.
- [x] Task: Define the training recipe, seeds, and artifact layout for the fine-tuning run.
- [x] Task: Write failing tests for configuration loading, artifact naming, and deterministic inputs.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Training Readiness' (Protocol in workflow.md)

## Phase 2: Fine-Tuning and Comparison

- [x] Task: Implement the fine-tuning pipeline for the selected model.
- [x] Task: Evaluate the trained model on the Track 74 held-out set.
- [x] Task: Compare the trained model against the baseline and record the deltas.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Fine-Tuning and Comparison' (Protocol in workflow.md)

## Phase 3: Release Decision and Fallback

- [x] Task: Package the resulting artifact, model card, and run record.
- [x] Task: Document the promotion or deferral decision and the rollback or fallback path.
- [x] Task: Update the conductor registry and any required project mirror records for the new track.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Release Decision and Fallback' (Protocol in workflow.md)

## Implementation Notes

- The closeout is repo-side and deterministic. The run record, model card, and evidence files are archived with the track.
- The comparison currently defers promotion because Track 74 remains below the promotion threshold and no live fine-tuned weights are published yet.
- Closeout commit: `06fe8d3`
