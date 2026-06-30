---
title: Operations runbook
description: Deployment, monitoring, backup, restore, and failure recovery.
---

# Operations runbook

## Deployment

1. Run CI and docs checks on the pull request.
2. Merge to `master`.
3. Let GitHub Actions build packages, docs, benchmarks, and release artifacts.
4. Verify published artifacts and API health endpoints.

## Monitoring

Use OpenTelemetry spans, structured logs, benchmark reports, and API health
checks to distinguish application failures from data or dependency failures.

## Backup and restore

- Keep raw source manifests, checksums, and Parquet outputs in versioned object
  storage.
- Keep Zenodo or OSF archives for citable release snapshots.
- Rebuild LanceDB and RDF outputs from Parquet plus source manifests rather than
  treating indexes as the canonical backup.

## Failure recovery

- If source parsing fails, quarantine the source document and preserve the
  original text.
- If vector search fails, serve non-vector metadata outputs while rebuilding the
  index.
- If publication fails, keep local release bundles and retry after credential or
  service validation.
- If CI benchmarks regress, inspect the uploaded HTML report before updating the
  baseline.
