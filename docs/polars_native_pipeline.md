# Polars-Native Corpus Pipeline Boundary

Track 59 introduces a small Polars core for the hottest tabular corpus-browser
paths while keeping the external UI contract stable.

## Decision

| Surface | Status | Rationale |
|---|---|---|
| `src/nlp_policy_nz/storage/polars_pipeline.py` | Polars-native core | Loads Parquet and searches chunks through Polars so the hottest paths stay Rust-backed. The stats helper remains benchmarked but is not the default wrapper. |
| `spaces/app.py` | Hybrid boundary | The Gradio app still returns pandas DataFrames and plain Python values to keep the current UI contract unchanged. |
| `load_parquet` / `search_chunks` | Hybrid wrapper | Public functions continue to present the existing API while delegating to the Polars core internally. |
| `compute_stats` | pandas-first | The small stats aggregation is fast enough in pandas and does not justify the extra conversion overhead here. |
| Graph, citation, and publication tab builders | Pandas-first for now | These surfaces are not the hottest path and do not need a rewrite to satisfy Track 59. |

## Benchmark Boundary

Track 59 benchmarks the current pandas baseline against the Polars candidate
for:

- Parquet load
- Chunk search
- Corpus stats

The benchmark remains fixture-sized so it can run in GitHub Actions and on the
Windows workstation without requiring full-corpus inputs.
