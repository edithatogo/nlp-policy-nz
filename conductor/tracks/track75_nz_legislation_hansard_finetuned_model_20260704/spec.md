# Track 75: NZ Legislation/Hansard Fine-Tuned Model

## Overview

Fine-tune a model on NZ legislation and Hansard only after the held-out evaluation set proves there is a defensible baseline and a meaningful target for improvement.

## Requirements

- Depend on the held-out evaluation set from Track 74.
- Select a baseline model and a training recipe that is reproducible in CI or a similarly deterministic local environment.
- Preserve the public API and downstream artifact schema unless a separate migration track is introduced.
- Record the training data version, hyperparameters, seed, and model artifact hashes.
- Compare the fine-tuned model against the Track 74 baseline on the same held-out set.
- Keep a non-fine-tuned fallback path available for users and CI.

## Acceptance Criteria

- [ ] Training data, model configuration, and seeds are reproducible from tracked inputs.
- [ ] The fine-tuned model is evaluated on the Track 74 held-out set with a recorded baseline comparison.
- [ ] A model artifact, model card, and run record are produced.
- [ ] A clear promotion or deferral decision is documented from the evaluation results.
- [ ] A fallback path remains available if the fine-tuned model does not justify promotion.

## Out of Scope

- Replacing the held-out evaluation set.
- Mojo integration or runtime acceleration.
- Production serving changes.
- Public API or schema breaking changes without a separate migration track.
