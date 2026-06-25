# Track 22: Isaacus Legal NLP Ecosystem Integration

**Dependencies**: Track 20, Track 5
**Parallelization Node**: Legal Knowledge Integration
**Status**: In Progress

---

## Phase 1: Dataset Acquisition & Normalization

**Estimated Effort**: Low-Medium
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Download `isaacus/open-australian-legal-corpus` (147K docs, 6 AU jurisdictions) | [ ] | |
| 1.2 | Download `isaacus/open-australian-legal-qa` (2.1K QA pairs) | [ ] | |
| 1.3 | Download `isaacus/legal-rag-bench`, `isaacus/mleb-legal-rag-bench` | [ ] | |
| 1.4 | Normalize AU corpus to PipelineRecord format (unify with NZ Parquet schema) | [x] | |
| 1.5 | Create NZ-AU merged training corpus (Parquet) for cross-jurisdiction fine-tuning | [ ] | |
| 1.6 | Write dataset download and normalization tests | [x] | |

## Phase 2: Model Acquisition & Evaluation

**Estimated Effort**: Medium
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Download `isaacus/open-australian-legal-llm` (1.5B), run zero-shot on NZ legal benchmark | [ ] | |
| 2.2 | Download `isaacus/emubert` (124M), evaluate on NZ text encoding | [ ] | |
| 2.3 | Evaluate Kanon 2 Embedder via API on NZ legal retrieval (citation search, document similarity) | [ ] | |
| 2.4 | Evaluate `kanon-2-tokenizer` vs our tokenizer on Māori token preservation | [ ] | |
| 2.5 | Produce comparison table: Isaacus models vs our fine-tuned models on NZ tasks | [ ] | |

## Phase 3: AU→NZ Domain Transfer Fine-Tuning

**Estimated Effort**: Medium-High
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Continue-pretrain Open Australian Legal LLM on NZ corpus (MLM, 50K steps) | [ ] | |
| 3.2 | Fine-tune AU→NZ transferred model on citation extraction | [ ] | |
| 3.3 | Fine-tune AU→NZ transferred model on deontic classification | [ ] | |
| 3.4 | Compare vs NLP-policy-NZ fine-tuned models: does AU legal pre-training help? | [ ] | |
| 3.5 | Push best AU→NZ model to Hugging Face Hub | [ ] | |

## Phase 4: MLEB-NZ Benchmark Extension

**Estimated Effort**: Medium
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 4.1 | Create NZ retrieval benchmark following MLEB methodology (NZ legislation, Hansard, court decisions) | [~] | local fixture contract satisfied; live benchmark remains external |
| 4.2 | Run NZ-MLEB on all available embedding models (our embedding, Kanon 2, OpenAI, etc.) | [ ] | |
| 4.3 | Publish NZ-MLEB results as technical report | [ ] | |
| 4.4 | Contribute NZ-MLEB dataset to Isaacus for inclusion in upstream MLEB | [ ] | |

## Phase 5: Tool Evaluation & Integration

**Estimated Effort**: Low
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 5.1 | Install and evaluate `semchunk` vs `syntactic/chunking.py` on legal document segmentation quality | [ ] | |
| 5.2 | Monitor Blackstone Graph (github.com/isaacus-dev) for stable release | [~] | |
| 5.3 | Evaluate Isaacus Legal RAG Bench on our pipeline | [ ] | |
| 5.4 | Document integration results in `docs/isaacus_integration.md` | [x] | |

## Files to Create/Modify

| File | Action |
|------|--------|
| `scripts/download_isaacus_datasets.sh` | Create |
| `scripts/evaluate_isaacus_models.sh` | Create |
| `src/nlp_policy_nz/training/isaacus_adapter.py` | Create |
| `docs/isaacus_integration.md` | Create |
| `tests/test_isaacus_adapter.py` | Create |

## Implementation Note - 2026-06-21

Repo-side Isaacus integration scaffold is implemented:

- Added offline Isaacus dataset, model, and tool manifests.
- Added AU legal row normalisation into the existing `PipelineRecord` schema.
- Added NZ-MLEB query scaffolding with relevance-judgement validation.
- Added explicit fail-closed access gates for network and proprietary API work.
- Added dry-run scripts and documentation.

Pending external work: live Hugging Face downloads, Kanon 2 API/air-gapped
evaluation, AU-to-NZ fine-tuning, measured NZ-MLEB baselines, semchunk runtime
comparison, and any Blackstone Graph integration after stable upstream release.

## Implementation Note - 2026-06-24

Narrow local-only NZ-MLEB fixture contract is implemented:

- Added `data/track22/nz_mleb_fixture.json` with three deterministic NZ sample documents, three retrieval queries, and relevance judgements.
- Added `data/track22/nz_mleb_fixture.schema.json` and local fixture validation helpers in `src/nlp_policy_nz/training/isaacus_adapter.py`.
- Updated Track 22 evidence reporting so repo-side satisfaction requires a validated local NZ-MLEB fixture.
- Focused validation passed: Track 22 pytest (`16 passed`) and targeted Ruff. The Git Bash wrapper tests require normal process access on this machine; sandboxed Bash failed with Win32 signal-pipe access denied.

Live Isaacus Hugging Face downloads, Kanon 2 API or air-gapped evaluation, AU-to-NZ fine-tuning, measured NZ-MLEB baselines, semchunk evaluation, and Blackstone Graph integration remain external-blocked and are not claimed by this slice.
