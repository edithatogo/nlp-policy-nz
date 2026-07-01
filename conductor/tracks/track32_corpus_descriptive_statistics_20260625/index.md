# Track 32: Whole-Corpus Descriptive Statistics

- [Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Metadata](./metadata.json)
- [Evidence](./evidence.md)

## Implementation

- `src/nlp_policy_nz/analysis/corpus_statistics.py`
- `src/nlp_policy_nz/cli/main.py` (`corpus-stats`)
- `tests/test_track32_corpus_statistics.py`
- `tests/test_track32_conductor.py`

## Outputs

- `data/statistics/corpus_statistics_manifest.json`
- `data/statistics/corpus_statistics_per_corpus.csv`
- `data/statistics/corpus_statistics_per_year.csv`
- `data/statistics/corpus_statistics_entity_types.csv`
- `data/statistics/corpus_statistics_ontology_coverage.json`
- `data/statistics/corpus_statistics_blockers.json`
- `docs/corpus_statistics.md`

## Boundary

The checked-in outputs are deterministic, fixture-bounded Track 32 artifacts. Full-corpus publication requires supplied `PipelineRecord` Parquet exports.

