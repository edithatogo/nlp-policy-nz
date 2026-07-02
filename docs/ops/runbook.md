# Production Runbook

## Common Failure Scenarios

1. API down: check the process supervisor, then inspect `uvicorn` logs and the `/health` response.
2. Database corruption: stop writes, restore the latest LanceDB backup, then re-run the pipeline smoke tests.
3. Model load failure: verify model artifacts and `HF_TOKEN`, then retry with embeddings disabled.
4. Pipeline hang: inspect in-flight jobs, confirm worker saturation, and restart after draining active requests.
5. HF / Zenodo auth failure: verify environment-specific secrets and retry the publication job in staging first.
6. Rate limit exceeded: confirm client IP / token usage, then increase the per-minute limit only if justified.

## Recovery Notes

- Prefer rolling restarts over hard process termination.
- Keep `VERSION.json` and `CITATION.cff` synchronized with the current release metadata.
- Record incident timestamps in the deployment log before making manual changes.
