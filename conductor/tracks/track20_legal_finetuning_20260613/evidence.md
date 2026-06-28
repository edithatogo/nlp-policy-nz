# Track 20 Evidence

## Repo-Side Status

- Training data preparation contracts: satisfied
- Task mix support for MLM, citation, deontic, entity, argument, and stance examples: satisfied
- Legal-BERT MLM job spec: satisfied
- Tier-2 QLoRA job specs: satisfied for Gemma, Phi-4, Qwen, Mistral, and additional compatible task specs
- Fine-tune command surfaces: dry-run/spec-only by default
- Track-scoped training package coverage: 93%

## Acceptance Gate Status

- Repo-side contracts: satisfied
- CUDA validation: pending
- Legal-BERT held-out perplexity improvement: pending
- At least 3 completed Tier-2 QLoRA fine-tunes: pending
- Citation F1 improvement greater than 10%: pending
- Te Reo Maori token integrity improvement greater than 15%: pending
- Hugging Face publication evidence: pending

## Non-Claim Boundary

- No CUDA-backed training run is evidenced in this track package.
- No held-out perplexity, citation F1, or Te Reo Maori token-integrity improvement is evidenced.
- No Hugging Face Hub model publication or model-card publication is evidenced.
- Dry-run JSON and shell entrypoint checks prove command/spec surfaces only; they do not prove model download, training, evaluation, or upload.

## Validation

- `python -m json.tool conductor\tracks\track20_legal_finetuning_20260613\metadata.json` passed.
- `python -m json.tool conductor\tracks\track20_legal_finetuning_20260613\finetune_dry_run_evidence_20260622.json` passed.
- `python -B -m pytest -p no:cacheprovider -q tests\test_track20_evidence.py tests\test_semantic_finetune_dry_run.py tests\test_training_data.py tests\test_training_eval.py --basetemp C:\tmp\nlp-policy-nz-track20-final` passed: 18 tests, 2 SWIG deprecation warnings.
- `python -m ruff check --no-cache src\nlp_policy_nz\training src\nlp_policy_nz\semantic\finetune.py tests\test_track20_evidence.py tests\test_semantic_finetune_dry_run.py tests\test_training_data.py tests\test_training_eval.py` passed.
- `python -B -m py_compile src\nlp_policy_nz\semantic\finetune.py src\nlp_policy_nz\training\run_qlora.py src\nlp_policy_nz\training\track20_evidence.py src\nlp_policy_nz\training\trainers.py` passed.
- `set PYTHONPATH=src&& python -B -m nlp_policy_nz.semantic.finetune --help` passed and shows `--run-training` as the live-training gate.
- `set PYTHONPATH=src&& python -B -m nlp_policy_nz.training.run_qlora --model-name google/gemma-3-9b --task citation --output-dir models/gemma-3-9b-citation --hub-model-id nlp-policy-nz/gemma-3-9b-citation --print-spec` passed.
- `python -B -m pytest -p no:cacheprovider -q tests\test_training_data.py tests\test_training_eval.py tests\test_track20_evidence.py tests\test_semantic_finetune_dry_run.py` passed: 19 passed.
- `python -m ruff check --no-cache src\nlp_policy_nz\training src\nlp_policy_nz\semantic\finetune.py tests\test_training_data.py tests\test_training_eval.py tests\test_track20_evidence.py tests\test_semantic_finetune_dry_run.py` passed.

## Residual External Gates

- Provision a CUDA/GPU environment and record `nvidia-smi`/runtime evidence.
- Run Legal-BERT MLM training on real NZ legal/Hansard Parquet inputs and compare held-out perplexity against the baseline model.
- Complete at least 3 Tier-2 QLoRA fine-tunes and record model artifact hashes.
- Evaluate held-out citation F1 and Te Reo Maori token integrity improvements against base models.
- Publish final adapted models and model cards to the Hugging Face `nlp-policy-nz` namespace.
