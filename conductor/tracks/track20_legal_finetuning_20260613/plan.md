# Track 20: NZ Legal NLP Model Fine-Tuning Pipeline

**Dependencies**: Track 5, Track 6
**Parallelization Node**: Model Fine-Tuning & Domain Adaptation
**Status**: Pending

---

## Phase 1: Infrastructure & Data Preparation

**Estimated Effort**: Medium
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Audit GPU availability and configure CUDA environment with `bitsandbytes`, `flash-attn`, `TRL`, `PEFT`, `wandb` | [ ] | |
| 1.2 | Prepare training datasets from Parquet corpora: create train/val/test splits for MLM, citation, deontic, entity tasks | [ ] | |
| 1.3 | Create `src/nlp_policy_nz/training/` package with task-specific data collators and tokenizers | [ ] | |
| 1.4 | Add MLM fine-tuning support to `src/nlp_policy_nz/semantic/finetune.py` (already scaffolds exist) | [ ] | |
| 1.5 | Write data preparation validation tests | [ ] | |

## Phase 2: Tier 1 — Legal Domain Specialist Fine-Tuning

**Estimated Effort**: Low (BERT-scale)
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Fine-tune **Legal-BERT** with MLM on NZ legislation + Hansard (100K steps, batch=32, lr=2e-5) | [ ] | |
| 2.2 | Evaluate perplexity on held-out NZ legal text vs baseline Legal-BERT | [ ] | |
| 2.3 | Fine-tune Legal-BERT for citation extraction (NER-style) using annotated NZ Act citations | [ ] | |
| 2.4 | Push domain-adapted Legal-BERT to Hugging Face Hub as `nlp-policy-nz/legal-bert-nz` | [ ] | |
| 2.5 | Write evaluation benchmarks and document results | [ ] | |

## Phase 3: Tier 2 — SOTA General-Purpose Model Fine-Tuning (QLoRA)

**Estimated Effort**: High (7B+ models)
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Fine-tune **Gemma 3 (9B)** with QLoRA (rank=16, target=all linear) on citation extraction | [ ] | |
| 3.2 | Fine-tune **Phi-4 (14B)** with QLoRA on citation + deontic classification | [ ] | |
| 3.3 | Fine-tune **Qwen 2.5 (7B)** with QLoRA on NZ legislation QA | [ ] | |
| 3.4 | Fine-tune **Mistral NeMo (12B)** with QLoRA on entity linking | [ ] | |
| 3.5 | Fine-tune **MiniCPM5** with QLoRA on Te Reo Māori preservation | [ ] | |
| 3.6 | Fine-tune **Liquid LFM 7B** with QLoRA on all task mixture | [ ] | |
| 3.7 | Evaluate all models on shared benchmark suite, produce leaderboard | [ ] | |
| 3.8 | Push best-performing variant per task to Hugging Face Hub | [ ] | |

## Phase 4: Tier 3 — Long-Context & Specialized Fine-Tuning

**Estimated Effort**: High (requires large GPU memory)
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 4.1 | Fine-tune **Jamba 1.5 (52B)** with QLoRA on full-Act citation extraction (128K context) | [ ] | |
| 4.2 | Fine-tune **Kimi (32B)** on long-document legal QA | [ ] | |
| 4.3 | Fine-tune **Exaone 3.5 (8B)** for NZ entity linking cross-lingual | [ ] | |
| 4.4 | Fine-tune **MiniMax-01** extreme long-context (256K+ tokens) for omnibus bill analysis | [ ] | |
| 4.5 | Evaluate long-context models on multi-section citation tasks | [ ] | |

## Phase 5: Model Evaluation & Benchmarking

**Estimated Effort**: Medium
**Status**: Pending

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
