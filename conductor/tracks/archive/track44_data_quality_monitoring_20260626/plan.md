# Track 44: Data Quality & Pipeline Monitoring

**Dependencies**: Track 6, Track 19
**Parallelization Node**: Infrastructure & Quality
**Status**: Archived

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Create `src/nlp_policy_nz/quality/monitoring.py` with schema validation for pipeline inputs | [x] | conductor_orchestrator |
| 2 | Create data drift detector: track corpus statistics and detect shifts | [x] | conductor_orchestrator |
| 3 | Add per-record quality metrics (completeness, parse success, entity density, macron integrity) | [x] | conductor_orchestrator |
| 4 | Create Streamlit or static HTML health dashboard in `scripts/monitoring_dashboard/` | [x] | conductor_orchestrator |
| 5 | Wire quality metrics into Track 19 OTel trace export | [x] | conductor_orchestrator |
| 6 | Create `.github/workflows/quality-alert.yml` for automated degradation alerts | [x] | conductor_orchestrator |
| 7 | Write tests for monitoring, drift detection, and alerting | [x] | conductor_orchestrator |
| 8 | Document monitoring architecture in `docs/data_quality_monitoring.md` | [x] | conductor_orchestrator |
