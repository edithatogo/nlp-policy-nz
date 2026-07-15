# Track 91 Specification: Cloud OCR Evaluation and Operations

## Goal

Operate the complete extraction system through GitHub Actions and pinned cloud workers with measurable quality, cost, security, and completeness.

## Requirements

- Add validation, shard planning, dispatch, GPU execution, result collection, retry, quarantine, and publication workflows.
- Never process corpus payloads on developer workstations; keep Actions logs free of content and secrets.
- Use OIDC where supported, least-privilege environments, pinned actions/containers, artifact attestations, SBOMs, and high/critical security gates.
- Maintain stratified OCR and extraction benchmarks with CER, WER, reading order, layout, tables, speaker attribution, calibration, throughput, and cost.
- Track every registry row through pending, unavailable, restricted, processed, reviewed, published, or failed states.
- Add budget limits, concurrency controls, idempotent caches, partial reruns, and signed completeness reports.

## Acceptance

A 1-3 volume public pilot completes end to end from GitHub dispatch to Hugging Face staging, then scales through resumable shards without local corpus storage.
