# Multi-Archive Dataset Ingestion & Archival Strategy

This document details the multi-archive strategy for redundantly publishing versioned dataset snapshots of the `nlp-policy-nz` pipeline, ensuring high availability, long-term durability, and citable DOIs.

---

## 1. Overview of Archive Targets

To prevent single-point-of-failure hosting or single-source dependency, pipeline datasets are distributed across three distinct tiers:

1.  **Active Tier: Hugging Face Hub (Production)**
    *   **Purpose:** Live dataset updates, collaborative iteration, and model training ingestion.
    *   **Interface:** Auto-sync via CLI `nlp-policy-nz upload-dataset` and `nlp-policy-nz deploy-space`.
2.  **Archival Tier: Zenodo Sandbox & Production (LTS / DOIs)**
    *   **Purpose:** Long-Term Storage (LTS) with versioned Digital Object Identifiers (DOIs) for academic citation.
    *   **Interface:** REST API integration via `ZenodoArchiver` (configured for both Sandbox and Production endpoints).
3.  **Convenience Tier: OSF (Open Science Framework)**
    *   **Purpose:** Project coordination and collaborative mirror package hosting, matching sister legal corpora datasets.
    *   **Interface:** Optional python-based OSF client sync mapping to shared legal repository storage pools.

---

## 2. Zenodo Archival Publication Schema

Zenodo deposits require specific metadata schemas conforming to the DataCite Metadata Schema. When building or submitting deposits, the payload must specify:

```json
{
  "metadata": {
    "title": "nlp-policy-nz: Preprocessed New Zealand Legislative & Parliamentary NLP Corpus",
    "upload_type": "dataset",
    "description": "Cleaned, tokenized, and enriched legal NLP corpus of Aotearoa New Zealand legislation and Parliamentary Hansard speeches. Features deontic modalities, syntactic cross-references, and bilingual Māori Language Guard phrase tagging.",
    "creators": [
      {
        "name": "nlp-policy-nz Contributors",
        "affiliation": "Open Source Community"
      }
    ],
    "keywords": [
      "legal-nlp",
      "rules-as-code",
      "new-zealand-legislation",
      "hansard",
      "spacy",
      "tei-ana",
      "akoma-ntoso"
    ],
    "license": "cc-by-4.0",
    "access_right": "open"
  }
}
```

### Script Integration Requirements

The deposit script (`nlp_policy_nz/integrations/zenodo.py` and `zenodo_archive.py`) must implement the following operational safeguards:

1.  **Endpoint Redundancy:** Fall back gracefully to `sandbox.zenodo.org` for testing purposes and switch to `zenodo.org` for production-level publishing using `ZENODO_SANDBOX_TOKEN` and `ZENODO_PRODUCTION_TOKEN`.
2.  **Size Limits & Partitions:** Parquet snapshots exceeding 50GB should be split using modular Polars/Arrow partitioning before payload serialization.
3.  **Metadata Alignment:** Inject the current version number of `nlp_policy_nz` dynamically into the release description notes to tie the pipeline code release and data snapshot versions together.

---

## 3. OSF (Open Science Framework) Mirroring Policy

The Open Science Framework acts as a matching convenience mirror for sister corpora (`corpus-law-nz` and `corpus-nz-hansard`). 

### Core Policies:
*   **Opt-In Triggers:** Snapshots are uploaded to OSF upon achieving major release milestones (e.g. `v1.0`, `v2.0`).
*   **Convenience Packaging:** OSF files are compressed as single-file zip archives (`.zip` containing the Parquet chunks, schema specifications, and the accompanying datasheet).
*   **Component Linking:** The OSF project coordinates metadata links pointing back to both the Hugging Face Hub dataset card and the published Zenodo DOI for canonical citation.
