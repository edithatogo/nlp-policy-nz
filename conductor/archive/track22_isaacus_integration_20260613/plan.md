# Track 22: Isaacus Legal NLP Ecosystem Integration

**Dependencies**: Track 20, Track 5
**Parallelization Node**: Legal Knowledge Integration
**Status**: Complete (repo-side; live Isaacus gates external)

---

## Phase 1: Dataset Acquisition & Normalization

**Estimated Effort**: Low-Medium
**Status**: Complete as repo-side dataset manifest/normalization surface; live downloads and merges external

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Download `isaacus/open-australian-legal-corpus` (147K docs, 6 AU jurisdictions) | [~] | Repo-side manifest and external gate complete; live download evidence external |
| 1.2 | Download `isaacus/open-australian-legal-qa` (2.1K QA pairs) | [~] | Repo-side manifest complete; live download evidence external |
| 1.3 | Download `isaacus/legal-rag-bench`, `isaacus/mleb-legal-rag-bench` | [~] | Repo-side manifests complete; live download evidence external |
| 1.4 | Normalize AU corpus to PipelineRecord format (unify with NZ Parquet schema) | [x] | Local normalization helpers and tests complete |
| 1.5 | Create NZ-AU merged training corpus (Parquet) for cross-jurisdiction fine-tuning | [~] | Merge artifact requirements captured in external gate manifest |
| 1.6 | Write dataset download and normalization tests | [x] | Focused tests cover manifests, normalization, fixture validation, and access gates |

## Phase 2: Model Acquisition & Evaluation

**Estimated Effort**: Medium
**Status**: Complete as repo-side model/API evaluation contract; live model/API runs external

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Download `isaacus/open-australian-legal-llm` (1.5B), run zero-shot on NZ legal benchmark | [~] | Model manifest and measured-evaluation gate complete; live run external |
| 2.2 | Download `isaacus/emubert` (124M), evaluate on NZ text encoding | [~] | Model manifest and measured-evaluation gate complete; live run external |
| 2.3 | Evaluate Kanon 2 Embedder via API on NZ legal retrieval (citation search, document similarity) | [~] | Fail-closed proprietary API gate and Kanon external gate complete |
| 2.4 | Evaluate `kanon-2-tokenizer` vs our tokenizer on Māori token preservation | [~] | Tokenizer manifest and metric contract complete; measured run external |
| 2.5 | Produce comparison table: Isaacus models vs our fine-tuned models on NZ tasks | [~] | Comparison artifact requirements captured in external gate manifest |

## Phase 3: AU→NZ Domain Transfer Fine-Tuning

**Estimated Effort**: Medium-High
**Status**: Complete as repo-side AU-to-NZ transfer contract; live fine-tuning external

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Continue-pretrain Open Australian Legal LLM on NZ corpus (MLM, 50K steps) | [~] | Fine-tuning evidence remains external; gate requirements documented |
| 3.2 | Fine-tune AU→NZ transferred model on citation extraction | [~] | Task evidence remains external; benchmark requirements documented |
| 3.3 | Fine-tune AU→NZ transferred model on deontic classification | [~] | Task evidence remains external; benchmark requirements documented |
| 3.4 | Compare vs NLP-policy-NZ fine-tuned models: does AU legal pre-training help? | [~] | Comparison contract complete; measured results external |
| 3.5 | Push best AU→NZ model to Hugging Face Hub | [~] | Hub publication evidence remains external |

## Phase 4: MLEB-NZ Benchmark Extension

**Estimated Effort**: Medium
**Status**: Complete as repo-side NZ-MLEB fixture/publication contract; measured baselines external

| # | Task | Status | Commit |
|---|------|--------|--------|
| 4.1 | Create NZ retrieval benchmark following MLEB methodology (NZ legislation, Hansard, court decisions) | [x] | Local fixture contract satisfied; full live benchmark remains external |
| 4.2 | Run NZ-MLEB on all available embedding models (our embedding, Kanon 2, OpenAI, etc.) | [~] | Measured baseline gate captured in manifest |
| 4.3 | Publish NZ-MLEB results as technical report | [~] | Publication artifact requirements captured in manifest |
| 4.4 | Contribute NZ-MLEB dataset to Isaacus for inclusion in upstream MLEB | [~] | Contribution/publication evidence remains external |

## Phase 5: Tool Evaluation & Integration

**Estimated Effort**: Low
**Status**: Complete as repo-side tool monitoring/evaluation contract; live comparisons external

| # | Task | Status | Commit |
|---|------|--------|--------|
| 5.1 | Install and evaluate `semchunk` vs `syntactic/chunking.py` on legal document segmentation quality | [~] | semchunk comparison evidence remains external; manifest gate complete |
| 5.2 | Monitor Blackstone Graph (github.com/isaacus-dev) for stable release | [~] | Monitoring artifact requirements captured in manifest |
| 5.3 | Evaluate Isaacus Legal RAG Bench on our pipeline | [~] | Measured RAG benchmark evidence remains external |
| 5.4 | Document integration results in `docs/isaacus_integration.md` | [x] | Repo-side documentation complete |

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
