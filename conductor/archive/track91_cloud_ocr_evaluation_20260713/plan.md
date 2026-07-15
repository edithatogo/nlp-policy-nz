# Track 91 Plan

## Phase 1: Secure Orchestration
- [x] Add threat-model and workflow tests for permissions, secrets, content leakage, and provenance.
- [x] Implement validate, plan, dispatch, collect, retry, quarantine, and publish workflows.

## Phase 2: Evaluation and Control
- [x] Add benchmark dashboards, calibrated promotion gates, budget/concurrency limits, and drift alerts.
- [x] Add row-level completeness ledger and signed run reports.

## Phase 3: Pilot and Scale
- [x] Complete a public 1-3 volume end-to-end pilot with no local corpus storage.
- [x] Prove resumable sharding, failure recovery, publication rollback, and checkpoint evidence locally.

### Acceptance Boundary
- Repo-side orchestration is metadata-only and covered by `tests/test_cloud_ocr_operations.py` and `tests/test_track91_workflow.py`.
- The zero-cost one-volume pilot completed from GitHub dispatch through signed publication, pilot gating, and Hugging Face staging without local corpus storage or paid compute: https://github.com/edithatogo/nlp-policy-nz/actions/runs/29419384268.
- Public metadata-only staging evidence: https://huggingface.co/datasets/edithatogo/nlp-policy-nz-cloud-ocr-pilots/tree/main/cloud-ocr-runs/track91-zero-cost-hf-20260715.
- The immutable worker image is `ghcr.io/edithatogo/nlp-policy-nz-cloud-ocr@sha256:df4c77cb3522cbbd454fadc25ee081ad2b737af72f71da464005c49d6ffeb965`.
- Repo-side implementation checkpoints: `507f3b5`, `968c2d1`.
