# Track 75: NZ Legislation/Hansard Fine-Tuned Model

## Summary

This track records the reproducible fine-tuning recipe, artifact layout, and promotion decision for the NZ legislation/Hansard model follow-up to Track 74.

## Tracked Inputs

- Baseline model: `nlpaueb/legal-bert-base-uncased`
- Fallback model: `bert-base-uncased`
- Training seed: `20260704`
- Track 74 manifest: `data/track74/held_out_evaluation_set.json`
- Track 74 manifest id: `track74_nz_legal_hansard_evaluation_set_20260704`
- Promotion threshold: `0.7500`
- Track 74 baseline score: `0.7143`
- Promotion margin: `-0.0357`

## Artifact Layout

- Model output dir: `models/nz-legislation-hansard-finetuned`
- Model card: `conductor/tracks/archive/track75_nz_legislation_hansard_finetuned_model_20260704/model_card.md`
- Run record: `conductor/tracks/archive/track75_nz_legislation_hansard_finetuned_model_20260704/run_record.json`
- Fallback reference: `nlp_policy_nz.semantic.model_loader:load_model`

## Decision

- Promotion ready: `False`
- Decision: `defer`
- Reason: Track 74 baseline remains below the promotion threshold; defer live model promotion until a measured live fine-tuned run improves the held-out score

## Residual External Gates

- Live fine-tuning run on the selected model
- Measured evaluation on the Track 74 held-out set
- Model card publication with artifact hashes
- Optional Hugging Face Hub publication after promotion approval
