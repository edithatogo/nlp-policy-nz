# Track 32: Whole-Corpus Descriptive Statistics

**Dependencies**: Tracks 6, 18, 31
**Parallelization Node**: Corpus Analytics
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Define required metrics: document count by corpus (legislation, Hansard, court), token/word/sentence counts, entity density by type, deontic modality distribution, citation graph stats, temporal coverage span, Māori language segment percentage | [ ] | conductor_orchestrator |
| 2 | Define grouping dimensions: by Parliament (Hansard), by Act type/Year (legislation), by Court/Year (case law), by topic/ontology category | [ ] | conductor_orchestrator |
| 3 | Define output table schemas: per-corpus summary, per-year trends, entity co-occurrence matrix, temporal entity histograms | [ ] | conductor_orchestrator |
| 4 | Identify metrics requiring unavailable full-corpus data and add blockers to register | [ ] | conductor_orchestrator |
| 5 | Create `src/nlp_policy_nz/analysis/corpus_statistics.py` with reproducible pipeline: load PipelineRecord parquet -> compute metrics -> aggregate -> emit tables | [ ] | conductor_orchestrator |
| 6 | Add temporal aggregation: year-over-year trends, entity burst detection, vocabulary growth curves | [ ] | conductor_orchestrator |
| 7 | Add ontology-coverage aggregation: count of records per ontology category, per standard, per mapping type | [ ] | conductor_orchestrator |
| 8 | Write fixture-level tests for each aggregator with deterministic sample data; add CLI command `corpus-stats` | [ ] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
