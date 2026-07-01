# Track 20: NZ Legal NLP Model Fine-Tuning Pipeline

**Dependencies**: Track 5, Track 6
**Parallelization Node**: Model Fine-Tuning & Domain Adaptation
**Status**: In Progress

---

## Phase 1: Infrastructure & Data Preparation

**Estimated Effort**: Medium
**Status**: Complete (repo-side), adaptive local/CI runtime validated

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Audit local/CI runtime availability and configure backend-adaptive execution with CPU, CI CPU, and optional accelerated backends | [x] | local runtime evidence: `local_cpu`; CI evidence: `ci_cpu`; accelerated backends optional |
| 1.2 | Prepare training datasets from Parquet corpora: create train/val/test splits for MLM, citation, deontic, entity tasks | [x] | local |
| 1.3 | Create `src/nlp_policy_nz/training/` package with task-specific data collators and tokenizers | [x] | local |
| 1.4 | Add MLM fine-tuning support to `src/nlp_policy_nz/semantic/finetune.py` (already scaffolds exist) | [x] | local |
| 1.5 | Write data preparation validation tests | [x] | local |

## Phase 2: Tier 1 — Legal Domain Specialist Fine-Tuning

**Estimated Effort**: Low (BERT-scale)
**Status**: Pending measured training/evaluation beyond CPU smoke/spec coverage

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Fine-tune **Legal-BERT** with MLM on NZ legislation + Hansard (100K steps, batch=32, lr=2e-5) | [ ] | |
| 2.2 | Evaluate perplexity on held-out NZ legal text vs baseline Legal-BERT | [ ] | |
| 2.3 | Fine-tune Legal-BERT for citation extraction (NER-style) using annotated NZ Act citations | [ ] | |
| 2.4 | Push domain-adapted Legal-BERT to Hugging Face Hub as `nlp-policy-nz/legal-bert-nz` | [ ] | |
| 2.5 | Write evaluation benchmarks and document results | [ ] | |

## Phase 3: Tier 2 — SOTA General-Purpose Model Fine-Tuning (QLoRA)

**Estimated Effort**: High (7B+ models)
**Status**: Pending accelerated or reduced-scope execution depending on environment

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Fine-tune **Gemma 3 (9B)** with QLoRA (rank=16, target=all linear) on citation extraction | [ ] | |
| 3.2 | Fine-tune **Phi-4 (14B)** with QLoRA on citation + deontic classification | [ ] | |
| 3.3 | Fine-tune **Qwen 2.5 (7B)** with QLoRA on NZ legislation QA | [ ] | |
| 3.4 | Fine-tune **Mistral NeMo (12B)** with QLoRA on entity linking | [ ] | |

## Phase 3b: Tier 4 — Isaacus Legal Specialist Fine-Tuning (NZ-Australia Transfer)

**Estimated Effort**: Low-Medium
**Status**: Pending accelerated or reduced-scope execution depending on environment

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3b.1 | Download Open Australian Legal LLM (1.5B) from Hugging Face; evaluate zero-shot on NZ legal benchmark | [ ] | |
| 3b.2 | Continue pre-training Open Australian Legal LLM on NZ legislation corpus (domain transfer AU→NZ) | [ ] | |
| 3b.3 | Fine-tune Open Australian Legal LLM on NZ citation extraction + deontic classification | [ ] | |
| 3b.4 | Evaluate Kanon 2 Embedder for NZ legal retrieval via API; compare vs in-house embeddings | [ ] | |
| 3b.5 | Download Open Australian Legal Corpus (AU law) + merge with NZ corpus for cross-training | [ ] | |
| 3b.6 | Push NZ-adapted AU Legal LLM to Hugging Face Hub as `nlp-policy-nz/australian-legal-llm-nz` | [ ] | |

| 3.5 | Fine-tune **MiniCPM5** with QLoRA on Te Reo Māori preservation | [ ] | |
| 3.6 | Fine-tune **Liquid LFM 7B** with QLoRA on all task mixture | [ ] | |
| 3.7 | Evaluate all models on shared benchmark suite, produce leaderboard | [ ] | |
| 3.8 | Push best-performing variant per task to Hugging Face Hub | [ ] | |

## Phase 4: Tier 3 — Long-Context & Specialized Fine-Tuning

**Estimated Effort**: High (requires large GPU memory)
**Status**: Pending large-model execution on suitable external/runtime backend

| # | Task | Status | Commit |
|---|------|--------|--------|
| 4.1 | Fine-tune **Jamba 1.5 (52B)** with QLoRA on full-Act citation extraction (128K context) | [ ] | |
| 4.2 | Fine-tune **Kimi (32B)** on long-document legal QA | [ ] | |
| 4.3 | Fine-tune **Exaone 3.5 (8B)** for NZ entity linking cross-lingual | [ ] | |
| 4.4 | Fine-tune **MiniMax-01** extreme long-context (256K+ tokens) for omnibus bill analysis | [ ] | |
| 4.5 | Evaluate long-context models on multi-section citation tasks | [ ] | |

## Phase 5: Model Evaluation & Benchmarking

**Estimated Effort**: Medium
**Status**: Pending trained-model artefacts and held-out benchmark evidence

| # | Task | Status | Commit |
|---|------|--------|--------|
| 5.1 | Create `nlp-policy-nz-eval` benchmark suite: citation F1, deontic F1, entity P@1, Māori token integrity, domain QA EM/F1 | [ ] | |
| 5.2 | Run all fine-tuned models through benchmark, produce comparison tables | [ ] | |
| 5.3 | Select final model(s) for production pipeline integration | [ ] | |
| 5.4 | Publish evaluation results and model cards to Hugging Face | [ ] | |
| 5.5 | Run full pipeline integration test with selected model(s) | [ ] | |

## Files to Create/Modify

| File | Action |
|------|--------|
| `src/nlp_policy_nz/training/__init__.py` | Create |
| `src/nlp_policy_nz/training/data.py` | Create |
| `src/nlp_policy_nz/training/trainers.py` | Create |
| `src/nlp_policy_nz/training/eval.py` | Create |
| `src/nlp_policy_nz/semantic/finetune.py` | Modify |
| `scripts/finetune_legal_bert.sh` | Create |
| `scripts/finetune_gemma.sh` | Create |
| `scripts/finetune_phi4.sh` | Create |
| `scripts/finetune_qwen.sh` | Create |
| `scripts/finetune_mistral.sh` | Create |
| `tests/test_training_data.py` | Create |
| `tests/test_training_eval.py` | Create |
| `src/nlp_policy_nz/training/track20_evidence.py` | Create |
| `tests/test_track20_evidence.py` | Create |
| `tests/test_semantic_finetune_dry_run.py` | Create |
| `conductor/tracks/track20_legal_finetuning_20260613/evidence.md` | Create |
| `conductor/tracks/track20_legal_finetuning_20260613/finetune_dry_run_evidence_20260622.json` | Create |

## Implementation Notes

| Date | Agent | Notes | Validation |
|------|-------|-------|------------|
| 2026-06-21 | codex_gpt5_engineer | Added `nlp_policy_nz.training` with deterministic Parquet-to-task example preparation, train/validation/test splitting, lightweight MLM collator, evaluation metrics, serializable Legal-BERT and QLoRA job specs, and a QLoRA spec CLI. Updated `semantic/finetune.py` to keep heavy Hugging Face/Torch imports lazy and expose a Track 20 MLM job spec. Added fine-tuning shell entrypoints for Legal-BERT, Gemma, Phi-4, Qwen, and Mistral. Added training dependencies for `accelerate`, `peft`, `trl`, `wandb`, and Linux-gated `flash-attn`. Local GPU audit: `nvidia-smi` is unavailable in this environment, so CUDA execution remains unvalidated. | Red phase confirmed: Track 20 tests initially failed because `nlp_policy_nz.training` did not exist. Focused tests now pass with `python -B -m pytest tests\test_training_data.py tests\test_training_eval.py -p no:cacheprovider -q` (13 passed). Coverage: `python -B -m coverage report --data-file=.tmp\coverage\track20c.coverage --include=src\nlp_policy_nz\training\* -m` reports 93%. Strict targeted Ruff passed. CLI smokes with `PYTHONPATH=src`: QLoRA spec print and `semantic.finetune --help` passed. Remaining: real CUDA environment validation, dataset-scale training runs, model evaluation, and Hugging Face publishing. |
| 2026-06-22 | implementer_subagent_b | Tightened the semantic fine-tune CLI and shell entrypoints into auditable dry-run surfaces. `semantic.finetune` now emits JSON evidence by default and requires explicit `--run-training` before loading datasets/models or pushing to Hugging Face. All `scripts/finetune_*.sh` entrypoints pass spec-print flags by default. Added `finetune_dry_run_evidence_20260622.json` for machine-readable claim boundaries. | Passed: `set PYTHONPATH=src&& python -B -m nlp_policy_nz.semantic.finetune --help`; `set PYTHONPATH=src&& python -B -m nlp_policy_nz.semantic.finetune --model-name nlpaueb/legal-bert-base-uncased --output-dir models/legal-bert-nz --batch-size 32 --learning-rate 2e-5 --hub-model-id nlp-policy-nz/legal-bert-nz --print-spec`; `set PYTHONPATH=src&& python -B -m nlp_policy_nz.training.run_qlora --model-name google/gemma-3-9b --task citation --output-dir models/gemma-3-9b-citation --hub-model-id nlp-policy-nz/gemma-3-9b-citation --print-spec`; `bash -n scripts/finetune_legal_bert.sh scripts/finetune_gemma.sh scripts/finetune_phi4.sh scripts/finetune_qwen.sh scripts/finetune_mistral.sh`. Live training, CUDA validation, dataset-scale evaluation, and Hub publishing remain external gates. |
| 2026-06-22 | codex_review | Added `track20_evidence.py` and focused tests that separate satisfied repo-side contracts from pending external model gates. Patched the semantic dry-run job spec to preserve requested CLI hyperparameters such as `--num-epochs`. Added `evidence.md` as the Track 20 closeout note for current repo-side evidence. | Passed: `python -B -m pytest -p no:cacheprovider -q tests\test_track20_evidence.py tests\test_semantic_finetune_dry_run.py tests\test_training_data.py tests\test_training_eval.py --basetemp C:\tmp\nlp-policy-nz-track20-final` (18 passed, 2 SWIG deprecation warnings). Passed: `python -m ruff check --no-cache src\nlp_policy_nz\training src\nlp_policy_nz\semantic\finetune.py tests\test_track20_evidence.py tests\test_semantic_finetune_dry_run.py tests\test_training_data.py tests\test_training_eval.py`. Passed: `python -B -m py_compile src\nlp_policy_nz\semantic\finetune.py src\nlp_policy_nz\training\run_qlora.py src\nlp_policy_nz\training\track20_evidence.py src\nlp_policy_nz\training\trainers.py`. |
| 2026-06-28 | codex_gpt5_engineer | Performed a Track 20 cleanup pass: normalized import order in the Track 20 training helper and dry-run test, then re-ran the focused Track 20 test surface and Ruff. | `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_training_data.py tests\test_training_eval.py tests\test_track20_evidence.py tests\test_semantic_finetune_dry_run.py` passed with 19 passed in 11.53s; `.\.venv\Scripts\python.exe -m ruff check --no-cache src\nlp_policy_nz\training src\nlp_policy_nz\semantic\finetune.py tests\test_training_data.py tests\test_training_eval.py tests\test_track20_evidence.py tests\test_semantic_finetune_dry_run.py` passed.
| 2026-07-01 | codex_gpt5_engineer | Added environment-adaptive runtime planning for Track 20. The system now selects `local_cpu` on this Windows workstation and `ci_cpu` under `CI=true`, while exposing CUDA, ROCm, MPS, DirectML, and ONNX CPU as optional backend choices when available. | `pixi run track20-runtime` selected `local_cpu`; `CI=true pixi run track20-runtime` selected `ci_cpu`; focused tests passed with 24 passed. Local profile: 22 logical CPUs, about 32 GiB RAM, Intel graphics, PyTorch `2.12.1+cpu`, no CUDA/MPS/DirectML/ONNX Runtime. |
