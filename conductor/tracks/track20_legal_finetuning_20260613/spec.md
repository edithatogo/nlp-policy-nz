# Track 20: NZ Legal NLP Model Fine-Tuning Pipeline

**Dependencies**: Track 5 (Semantic Layer), Track 6 (Storage Layer)
**Parallelization Node**: Model Fine-Tuning & Domain Adaptation
**Status**: Pending

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
