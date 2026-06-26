# Track 44: Data Quality & Pipeline Monitoring

**Dependencies**: Track 6, Track 19
**Parallelization Node**: Infrastructure & Quality
**Status**: Planned

## Goal

Implement data quality monitoring across the pipeline: schema validation on ingestion, data drift detection for corpus changes, per-record quality metrics, and a health dashboard for monitoring pipeline runs.

## Scope

- **Ingestion Schema Validation**: Pydantic/msgspec validation on pipeline inputs (XML, HTML, JSONL) before processing
- **Data Drift Detection**: Track distribution shifts in corpus statistics (document length, entity density, language distribution) over time
- **Quality Metrics**: Per-record quality scores (completeness, parse success rate, entity density, Māori macron integrity)
- **Pipeline Health Dashboard**: Streamlit or static HTML dashboard showing run history, pass/fail rates, quality trends
- **Alerting**: GitHub issue creation or email notification on quality degradation below thresholds
- **Integration with Track 19 OTel spans**: Correlate quality metrics with tracing spans for end-to-end observability

## Acceptance Criteria

- [ ] Input schema validation runs on every pipeline invocation and logs structured errors
- [ ] Data drift detector reports distribution shifts in corpus statistics per run
- [ ] Quality metrics computed and stored per PipelineRecord batch
- [ ] Health dashboard renders run history with pass/fail and quality trends
- [ ] Quality degradation below configurable threshold triggers GitHub issue alert
- [ ] All monitoring data queryable via CLI or API
