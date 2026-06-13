# Track 22: Isaacus Legal NLP Ecosystem Integration

**Dependencies**: Track 20 (Fine-Tuning), Track 5 (Semantic Layer)
**Parallelization Node**: Legal Knowledge Integration
**Status**: Pending

---

## Goal

Integrate the Isaacus legal NLP ecosystem — the most comprehensive open-source legal AI stack — into the nlp-policy-nz pipeline. Isaacus (Australia) is the closest existing legal NLP effort to NZ's needs, sharing common law heritage and statutory interpretation patterns. This track covers dataset integration, benchmark extension, model evaluation, and tool adoption.

## Isaacus Ecosystem Overview

### Models (HF: isaacus/*)

| Model | Type | Params | License | Relevance |
|-------|------|--------|---------|-----------|
| `open-australian-legal-llm` | Text generation (GPT-2 XL) | 1.5B | Apache 2.0 | Fine-tune on NZ law; best AU→NZ transfer baseline |
| `open-australian-legal-phi-1_5` | Text generation (Phi-1.5) | 1.3B | Apache 2.0 | Smaller, faster iteration |
| `open-australian-legal-gpt2` | Text generation | 124M | Apache 2.0 | Baseline comparison |
| `emubert` | Fill-Mask (BERT) | 124M | Apache 2.0 | Legal MLM for embedding comparison |
| `kanon-2-tokenizer` | Tokenizer | — | — | Legal-domain tokenizer for evaluation |
| `kanon-tokenizer` | Tokenizer | — | — | Legacy legal tokenizer |

### Kanon 2 Embedder (Proprietary — API/Air-Gapped)

- **#1 on MLEB** as of Oct 2025 — beats OpenAI Text Embedding 3 Large by 9%
- 30% faster inference than comparably accurate models
- Trained on millions of documents from 38 jurisdictions
- Available via Isaacus API or air-gapped AWS/Azure Marketplace containers
- **Action**: Evaluate on NZ legal retrieval; if superior, adopt as embedding backend

### Key Datasets (HF: isaacus/*)

| Dataset | Records | Description |
|---------|---------|-------------|
| `open-australian-legal-corpus` | 147K | Laws, regulations, decisions from 6 AU jurisdictions. **Directly supplement NZ training data** |
| `open-australian-legal-qa` | 2.1K | QA pairs over AU legal corpus. Template for NZ legal QA dataset |
| `legal-rag-bench` | 4.9K | End-to-end legal RAG evaluation benchmark |
| `mleb-legal-rag-bench` | 5K | MLEB retrieval benchmark dataset |
| `high-court-of-australia-cases` | 8.1K | Full HCA decisions |
| `uk-legislative-long-titles` | 234 | UK legislative titles (common law comparison) |
| `australian-tax-guidance-retrieval` | 329 | Tax domain retrieval |
| `contractual-clause-retrieval` | 225 | Contract clause retrieval |

### Key Tools

| Tool | Repository | Description |
|------|-----------|-------------|
| **semchunk** | github.com/isaacus-dev/semchunk | AI-powered legal document chunking. Evaluate vs our `syntactic/chunking.py` |
| **Blackstone Graph** | Announced June 2026 | Graph-based legal knowledge representation. Monitor for integration. |
| **MLEB** | HF: isaacus/mleb-* | Massive Legal Embedding Benchmark. Extend to NZ as 7th jurisdiction. |

## Integration Tasks

### 1. Dataset Integration
- Download and normalize Open Australian Legal Corpus for cross-training with NZ data
- Create NZ-AU merged training corpus for fine-tuning
- Build NZ legal QA dataset following Open Australian Legal QA template

### 2. Model Integration
- Fine-tune Open Australian Legal LLM on NZ legislation (domain transfer)
- Evaluate Kanon 2 Embedder for NZ legal retrieval
- Compare all Isaacus models against our fine-tuned models

### 3. Benchmark Extension
- Extend MLEB with NZ jurisdiction (NZ legislation, Hansard, court decisions)
- Run NZ-extended MLEB to establish baselines
- Publish NZ-MLEB results

### 4. Tool Adoption
- Evaluate semchunk vs our chunking for legal document segmentation
- Monitor Blackstone Graph for potential integration with our PolicyGraph

## Acceptance Criteria

- [ ] Open Australian Legal Corpus downloaded, normalized, and merged with NZ corpus
- [ ] Open Australian Legal LLM fine-tuned on NZ law and evaluated (AU→NZ transfer)
- [ ] Kanon 2 Embedder evaluated on NZ legal retrieval tasks
- [ ] MLEB extended to include NZ jurisdiction
- [ ] NZ-MLEB baselines published
- [ ] semchunk evaluated vs existing chunking
- [ ] Blackstone Graph monitored for integration opportunities
