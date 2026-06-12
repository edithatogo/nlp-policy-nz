# Track 8: Deploy Hugging Face Datasets & Interactive Visualization Spaces

**Dependencies**: Track 7 (Downstream API)
**Parallelization Node**: Hugging Face Hub Integration
**Status**: ✅ Complete

---

## Goal

Push processed Parquet outputs as versioned Hugging Face datasets (`nz-hansard`, `nz-legislation`) and build interactive Gradio Spaces for live exploration of the NLP pipeline results.

## Scope

### What This Track Covers

1. **Dataset Upload Pipeline**: A CLI command and Python API to push Parquet files to the Hugging Face Hub as proper `datasets.Dataset` objects with metadata cards.
2. **Dataset Card Generator**: Auto-generate YAML frontmatter + markdown description from project context (schema fields, corpus stats, processing details).
3. **Interactive Gradio Spaces**: A Gradio-based Space that accepts Parquet uploads and provides:
   - Full-text search over document chunks
   - Citation network explorer (act/section cross-references)
   - Te Reo Māori term frequency visualisation
   - Corpus statistics dashboard (chunk counts, language mix, source distribution)
4. **Space Deployment Script**: A CI-friendly script to push Gradio apps to HF Spaces with proper `README.md` and `requirements.txt`.

### What This Track Does NOT Cover

- Zenodo archiving (Track 9)
- Model fine-tuning or inference endpoints
- Authentication/permission management (assumes HF token is set)

---

## Phases

### Phase 1: Dataset Upload Pipeline
**Estimated Effort**: Medium
**Status**: ✅ Complete

Create the upload machinery to push Parquet data to the Hugging Face Hub.

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Create `src/nlp_policy_nz/integrations/hf_uploader.py` — functions to convert Parquet → `datasets.Dataset`, create dataset repos, upload with metadata | [x] | |
| 1.2 | Add `upload_dataset()` CLI subcommand to `src/nlp_policy_nz/cli/main.py` — flags: `--parquet`, `--repo-id`, `--private`, `--license` | [x] | |
| 1.3 | Create dataset card generator in `src/nlp_policy_nz/integrations/dataset_card.py` — builds YAML frontmatter + markdown from pipeline output metadata | [x] | |
| 1.4 | Write unit tests for upload pipeline and dataset card generation | [x] | |
| 1.5 | Integration test: upload a small test Parquet to HF sandbox (mock or real) | [x] | |

**Checkpoint**: `conductor(checkpoint): Checkpoint end of Phase 1 — Track 8` ✅

### Phase 2: Interactive Gradio Visualization Space
**Estimated Effort**: Medium-High
**Status**: ✅ Complete

Build a self-contained Gradio app that visualises pipeline outputs.

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Create `spaces/app.py` — Gradio Blocks app with tabs: Search, Citations, Te Reo, Stats | [x] | |
| 2.2 | Implement Search tab — loads Parquet, provides `gr.Dataframe` + text search via simple TF-IDF or exact match | [x] | |
| 2.3 | Implement Citations tab — parses `nz_act_citations` field, shows cross-reference network as `gr.Plot` (matplotlib/plotly) | [x] | |
| 2.4 | Implement Te Reo tab — word cloud or frequency bar chart of `te_reo_terms` field | [x] | |
| 2.5 | Implement Stats tab — corpus-level metrics: total chunks, language distribution, source breakdown, embedding dimension | [x] | |
| 2.6 | Create `spaces/requirements.txt` with Gradio, pandas, plotly, wordcloud | [x] | |
| 2.7 | Create `spaces/README.md` with HF Spaces metadata (emoji, SDK, app file) | [x] | |
| 2.8 | Write tests for each tab's data transformation logic | [x] | |

**Checkpoint**: `conductor(checkpoint): Checkpoint end of Phase 2 — Track 8` ✅

### Phase 3: Deployment & Documentation
**Estimated Effort**: Low-Medium
**Status**: ✅ Complete

Wire up the Space deployment and document the full workflow.

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Create `scripts/deploy_space.sh` — pushes `spaces/` dir to a HF Space repo | [x] | |
| 3.2 | Add `deploy-space` CLI subcommand to `src/nlp_policy_nz/cli/main.py` | [x] | |
| 3.3 | Update `product.md` and `requirements.md` to reflect HF Hub and Space features | [x] | |
| 3.4 | Add integration test for deploy script (dry-run mode) | [x] | |

**Checkpoint**: `conductor(checkpoint): Checkpoint end of Phase 3 — Track 8` ✅

---

## Acceptance Criteria

- [x] `nlp-policy-nz upload-dataset` pushes a Parquet file to HF Hub with auto-generated dataset card
- [x] `nlp-policy-nz deploy-space` pushes the Gradio app to a HF Space
- [x] Gradio app loads a Parquet dataset and provides 4 interactive tabs
- [x] All new modules have >90% test coverage
- [x] No linting/formatting errors via `pixi run check`

## Files Created/Modified

| File | Action |
|------|--------|
| `src/nlp_policy_nz/integrations/hf_uploader.py` | Create |
| `src/nlp_policy_nz/integrations/dataset_card.py` | Create |
| `src/nlp_policy_nz/cli/main.py` | Modify |
| `spaces/app.py` | Create |
| `spaces/requirements.txt` | Create |
| `spaces/README.md` | Create |
| `scripts/deploy_space.sh` | Create |
| `tests/test_hf_upload.py` | Create |
| `tests/test_dataset_card.py` | Create |
| `tests/test_gradio_space.py` | Create |
| `tests/test_cli.py` | Modify |
| `README.md` | Modify |
| `src/nlp_policy_nz/integrations/__init__.py` | Modify |

## Notes

- The existing `huggingface.py` handles dataset **loading**; this track adds **uploading** — they are complementary, not overlapping.
- Gradio is chosen over Streamlit for HF Spaces native support and simpler self-contained deployment.
- The `datasets` library from Hugging Face handles Parquet ↔ Dataset conversion natively.
- For the Space's search, start with pandas-based filtering (TF-IDF can be added later as an enhancement).
- `deploy_space` function added to `hf_uploader.py` with dry-run support and HfApi-based upload_folder.
- CLI also includes `archive-to-zenodo` and `release` subcommands (Track 9 work has begun in parallel).
