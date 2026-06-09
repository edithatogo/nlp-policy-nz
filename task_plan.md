# Mission Plan: nlp-policy-nz Implementation

This document outlines the granular, sequential, dependency-aware task checklist to implement the `nlp-policy-nz` shared core package.

---

## Track 1: Workspace Environment & Quality Tooling
**Owner**: `Env_Architect` | **Validator**: `Quality_Validator`

- [ ] **Task 1.1: Verify Pixi and uv configurations**
  - Create standard python package directory structure `src/nlp_policy_nz/`.
  - Validate pixi.toml and pyproject.toml configuration settings.
- [ ] **Task 1.2: Initialize quality gate rules**
  - Setup `.ruff.toml` strict rules, `Tach` configuration files, and `Complexipy` checkers.
- [ ] **Task 1.3: Configure testing framework**
  - Setup `pytest` hooks, `Hypothesis` property config, and `Mutatest` configurations.
- [ ] **Task 1.4: Configure CI Workflow**
  - Scaffold `.github/workflows/ci.yml` to run tests and quality checks.

---

## Track 2: Configure External Registries (Hugging Face / GitHub / Zenodo)
**Owner**: `Env_Architect` | **Validator**: `Quality_Validator`

- [ ] **Task 2.1: Implement integration loaders**
  - Setup credential managers to load Hugging Face Hub dataset keys securely.
- [ ] **Task 2.2: Build sandbox archive templates**
  - Code sandbox dataset serialization hooks for Zenodo API deposits.

---

## Track 3: Implement Māori Language Guard (SOTA)
**Owner**: `Maori_Language_Expert` | **Validator**: `Quality_Validator`

- [ ] **Task 3.1: Build Unicode Normalization Layer**
  - Implement NFC unicode normalizer to handle macron variations.
- [ ] **Task 3.2: Implement Tokenizer Exceptions**
  - Configure spaCy tokenizer rules to protect Te Reo Māori vocabulary from subword splits.
- [ ] **Task 3.3: Build Language Identifier**
  - Code phrase-level sequence classifier identifying Te Reo Māori vs English sections.

---

## Track 4: Build Syntactic Parser & Citation Extractor
**Owner**: `Syntactic_Engineer` | **Validator**: `Quality_Validator`

- [ ] **Task 4.1: Scaffold blank spaCy Pipeline**
  - Build pipeline loader using the customized tokenizer from Track 3.
- [ ] **Task 4.2: Implement EntityRuler Regex Matchers**
  - Configure patterns to extract NZ Act titles and cross-references.
- [ ] **Task 4.3: Implement Document Chunking**
  - Write sentence-level splitting logic with unique document identifiers (`doc_id`).

---

## Track 5: Integrate Semantic Layer & quantized embeddings
**Owner**: `Semantic_Embedder` | **Validator**: `Quality_Validator`

- [ ] **Task 5.1: Integrate local LLM loader**
  - Implement quantized 4-bit loading via bitsandbytes for SaulLM-7B/Legal-BERT.
- [ ] **Task 5.2: Implement embedding generators**
  - Code dense vector generation pipelines utilizing Hugging Face fast tokenizers, releasing Python GIL.

---

## Track 6: Standardize Output Schema & LanceDB Vector Engine
**Owner**: `Storage_Search_Integrator` | **Validator**: `Quality_Validator`

- [ ] **Task 6.1: Build Narwhals Serialization Layer**
  - Code zero-copy dataframe serialization to Parquet files using Narwhals.
- [ ] **Task 6.2: Integrate LanceDB vector databases**
  - Implement local Arrow-native embedding indices using LanceDB.

---

## Track 7: Downstream API & Cross-Domain Verification
**Owner**: `Storage_Search_Integrator` | **Validator**: `Quality_Validator`

- [ ] **Task 7.1: Expose public module APIs**
  - Finalize public function exports for `corpus-law-nz` and `corpus-nz-hansard`.
- [ ] **Task 7.2: Code relational graphs**
  - Implement NetworkX mapping layer linking debate mentions to legislation acts.
