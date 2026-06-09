# Plan: Track 2 External Integrations & Data Sovereignty Registry

This track configures external integrations for loading datasets from Hugging Face Hub, managing credentials securely, and creating sandbox archival templates for Zenodo deposits to support data sovereignty.

---

## Phase 1: Integration Loaders [b65c685]

### [x] Task 2.1: Implement Hugging Face Integration Loader
- **Action**: Create `src/nlp_policy_nz/integrations/` module with Hugging Face dataset loader that manages API tokens securely via environment variables.
- **Why**: Enables streaming NZ Hansard and Legislation datasets from Hugging Face Hub.
- **Completed**: Created `integrations/huggingface.py` with `load_hansard_dataset()` and `load_legislation_dataset()` loaders, `DatasetLoadError` exception, and `HF_TOKEN` environment variable auth.

### [x] Task 2.2: Build Zenodo Sandbox Archive Templates
- **Action**: Create Zenodo Sandbox API deposit hooks and data sovereignty registry templates.
- **Why**: Enables dataset archival and DOI generation for reproducibility.
- **Completed**: Created `integrations/zenodo.py` with `create_sandbox_deposit()`, `upload_file_to_deposit()`, `publish_deposit()`. Created `integrations/data_registry.py` with `DataSovereigntyRegistry` and `DataRecord` (msgspec Struct) for JSON-backed provenance tracking.

---
