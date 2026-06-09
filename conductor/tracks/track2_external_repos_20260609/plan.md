# Plan: Track 2 External Integrations & Data Sovereignty Registry

This track configures external integrations for loading datasets from Hugging Face Hub, managing credentials securely, and creating sandbox archival templates for Zenodo deposits to support data sovereignty.

---

## Phase 1: Integration Loaders

### [ ] Task 2.1: Implement Hugging Face Integration Loader
- **Action**: Create `src/nlp_policy_nz/integrations/` module with Hugging Face dataset loader that manages API tokens securely via environment variables.
- **Why**: Enables streaming NZ Hansard and Legislation datasets from Hugging Face Hub.

### [ ] Task 2.2: Build Zenodo Sandbox Archive Templates
- **Action**: Create Zenodo API sandbox deposit hooks and data sovereignty registry templates.
- **Why**: Enables dataset archival and DOI generation for reproducibility.

---
