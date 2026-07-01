# Track 8 Evidence - Hugging Face Dataset and Space Integration

Track 8 is complete for repo-side Hugging Face dataset publication tooling and Gradio Space source.

Implemented surfaces:

- `src/nlp_policy_nz/integrations/hf_uploader.py` converts Parquet files to `datasets.Dataset`, creates dataset repos, pushes datasets, and deploys Gradio Space folders.
- `src/nlp_policy_nz/integrations/dataset_card.py` generates dataset cards with YAML frontmatter, schema documentation, usage examples, and citation metadata.
- `src/nlp_policy_nz/integrations/__init__.py` exports the Hugging Face upload and dataset-card helpers.
- `src/nlp_policy_nz/cli/main.py` exposes `upload-dataset` and `deploy-space` commands.
- `spaces/app.py`, `spaces/README.md`, and `spaces/requirements.txt` define the interactive Gradio Space source.
- `scripts/deploy_space.sh` provides a shell deployment path with dry-run support.

Validation evidence:

- `tests/test_hf_upload.py` covers token resolution, Parquet conversion, repo creation, dataset upload, Space deployment, dry-run behavior, and mocked end-to-end upload/deploy flows.
- `tests/test_dataset_card.py` covers dataset-card frontmatter, metadata interpolation, schema text, BibTeX citation, and file writing.
- `tests/test_gradio_space.py` covers Space data-loading, search, citation-network, Te Reo chart, and stats transformations.
- `tests/test_cli.py` covers the public CLI parser surface for Track 8 commands.
- The Track 8 Conductor contract test verifies this archived track keeps standard `index.md`, `spec.md`, `plan.md`, `metadata.json`, and `evidence.md` artifacts.

External gates:

- Live Hugging Face dataset or Space publication requires a valid `HF_TOKEN` and an approved target namespace.
- Automated Hugging Face publication on merge belongs to Track 45.
- The broader public exploration site belongs to Track 36, and accessibility/privacy hardening belongs to Track 50.

