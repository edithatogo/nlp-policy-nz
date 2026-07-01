# Track 32 Evidence: Whole-Corpus Descriptive Statistics

## Repo-Side Implementation

- Added `src/nlp_policy_nz/analysis/corpus_statistics.py` and `src/nlp_policy_nz/analysis/__init__.py` for deterministic Track 32 statistics.
- Added `nlp-policy-nz corpus-stats` to export statistics from one or more `PipelineRecord Parquet` files, with deterministic fixture fallback for CI.
- Added checked-in artifacts under `data/statistics/`: `corpus_statistics_manifest.json`, `corpus_statistics_per_corpus.csv`, `corpus_statistics_per_year.csv`, `corpus_statistics_entity_types.csv`, `corpus_statistics_ontology_coverage.json`, and `corpus_statistics_blockers.json`.
- Added `docs/corpus_statistics.md` as the publication-ready summary.
- Added `tests/test_track32_corpus_statistics.py` and `tests/test_track32_conductor.py`.

## Boundaries

- Checked-in statistics are fixture-bounded and do not claim canonical full-corpus coverage.
- True whole-corpus counts, longitudinal completeness, and case-law coverage require external full `PipelineRecord` Parquet inputs.
- Missing full-corpus and date-normalization coverage are recorded in `corpus_statistics_blockers.json`.

## Closeout Validation

- `pixi run python -m pytest -q tests\test_track32_corpus_statistics.py tests\test_track32_conductor.py tests\test_cli.py tests\test_track31_nz_ontologies.py tests\test_track31_conductor.py` passed.
- `pixi run python -m ruff check --no-cache src\nlp_policy_nz\analysis\corpus_statistics.py src\nlp_policy_nz\analysis\__init__.py src\nlp_policy_nz\__init__.py src\nlp_policy_nz\cli\main.py tests\test_track32_corpus_statistics.py tests\test_track32_conductor.py tests\test_cli.py` passed.
- `git diff --check` passed.
