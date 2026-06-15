# Isaacus Legal AI Alignment — Comprehensive Inventory

> **Track 12 — Isaacus Legal AI Alignment, Benchmarks, and Contribution Path**
>
> Owning subrepo: `nlp-policy-nz`
>
> Upstream surfaces reviewed on 2026-06-14:
> - [Isaacus Hugging Face organisation](https://huggingface.co/isaacus)
> - [Open Australian Legal Corpus Creator](https://github.com/isaacus-dev/open-australian-legal-corpus-creator)
> - [Open Australian Legal Embeddings Creator](https://github.com/isaacus-dev/open-australian-legal-embeddings-creator)
> - [isaacus-haystack](https://github.com/isaacus-dev/isaacus-haystack)
> - [Haystack documentation](https://haystack.deepset.ai/)

---

## Table of Contents

1. [Upstream Surfaces Reviewed](#1-upstream-surfaces-reviewed)
2. [Schema Inventory](#2-schema-inventory)
3. [Benchmark Task Format Inventory](#3-benchmark-task-format-inventory)
4. [Document Metadata Conventions](#4-document-metadata-conventions)
5. [Chunking Strategy Documentation](#5-chunking-strategy-documentation)
6. [Embedding Defaults](#6-embedding-defaults)
7. [Haystack Component Boundaries](#7-haystack-component-boundaries)
8. [NZ-Specific Adaptations Needed](#8-nz-specific-adaptations-needed)
9. [Placement Decisions](#9-placement-decisions)
10. [Integration Phases Summary](#10-integration-phases-summary)
11. [Appendix A: Isaacus Ecosystem Reference](#appendix-a-isaacus-ecosystem-reference)
12. [Appendix B: PipelineRecord Schema v1.0 Full Specification](#appendix-b-pipelinerecord-schema-v10-full-specification)

---

## 1. Upstream Surfaces Reviewed

### 1.1 Hugging Face Organisation (`huggingface.co/isaacus`)

The Isaacus Hugging Face organisation publishes the following resource categories:

| Category | Resources | Licence |
|---|---|---|
| **Generation models** | `open-australian-legal-llm` (1.5B), `open-australian-legal-phi-1_5` (1.3B), `open-australian-legal-gpt2` (124M) | Apache 2.0 |
| **Embedding models** | `emubert` (124M), `kanon-2-tokenizer`, `kanon-tokenizer` | Apache 2.0 |
| **Corpus datasets** | `open-australian-legal-corpus` (147K docs, 6 AU jurisdictions) | — |
| **QA datasets** | `open-australian-legal-qa` (2.1K QA pairs) | — |
| **Benchmark datasets** | `legal-rag-bench` (4.9K), `mleb-legal-rag-bench` (5K retrieval) | — |
| **AU-specific datasets** | `high-court-of-australia-cases` (8.1K), `uk-legislative-long-titles` (234), `australian-tax-guidance-retrieval` (329), `contractual-clause-retrieval` (225) | — |

### 1.2 GitHub Repositories

| Repository | Purpose |
|---|---|
| `isaacus-dev/open-australian-legal-corpus-creator` | Corpus ingestion, provenance, and publication pipeline for AU legal sources |
| `isaacus-dev/open-australian-legal-embeddings-creator` | Embedding/reranking experiments and evaluation harness |
| `isaacus-dev/isaacus-haystack` | Haystack 2.x pipeline components, retrieval, and RAG adapters |

### 1.3 Tooling Surfaces

| Tool | Repository | Description |
|---|---|---|
| **semchunk** | `github.com/isaacus-dev/semchunk` | AI-powered legal document chunking |
| **Blackstone Graph** | Announced June 2026 | Graph-based legal knowledge representation |
| **MLEB** | HF: `isaacus/mleb-*` | Massive Legal Embedding Benchmark |
| **Kanon 2 Embedder** | Proprietary (API/air-gapped) | #1 on MLEB as of Oct 2025 |

### 1.4 External Reference

| Surface | Use |
|---|---|
| [Haystack documentation](https://haystack.deepset.ai/) | Component reference for RAG pipeline design |

---

## 2. Schema Inventory

### 2.1 Isaacus Upstream Schemas (Observed)

**Open Australian Legal Corpus (observed fields):**
```
version_id, document_id, type, jurisdiction, source, collection,
mime, date, citation, title, url, text, rights, provenance
```

**Open Australian Legal QA (observed fields):**
```
question_id, question, answer, supporting_passage_ids,
retrieval_split, document_id, source
```

**MLEB / Legal RAG Bench (observed fields):**
```
query_id, query, corpus_passage_id, passage_text, passage_source,
relevance_label, task_type, jurisdiction, split
```

### 2.2 nlp-policy-nz PipelineRecord Schema

The local `PipelineRecord` (defined in `src/nlp_policy_nz/storage/serialization.py`) is a `msgspec.Struct`:

| Field | Type | Required | Description |
|---|---|---|---|
| `doc_id` | `str` | Yes | Unique document/chunk identifier |
| `corpus_source` | `str` | Yes | Source corpus (`legislation`, `hansard`, `select_committee`) |
| `raw_text` | `str` | Yes | Original raw text of the chunk |
| `cleaned_tokens` | `list[str]` | Yes | Tokenised and cleaned tokens |
| `nz_act_citations` | `list[str]` | Yes | NZ Act citations detected |
| `te_reo_terms` | `list[str]` | Yes | Te Reo Māori terms identified |
| `embeddings` | `list[float] \| None` | No | Dense vector embedding |
| `deontic_modality` | `list[dict]` | No | Modality annotations |
| `legal_effect` | `str \| None` | No | LKIF-inspired legal effect |
| `submitter_name` | `str \| None` | No | Submission author |
| `committee` | `str \| None` | No | Committee name |
| `bill_reference` | `str \| None` | No | Related bill reference |
| `linkage_confidence` | `float \| None` | No | Cross-corpus linkage confidence |
| `challenged_regulation` | `str \| None` | No | Regulation challenged |
| `grounds` | `str \| None` | No | Grounds for challenge |
| `report_title` | `str \| None` | No | Report title |
| `findings` | `list[str] \| None` | No | Report findings |
| `recommendations` | `list[str] \| None` | No | Report recommendations |

## 3. Benchmark Task Format Inventory

### 3.1 MLEB-Style Retrieval Benchmark

**Upstream (Isaacus MLEB):**
- Multi-jurisdiction retrieval evaluation
- Tasks: legislative retrieval, case-law retrieval, contract retrieval, tax guidance
- Metrics: NDCG@K, Recall@K, MRR

**NZ Adaptation (NZ-MLEB):**
- Add NZ as 7th jurisdiction
- Query types: legislative provision retrieval, amendment/version retrieval, case-to-statute, Hansard-to-bill/Act, policy-to-authority, regulator guidance

### 3.2 Retrieval Task Families (NZ-Specific)

| Task Family | Query Type | Corpus | Metrics |
|---|---|---|---|
| Legislative provision retrieval | NL questions about specific sections | NZ legislation acts | NDCG@5, Recall@10 |
| Amendment/version retrieval | "What did section X say before 2020 amendment?" | Multi-version legislation | NDCG@3, MRR |
| Case-to-statute retrieval | "Which statutes did this judgment cite?" | Medilegal cases + legislation | Recall@5 |
| Hansard-to-bill/Act retrieval | "Which bill was being debated in this speech?" | Hansard + legislation | NDCG@5 |
| Policy-to-authority retrieval | "What legal authority supports this policy?" | Policy docs + legislation | Recall@3, MRR |
| Regulator guidance retrieval | "Which guidance applies to this scenario?" | Regulator text + legislation | NDCG@5 |
| NZ citation normalisation | Normalise free-text legal reference | Legislation + Hansard | Accuracy, F1 |

### 3.3 Classification Tasks

| Task | Labels | Source |
|---|---|---|
| Deontic modality | `obligation`, `prohibition`, `permission`, `dispensation`, `none` | Legislation clauses |
| Legal effect | `obligation`, `prohibition`, `permission`, `power`, `liability`, `immunity`, `disability`, `none` | Legislation clauses |
| Document type | `act`, `bill`, `secondary_legislation`, `regulation`, `hansard_document`, `speech_turn`, `sitting` | All corpora |
| Language detection | `en`, `mi`, `en-mi-bilingual` | All corpora |
| Te Reo term presence | `present`, `absent` | All corpora |

### 3.4 Long-Form Answer Tasks

| Task Type | Input | Output | Evaluation |
|---|---|---|---|
| Legal QA (template: Open Australian Legal QA) | Question + supporting passages | Extractive/abstractive answer | Exact match, F1, ROUGE-L |
| Clause-level legal effect explanation | Clause text | Natural language explanation | Expert review, BLEU |
| Citation context resolution | Citation mention + context | Full citation target | Accuracy |

### 3.5 Benchmark Export Contract (Phase 2)

```json
{
  "benchmark_id": "nz-legal-rag-bench-v1",
  "jurisdiction": "NZ",
  "tasks": [
    {
      "task_id": "legislative-provision-retrieval",
      "task_type": "retrieval",
      "queries": [...],
      "corpus_passages": [...],
      "qrels": {...},
      "train_split": "...",
      "test_split": "..."
    }
  ]
}
```

## 4. Document Metadata Conventions

### 4.1 Chunk ID Conventions

**Legislation:** `NZ-ACT-{YEAR}-{NNN}-SEC-{SECTION}` (e.g. `NZ-ACT-1961-043-SEC-4`)
**Hansard:** `NZ-HANS-{YYYY-MM-DD}-SP-{NN}` (e.g. `NZ-HANS-2023-05-12-SP-04`)

### 4.2 Provenance Conventions

| Field | Example |
|---|---|
| `pipeline_name` | `nlp_policy_nz` |
| `pipeline_version` | `0.1.0` |
| `source_name` | `PCO Legislation API` |
| `source_record_id` | Source-specific persistent ID |
| `source_retrieved_at` | ISO 8601 datetime |
| `release_version` | SemVer string |
| `release_commit` | Git commit SHA (7-40 hex chars) |
| `license_note` | Rights and licensing text |

### 4.3 Corpus Source Values

`legislation`, `hansard`, `select_committee`, `parliament_submission`, `regulations_review`

### 4.4 Coverage Status

`complete`, `partial`, `pilot`, `sample`, `search_derived`, `unknown`

### 4.5 Language Codes

`en` (English), `mi` (Te Reo Maori), `en-mi`, `mi-en`

---

## 5. Chunking Strategy Documentation

### 5.1 Current Implementation

**Module:** `src/nlp_policy_nz/syntactic/chunking.py`
**Strategy:** Sentence-level using spaCy `doc.sents`

**Functions:**
- `chunk_legislation_document(text, nlp, year, number)` -> `NZ-ACT-{year}-{number:03d}-SEC-{i}`
- `chunk_hansard_speech(text, nlp, date, speech_num)` -> `NZ-HANS-{date}-SP-{speech_num:02d}`
- Both delegate to `chunk_by_sentence(text, nlp)` for spaCy boundaries.

### 5.2 Parameters

| Parameter | Value |
|---|---|
| Granularity | Sentence |
| Max tokens per chunk | Implicit (spaCy) |
| Overlap | None |
| Structural awareness | None |

### 5.3 Comparison with Isaacus semchunk

Isaacus `semchunk`: semantic boundary detection, configurable size, overlap, structural awareness.
**Evaluation gap:** Not yet performed (Track 22 Phase 5, Task 5.1).

### 5.4 Recommended Enhancements

1. Semantic chunking evaluation (vs semchunk)
2. Structural boundary awareness (XML sections, parts, schedules)
3. Configurable overlap
4. Max-token awareness (512 for BERT)
5. Hybrid structural + sentence approach

---

## 6. Embedding Defaults

### 6.1 Model Configuration

- **Primary:** `nlpaueb/legal-bert-base-uncased`
- **Fallback:** `bert-base-uncased`

### 6.2 Quantization Defaults

| Parameter | Default |
|---|---|
| Quantization mode | `4bit` |
| Compute dtype | `float16` |
| Double quantization | Enabled |
| Quantization type | `nf4` |
| Device map | `auto` |

### 6.3 Embedding Generation

| Parameter | Default |
|---|---|
| `max_length` | 512 tokens |
| Pooling | Mean pooling |
| Batch size | 32 |
| Dimension | 768 |

### 6.4 Vector Store

| Parameter | Default |
|---|---|
| Backend | LanceDB |
| URI | `./lancedb_data` |
| Table | `embeddings` |
| Default top-k | 10 |

### 6.5 Comparison Targets

| Model | MLEB | Access |
|---|---|---|
| Kanon 2 Embedder | #1 (Oct 2025) | Gated (API/air-gapped) |
| `emubert` | Baseline | Apache 2.0 |
| OpenAI Text Embedding 3 Large | Below Kanon 2 | Paid, cost-gated |
| `nlpaueb/legal-bert-base-uncased` | -- | Current default |

---

## 7. Haystack Component Boundaries

### 7.1 Current State

Haystack 2.x is **not yet integrated** into `nlp-policy-nz`. It belongs in `nlp-policy-nz` prototypes first (Track 23).

### 7.2 Proposed Mapping

| Component | NZ Implementation |
|---|---|
| `DocumentStore` | LanceDB (VectorIndex) |
| `Embedder` | `generate_embedding()` |
| `Retriever` | `VectorIndex.search()` |
| `Ranker` | Not yet implemented |
| `Reader` | Not yet implemented |
| `PreProcessor` | chunking.py |
| `Pipeline` | pipeline_api.py |

### 7.3 Adapter Requirements

1. PipelineRecord -> Haystack Document adapter
2. `generate_embedding()` -> Haystack Embedder wrapper
3. `VectorIndex.search()` -> Haystack Retriever wrapper
4. LanceDB -> Haystack DocumentStore wrapper

### 7.4 Decision Flow

```
nlp-policy-nz/rag/ -> examples/tests
  If reusable -> legal-nz-rag-haystack/ repo
  If stable CLI -> cli-legislation-nz/ commands
  If Isaacus compatible -> import from isaacus-haystack
```

---

## 8. NZ-Specific Adaptations Needed

### 8.1 Source Replacements

| Isaacus AU | NZ Replacement | Subrepo |
|---|---|---|
| `open-australian-legal-corpus` | NZ legislation | `corpus-law-nz` |
| AU court decisions | NZ judgments | `corpus-cases-medilegal-nz` |
| AU parliamentary records | NZ Hansard | `corpus-nz-hansard` |
| AU policy docs | NZ regulatory guidance | `nlp-policy-nz` |
| AU historical material | NZ public-domain | `hathi-nz` |
| AU social media | NZ govt social media | `sm-govt-nz` |

### 8.2 Schema Adaptations

| AU Pattern | NZ Adaptation |
|---|---|
| `jurisdiction: AU-{STATE}` | `jurisdiction: New Zealand` |
| Act citation `(Cth)` | NZ year-only citation |
| Common law + statute | + Treaty of Waitangi |
| English-only | English + Te Reo Maori |
| Single licence | Per-source rights note |

### 8.3 Citation Adaptations

| NZ Type | Pattern | Example |
|---|---|---|
| Act | `{Title Act} {Year}` | "Crimes Act 1961" |
| Section | `section {N}` | "section 29" |
| Neutral citation | `[Year] NZ{Court} {N}` | "[2024] NZSC 1" |
| Part | `Part {N}` | "Part 2" |
| Schedule | `Schedule {N}` | "Schedule 1" |
| Bill | `{Name} Bill` | "Climate Change Response Bill" |

Existing `citations.py` `EntityRuler` already covers these patterns.

### 8.4 Maori Language

- Maori Guard implemented in `guard/` module
- Token preservation, code-switching, macron normalisation
- Language ID: `mi` / `en` / bilingual
- Benchmarks must include Maori/bilingual content

### 8.5 Provenance Requirements

1. Source authority identification
2. Version/amendment trail with effective dates
3. Per-source rights notes (not single licence)
4. Cultural/tikanga considerations beyond copyright
5. Redaction/privacy status tracking

---

## 9. Placement Decisions

(From `task_plan.md` Track 12)

1. **Corpus ingestion** -> Keep in existing corpus repos
2. **Benchmark adapters & RAG prototypes** -> `nlp-policy-nz` first
3. **CLI workflows** -> `cli-legislation-nz` only for stable commands
4. **New repo** -> Only if RAG layer becomes reusable app (`legal-nz-rag-haystack`)
5. **Forking Isaacus** -> Not without specific upstream divergence
6. **DigitalNZ discovery** -> Prototype in `nlp-policy-nz`

---

## 10. Integration Phases Summary

| Phase | Status | Owner |
|---|---|---|
| **Phase 1: Inventory** | Complete | `nlp-policy-nz` |
| **Phase 2: Benchmark export contract** | Pending | `nlp-policy-nz` |
| **Phase 3: Per-corpus benchmark slices** | Pending | Corpus repos |
| **Phase 4: Embedding/retrieval baselines** | Pending | `nlp-policy-nz` |
| **Phase 5: Haystack RAG prototype** | Pending | `nlp-policy-nz` |
| **Phase 6: Upstream contributions** | Pending | Various |
| **Phase 7: Fine-tuning evaluation** | Pending | `nlp-policy-nz` |

---

## Appendix A: Isaacus Ecosystem Reference

### Models

| HF Model ID | Type | Params | Licence |
|---|---|---|---|
| `isaacus/open-australian-legal-llm` | GPT-2 XL | 1.5B | Apache 2.0 |
| `isaacus/open-australian-legal-phi-1_5` | Phi-1.5 | 1.3B | Apache 2.0 |
| `isaacus/open-australian-legal-gpt2` | GPT-2 | 124M | Apache 2.0 |
| `isaacus/emubert` | BERT | 124M | Apache 2.0 |
| `isaacus/kanon-2-tokenizer` | Tokenizer | -- | -- |
| `isaacus/kanon-tokenizer` | Tokenizer | -- | -- |

### Datasets

| HF Dataset ID | Records | Description |
|---|---|---|
| `isaacus/open-australian-legal-corpus` | 147K | AU legislation, regulations, decisions |
| `isaacus/open-australian-legal-qa` | 2.1K | AU legal QA pairs |
| `isaacus/legal-rag-bench` | 4.9K | Legal RAG evaluation |
| `isaacus/mleb-legal-rag-bench` | 5K | MLEB retrieval |
| `isaacus/high-court-of-australia-cases` | 8.1K | HCA decisions |
| `isaacus/uk-legislative-long-titles` | 234 | UK titles |
| `isaacus/australian-tax-guidance-retrieval` | 329 | Tax retrieval |
| `isaacus/contractual-clause-retrieval` | 225 | Contract retrieval |

### Tools

| Tool | Repository | Status |
|---|---|---|
| semchunk | `github.com/isaacus-dev/semchunk` | Active |
| Blackstone Graph | Announced June 2026 | Monitor |
| isaacus-haystack | `github.com/isaacus-dev/isaacus-haystack` | Active |
| MLEB suite | HF: `isaacus/mleb-*` | Active |
| Kanon 2 Embedder | Proprietary | Gated (credential + cost) |

---

## Appendix B: PipelineRecord Schema v1.0 Full Spec

```python
@msgspec.struct
class PipelineRecord:
    doc_id: str
    corpus_source: str
    raw_text: str
    cleaned_tokens: list[str]
    nz_act_citations: list[str]
    te_reo_terms: list[str]
    embeddings: list[float] | None = None
    deontic_modality: list[dict]
    legal_effect: str | None = None
    submitter_name: str | None = None
    committee: str | None = None
    bill_reference: str | None = None
    linkage_confidence: float | None = None
    challenged_regulation: str | None = None
    grounds: str | None = None
    report_title: str | None = None
    findings: list[str] | None = None
    recommendations: list[str] | None = None
```

**SCHEMA_FIELDS** (Parquet column ordering):
```python
SCHEMA_FIELDS = [
    "doc_id", "corpus_source", "raw_text", "cleaned_tokens",
    "nz_act_citations", "te_reo_terms", "embeddings",
    "deontic_modality", "legal_effect",
    "submitter_name", "committee", "bill_reference",
    "linkage_confidence", "challenged_regulation", "grounds",
    "report_title", "findings", "recommendations",
]
```

---

*Document created 2026-06-15 as part of Track 12 (Isaacus Legal AI Alignment).*
*Owning subrepo: `nlp-policy-nz`.*
