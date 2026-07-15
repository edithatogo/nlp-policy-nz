# Track 91 Evidence

## Repo-side gates

- The cloud OCR workflow is manually dispatched, least-privilege for repository contents, concurrency-controlled, and artifact-based.
- The orchestration contract creates deterministic metadata-only shards, tracks every row through explicit lifecycle states, enforces cost/concurrency/retry limits, supports partial retry, and writes signed run reports.
- The CLI now serializes the real `CloudRunPlan` through validation, planning, collection, retry, quarantine, and publication stages; publication rejects pending, failed, or quarantined rows.
- The workflow requires a digest-pinned worker image, consumes an explicit worker result manifest, enforces the configured volume limit, and signs complete publication reports from the GitHub environment secret.
- Focused Track 91 tests cover workflow security assertions, pilot volume limits, metadata-plan construction, plan preservation, worker-state collection, signed publication reports, shard determinism, rights-aware restricted routing, transitions, retry, and budget gates.

## Pilot completion

The public pilot completed at zero cost on 2026-07-15 using a standard GitHub-hosted runner. The Python 3.14 non-root worker uses Tesseract and Poppler, is published with SBOM and provenance, and was invoked by immutable digest `sha256:df4c77cb3522cbbd454fadc25ee081ad2b737af72f71da464005c49d6ffeb965`.

The final successful run is https://github.com/edithatogo/nlp-policy-nz/actions/runs/29419384268. It validated and hashed the public pilot source on GitHub, dispatched the worker, collected row-level transitions, reconciled retries/quarantine, produced a signed publication report, passed the pilot gate with a hard `max_cost_usd=0`, and staged the approved metadata evidence on Hugging Face.

The public staging evidence is https://huggingface.co/datasets/edithatogo/nlp-policy-nz-cloud-ocr-pilots/tree/main/cloud-ocr-runs/track91-zero-cost-hf-20260715. The directory contains exactly `pilot-gate.json`, `reconciled.json`, and `run-report.json`; the public Hub API verified all three files after upload. No corpus payload was processed on a developer workstation or uploaded to this evidence dataset. Hugging Face Jobs, Kaggle, Colab, and commercial cloud OCR were not required.

The workflow requires a repository path to a metadata-only item manifest. It does not accept corpus payloads, and it remains fail-closed when that manifest or a worker checkpoint is unavailable. The protected `CLOUD_OCR_SIGNING_KEY` remains configured for signed publication runs.

Live integration defects discovered during the pilot were fixed and merged in PRs #124-#127: explicit Hugging Face staging, pinned runner tooling, a metadata allow-list uploader using `HfApi`, and the required repository checkout.
