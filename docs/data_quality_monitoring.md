# Data Quality Monitoring

Track 44 adds repo-side data quality monitoring for pipeline validation, drift detection, and run reporting.

## What It Records

- Input validation results for XML, HTML, JSONL, and text inputs.
- Per-record quality metrics for completeness, parse success, entity density, and Māori macron integrity.
- Batch summaries for record count, validation failures, quality score, and corpus-source distribution.
- Drift comparisons against an optional baseline quality report.

## Pipeline Integration

- `process_legislation()` and `process_hansard()` validate every input file before processing.
- Each batch writes a `*.quality.json` sidecar next to the Parquet output.
- The quality summary is attached to the active OpenTelemetry span.

## CLI

```bash
nlp-policy-nz quality validate --input data/hansard/example.xml
nlp-policy-nz quality report --parquet output/hansard.parquet
nlp-policy-nz quality dashboard
nlp-policy-nz quality alert --create-issue
```

## Dashboard

- Static HTML output: `data/quality/dashboard.html`
- Persisted run history: `data/quality/runs/`
- Latest batch report: `data/quality/latest.quality.json`

## Alerting

- The `quality alert` command evaluates the latest report and can create a GitHub issue when the latest run falls below the configured threshold or shows drift.

