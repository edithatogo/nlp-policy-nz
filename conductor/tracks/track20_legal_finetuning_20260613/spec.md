# Track 20: NZ Legal NLP Model Fine-Tuning Pipeline

**Dependencies**: Track 5 (Semantic Layer), Track 6 (Storage Layer)
**Parallelization Node**: Model Fine-Tuning & Domain Adaptation
**Status**: In Progress

---

## Goal

Fine-tune a curated selection of SOTA open-source language models on NZ legislative and Hansard corpora for domain-adapted legal NLP. Produce domain-adapted model variants that outperform generic pre-trained models on NZ-specific legal tasks (citation extraction, obligation detection, entity resolution, Te Reo Māori preservation).

## Model Selection Strategy

Models are selected across three tiers based on availability, efficiency, and relevance to NZ legal NLP:

### Tier 1 — Legal Domain Specialists (foundation for NZ adaptation)

| Model | Params | Why |
|-------|--------|-----|
| **Legal-BERT** (nlpaueb/legal-bert-base-uncased) | 110M | Already in codebase; ideal for MLM fine-tuning on NZ legislation |
| **SaulLM-7B** (Equall/SaulLM-7B) | 7B | Legal domain pre-trained; strong baseline for zero-shot legal tasks |
| **SaulLM-141B** (Equall/SaulLM-141B) | 141B | Largest legal-specialised model; MoE architecture |

### Tier 2 — SOTA General-Purpose Open Models (cross-domain transfer)

| Model | Family | Params | Why |
|-------|--------|--------|-----|
| **Gemma 3** (Google) | Gemma | 2B / 9B / 27B | Strong multilingual tokenizer, open weights, efficient |
| **Phi-4** (Microsoft) | Phi | 14B | Compact, strong reasoning, MIT license |
| **Qwen 2.5** (Alibaba) | Qwen | 7B / 14B / 32B / 72B | Excellent multilingual support, strong instruction following |
| **Mistral NeMo** (Mistral) | Mistral | 12B | Apache 2.0, efficient architecture, strong EU legal coverage |
| **MiniCPM5** (OpenBMB) | MiniCPM | 5B | Exceptional small-model quality, strong OCR/document understanding |
| **Liquid LFM 7B** (Liquid AI) | LFM | 7B / 40B | Novel architecture, strong efficiency |

### Tier 3 — Long-Context & Specialized

| Model | Family | Params | Why |
|-------|--------|--------|-----|
| **Kimi** (Moonshot AI) | Kimi | 32B | Native long-context (128K+), ideal for full Acts |
| **Exaone 3.5** (LG) | Exaone | 8B / 32B | Strong multilingual transfer, Apache 2.0 |
| **Jamba 1.5** (AI21) | Jamba | 52B (MoE) | Hybrid SSM-Transformer, 256K context, strong on legal |
| **MiniMax-01** (MiniMax) | MiniMax | 456B (MoE) | 4M context window, extreme long-document capability |

## Training Tasks

| Task | Description | Evaluation Metric |
|------|-------------|-------------------|
| **MLM Fine-Tuning** | Masked Language Model adaptation on NZ legal/Hansard text | Perplexity on held-out sections |
| **Citation Extraction** | Fine-tune for NZ Act/Section citation span detection | Token-level F1 |
| **Deontic Classification** | Fine-tune for obligation/permission/prohibition classification | Macro F1 |
| **Entity Linking** | Fine-tune for NZ entity resolution (MPs, parties, electorates) | Precision@1, Recall@5 |
| **Te Reo Māori Preservation** | Fine-tune to reduce token fragmentation of Māori words | Māori token integrity score |
| **Domain QA** | Fine-tune for NZ legislation question answering | Exact Match, F1 |

## Infrastructure

- **Hardware**: GPU nodes with 4× H100 (80GB) or A100 (80GB) for 7B+ models; single GPU for BERT-scale
- **Framework**: Hugging Face Transformers + TRL (Transformer Reinforcement Learning) + PEFT (LoRA/QLoRA)
- **Quantization**: bitsandbytes 4-bit QLoRA for models >7B parameters
- **Data**: Parquet-processed corpora from Tracks 4-6
- **Tracking**: Weights & Biases for experiment logging; Hugging Face Hub for model publishing

## Acceptance Criteria

- [ ] MLM fine-tuned Legal-BERT achieves lower perplexity on NZ legal text than baseline
- [ ] At least 3 Tier-2 models fine-tuned with QLoRA on citation extraction task
- [ ] Domain-adapted models show >10% improvement on citation F1 vs base
- [ ] Te Reo Māori token integrity improved by >15% in fine-tuned tokenizers
- [ ] All fine-tuned models published to Hugging Face Hub under nlp-policy-nz namespace
- [ ] Test coverage > 90%

## Current Evidence Boundary

- Repo-side fine-tuning scaffolding and dry-run evidence are implemented and tested.
- `semantic.finetune` is dry-run/spec-only by default and requires `--run-training` before dataset loading, model download, or Hugging Face push.
- The model-quality acceptance criteria above remain unchecked until CUDA-backed training, held-out evaluation, and Hub publication evidence exist.
- Track-scoped training-package coverage evidence is 93%; full acceptance remains open because the trained-model gates are not satisfied.
- Current evidence does not claim completed CUDA training, held-out model-quality improvements, or Hugging Face Hub publication.


### Tier 4 — Legal-Domain Australian/NZ Specialist Models

| Model | Family | Params | Why |
|-------|--------|--------|-----|
| **Open Australian Legal LLM** (isaacus) | GPT-2 XL fine-tune | 1.5B | Closest legal domain to NZ (common law, shared heritage). Apache 2.0. |
| **Open Australian Legal Phi 1.5** (isaacus) | Phi-1.5 fine-tune | 1.3B | Smaller variant for rapid iteration |
| **EmuBERT** (isaacus) | BERT fine-tune | 124M | Legal MLM for embedding tasks |
| **Kanon 2 Embedder** (isaacus) | Custom legal foundation | Proprietary | #1 on MLEB — beats OpenAI by 9%, Gemini by 6%, 30% faster. 38 jurisdictions. |
| **Open Australian Legal Corpus** (isaacus) | Dataset | 147K docs | Largest open corpus of Australian law, directly transferable to NZ |
| **MLEB Benchmark** (isaacus) | Benchmark | 6 jurisdictions | Extend to NZ as 7th jurisdiction |

## Key Isaacus Resources

- **GitHub**: https://github.com/isaacus-dev (semchunk, Blackstone Graph, MLEB code)
- **HF Organization**: https://huggingface.co/isaacus (7 models, 24 datasets)
- **Open Australian Legal Corpus**: 147K laws/regulations from 6 Australian jurisdictions
- **Legal RAG Bench**: End-to-end evaluation for legal retrieval augmentation
- **MLEB**: Covers US, UK, EU, Australia, Singapore, Ireland — extend to NZ
- **semchunk**: AI-powered legal document chunking library
- **Blackstone Graph**: Graph-based legal knowledge representation (announced June 2026)
