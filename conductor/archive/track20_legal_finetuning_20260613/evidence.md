# Track 20 Evidence

## Repo-Side Status

- Training data preparation contracts: satisfied
- Task mix support for MLM, citation, deontic, entity, argument, and stance examples: satisfied
- Legal-BERT MLM job spec: satisfied
- Tier-2 QLoRA job specs: satisfied for Gemma, Phi-4, Qwen, Mistral, and additional compatible task specs
- Fine-tune command surfaces: dry-run/spec-only by default
- Environment-adaptive runtime planning: satisfied for local CPU, GitHub Actions CPU, and optional accelerated backends
- Bounded CPU smoke training: satisfied for local CPU and GitHub Actions CPU plans
- Track-scoped training package coverage: 93%

## Acceptance Gate Status

- Repo-side contracts: satisfied
- Runtime dependency imports: satisfied
- Parquet training input availability: satisfied (519 files found under the checked roots)
- Hugging Face CLI availability: satisfied in the Pixi runtime
- Local execution plan: satisfied (`local_cpu`, CPU smoke mode, max 32 records, max 5 steps, no model download, no Hub push)
- GitHub Actions execution plan: satisfied (`ci_cpu`, CPU smoke mode, max 8 records, max 2 steps, no model download, no Hub push)
- Local CPU smoke training: satisfied (5 steps, loss decreased from 3.4447 to 3.1598)
- GitHub Actions CPU smoke training: satisfied with `CI=true` (2 steps, loss decreased from 3.4447 to 3.3707)
- Real-Parquet CPU smoke training: satisfied on a PipelineRecord Parquet fixture (5 steps, loss decreased from 2.5463 to 1.8621)
- Accelerated backend validation: optional and pending for CUDA/ROCm/MPS/DirectML when such hardware/runtime exists
- Legal-BERT held-out perplexity improvement: pending
- At least 3 completed Tier-2 QLoRA fine-tunes: pending
- Citation F1 improvement greater than 10%: pending
- Te Reo Maori token integrity improvement greater than 15%: pending
- Hugging Face publication evidence: pending

## Non-Claim Boundary

- No publication-quality accelerated training run is evidenced in this track package.
- No held-out perplexity, citation F1, or Te Reo Maori token-integrity improvement is evidenced.
- No Hugging Face Hub model publication or model-card publication is evidenced.
- Dry-run JSON, shell entrypoint checks, and adaptive runtime planning prove command/spec/runtime-selection surfaces; they do not prove full model download, long training, benchmark improvement, or upload.

## Runtime Gate Evidence

- A live local runtime probe on 2026-07-01 records the workstation's training readiness.
- Importable training stack: `torch`, `transformers`, `datasets`, `peft`, `trl`, `bitsandbytes`, and `wandb`.
- Data visibility: 519 Parquet files found under `.` and `C:\Users\60217257\OneDrive - Flinders\repos\legal-nz\corpus-law-nz`.
- Publication tooling: `hf` CLI is available inside the Pixi runtime.
- Local hardware profile: Windows, 22 logical CPUs, about 32 GiB RAM, Intel graphics, PyTorch `2.12.1+cpu`, no CUDA, no MPS, no DirectML, and no ONNX Runtime.
- Selected local plan: `local_cpu`, CPU smoke mode, max 32 records, max 5 steps, no model download, and no Hub push.
- Selected CI plan with `CI=true`: `ci_cpu`, CPU smoke mode, max 8 records, max 2 steps, no model download, and no Hub push.
- Local smoke-training result: backend `local_cpu`, 4 fixture records, 5 steps, decreasing loss.
- CI smoke-training result: backend `ci_cpu`, 4 fixture records, 2 steps, decreasing loss.
- Real-Parquet CLI smoke-training result: backend `local_cpu`, 2 PipelineRecord Parquet records, 5 steps, decreasing loss.

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
- Inline runtime probe with `PYTHONPATH=src` passed and reported 519 Parquet inputs, importable training dependencies, available `hf` CLI, unavailable CUDA, and missing `nvidia-smi`.
- `pixi run track20-runtime` passed and selected `local_cpu`.
- `CI=true pixi run track20-runtime` passed and selected `ci_cpu`.
- `pixi run track20-smoke` passed and ran local CPU smoke training with decreasing loss.
- `CI=true pixi run track20-smoke` passed and ran CI CPU smoke training with decreasing loss.
- `pixi run track20-smoke --parquet .tmp\track20-smoke-cli.parquet` passed and ran local CPU smoke training from real PipelineRecord Parquet with decreasing loss.
- `pixi run pytest -p no:tach -p no:cacheprovider -q tests\test_track20_runtime.py` passed: 10 passed.
- `pixi run pytest -p no:tach -p no:cacheprovider -q tests\test_track20_runtime.py tests\test_track20_evidence.py tests\test_semantic_finetune_dry_run.py tests\test_training_data.py tests\test_training_eval.py` passed: 27 passed.

## Residual External Gates

- Run Legal-BERT MLM training on real NZ legal/Hansard Parquet inputs using the best available backend and compare held-out perplexity against the baseline model.
- Complete at least 3 Tier-2 QLoRA fine-tunes on a suitable accelerated backend and record model artifact hashes.
- Evaluate held-out citation F1 and Te Reo Maori token integrity improvements against base models.
- Publish final adapted models and model cards to the Hugging Face `nlp-policy-nz` namespace.
