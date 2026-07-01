# Whole-Corpus Descriptive Statistics

Track 32 provides deterministic descriptive statistics for supplied pipeline records
and checked-in ontology artifacts. The checked-in report is fixture-bounded until
canonical whole-corpus Parquet exports are supplied.

## Summary

- Records: 3
- Corpora represented: 3
- Years represented: 3
- Entity types: 3
- Known blockers: 4

## Per-corpus coverage

| Corpus | Records | Tokens | Citations | Entities | Deontic | Temporal |
|---|---:|---:|---:|---:|---:|---:|
| court | 1 | 10 | 0 | 1 | 0 | 1 |
| hansard | 1 | 11 | 0 | 1 | 1 | 1 |
| legislation | 1 | 14 | 1 | 2 | 2 | 1 |

## Temporal coverage

- Years: 2023, 2024, 2025

## Ontology coverage

- Track 25 rows: 29
- Track 29 mappings: 12
- Track 30 inferred candidates: 4
- Track 31 NZ concepts: 10

## Blockers

- `full-corpus-inputs`: No canonical whole-corpus Parquet inventory is checked into this repo; statistics are bounded to supplied inputs or deterministic fixtures.
- `date-coverage`: Not every PipelineRecord guarantees normalized temporal metadata.
- `case_law-parquet-missing`: No case_law PipelineRecord rows were supplied.
- `track28-analytics-measurement`: Track 28 identified analytics measurement model work for Track 32.
