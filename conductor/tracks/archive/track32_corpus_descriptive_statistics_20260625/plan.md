# Track 32: Whole-Corpus Descriptive Statistics

**Dependencies**: Tracks 6, 18, 31
**Parallelization Node**: Corpus Analytics
**Status**: Complete

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Define required metrics: document count by corpus (legislation, Hansard, court), token/word/sentence counts, entity density by type, deontic modality distribution, citation graph stats, temporal coverage span, Māori language segment percentage | [x] | conductor_orchestrator |
| 2 | Define grouping dimensions: by Parliament (Hansard), by Act type/Year (legislation), by Court/Year (case law), by topic/ontology category | [x] | conductor_orchestrator |
| 3 | Define output table schemas: per-corpus summary, per-year trends, entity co-occurrence matrix, temporal entity histograms | [x] | conductor_orchestrator |
| 4 | Identify metrics requiring unavailable full-corpus data and add blockers to register | [x] | conductor_orchestrator |
| 5 | Create `src/nlp_policy_nz/analysis/corpus_statistics.py` with reproducible pipeline: load PipelineRecord parquet -> compute metrics -> aggregate -> emit tables | [x] | conductor_orchestrator |
| 6 | Add temporal aggregation: year-over-year trends, entity burst detection, vocabulary growth curves | [x] | conductor_orchestrator |
| 7 | Add ontology-coverage aggregation: count of records per ontology category, per standard, per mapping type | [x] | conductor_orchestrator |
| 8 | Write fixture-level tests for each aggregator with deterministic sample data; add CLI command `corpus-stats` | [x] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.

## Implementation Note - 2026-07-01

Track 32 is implemented as a deterministic, fixture-bounded statistics layer:

- `src/nlp_policy_nz/analysis/corpus_statistics.py` loads supplied `PipelineRecord`
  Parquet files or deterministic fixture records, computes per-corpus,
  per-year, entity-type, vector, Māori term, deontic, temporal, and ontology
  summary statistics, and emits JSON, CSV, and Markdown artifacts.
- `data/statistics/` contains checked-in machine-readable statistics tables.
- `docs/corpus_statistics.md` records the publication-ready summary and
  explicit full-corpus/date coverage blockers.
- `nlp-policy-nz corpus-stats` exposes the pipeline for one or more Parquet
  inputs while defaulting to fixture-bounded repo-side output for CI.

## Review Fixes

- [x] Task: Apply review suggestions 097cc9c
