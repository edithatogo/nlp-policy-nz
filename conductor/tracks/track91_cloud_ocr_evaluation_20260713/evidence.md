# Track 91 Evidence

## Repo-side gates

- The cloud OCR workflow is manually dispatched, least-privilege for repository contents, concurrency-controlled, and artifact-based.
- The orchestration contract creates deterministic metadata-only shards, tracks every row through explicit lifecycle states, enforces cost/concurrency/retry limits, supports partial retry, and writes signed run reports.
- The CLI now serializes the real `CloudRunPlan` through validation, planning, collection, retry, quarantine, and publication stages; publication rejects pending, failed, or quarantined rows.
- The workflow requires a digest-pinned worker image, consumes an explicit worker result manifest, enforces the configured volume limit, and signs complete publication reports from the GitHub environment secret.
- Focused Track 91 tests cover workflow security assertions, pilot volume limits, metadata-plan construction, plan preservation, worker-state collection, signed publication reports, shard determinism, rights-aware restricted routing, transitions, retry, and budget gates.

## External gate

The public 1-3 volume cloud pilot requires configured GitHub environments, cloud worker credentials/OIDC trust, a real OCR worker, and Hugging Face staging. No live run report is claimed until those external services produce signed checkpoint evidence.

The workflow requires a repository path to a metadata-only item manifest. It does not accept corpus payloads, and it remains fail-closed when that manifest or a worker checkpoint is unavailable.
