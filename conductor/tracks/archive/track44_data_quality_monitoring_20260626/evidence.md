# Track 44 Evidence

## Implementation Summary

- Added `src/nlp_policy_nz/quality/monitoring.py` with ingestion validation, per-record quality metrics, drift detection, history persistence, dashboard rendering, and span attribute registration.
- Wired validation and quality artifact persistence into `src/nlp_policy_nz/pipeline_api.py` for both legislation and Hansard processing.
- Added CLI support in `src/nlp_policy_nz/cli/main.py` for `quality validate`, `quality report`, `quality dashboard`, and `quality alert`.
- Added a dashboard generator script, alert workflow, documentation, and focused tests for validation, report persistence, trace attributes, and CLI rendering.

## Verification

- `pixi run pytest tests/test_track44_data_quality_monitoring.py tests/test_quality_infrastructure.py -q`
- The Track 44 contract tests passed after isolating subprocess validation and CLI checks to the `py311` environment with `PYTHONPATH=src`.
