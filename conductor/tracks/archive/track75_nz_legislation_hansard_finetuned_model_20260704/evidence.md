# Track 75 Evidence

- Model card: `conductor/tracks/archive/track75_nz_legislation_hansard_finetuned_model_20260704/model_card.md`
- Run record: `conductor/tracks/archive/track75_nz_legislation_hansard_finetuned_model_20260704/run_record.json`
- Training baseline: `data/track74/held_out_evaluation_set.json`

## Validation

- `.\.venv\Scripts\python.exe -m pytest -q tests/test_track75_finetune.py`

## Decision

Track 75 is complete as a repo-side fine-tuning closeout. The recipe is reproducible from tracked inputs, the Track 74 comparison is recorded, and the remaining live-training and publication gates are explicit rather than implied.
