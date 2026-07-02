# Track 59 Evidence

## Summary

- `load_parquet` now uses a Polars core and was faster than pandas on the benchmark fixture.
- `search_chunks` now uses a Polars core and was faster than pandas on the benchmark fixture.
- `compute_stats` still has a Polars helper, but the benchmark on this fixture keeps the public wrapper on the pandas path because the measured result was not strong enough to justify a conversion-heavy default switch.
- The Gradio-facing API still returns pandas DataFrames and plain Python values.

## Validation

- `.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\storage\polars_pipeline.py spaces\app.py scripts\track59_polars_native_pipeline.py tests\test_track59_polars_native_pipeline.py`
- `.venv\Scripts\python.exe -m pytest tests\test_track59_polars_native_pipeline.py tests\test_gradio_space.py -q`
- `.venv\Scripts\python.exe scripts\track59_polars_native_pipeline.py --iterations 5 --output .tmp\track59_polars_native_pipeline.json`
- `git diff --check`

## Benchmark Notes

The benchmark used a 90-row fixture derived from the corpus-browser sample rows.

| Path | Baseline mean | Candidate mean | Decision |
|---|---:|---:|---|
| `load_parquet` | `3.37996 ms` | `2.46186 ms` | Polars |
| `search_chunks` | `4.39656 ms` | `2.43328 ms` | Polars |
| `compute_stats` | `1.96772 ms` | `2.69328 ms` | pandas |

## Closeout

Track 59 is complete as a local Polars substitution for the corpus-browser hot
paths, with the public UI boundary left unchanged and the dependency policy
recorded for future follow-up.
