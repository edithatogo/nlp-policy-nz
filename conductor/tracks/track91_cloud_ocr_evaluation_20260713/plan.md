# Track 91 Plan

## Phase 1: Secure Orchestration
- [x] Add threat-model and workflow tests for permissions, secrets, content leakage, and provenance.
- [x] Implement validate, plan, dispatch, collect, retry, quarantine, and publish workflows.

## Phase 2: Evaluation and Control
- [x] Add benchmark dashboards, calibrated promotion gates, budget/concurrency limits, and drift alerts.
- [x] Add row-level completeness ledger and signed run reports.

## Phase 3: Pilot and Scale
- [~] Complete a public 1-3 volume end-to-end pilot with no local corpus storage.
- [x] Prove resumable sharding, failure recovery, publication rollback, and checkpoint evidence locally.

### Acceptance Boundary
- Repo-side orchestration is metadata-only and covered by `tests/test_cloud_ocr_operations.py` and `tests/test_track91_workflow.py`.
- The public 1-3 volume pilot remains an external GitHub/cloud/Hugging Face gate and is not claimed complete without a live run report.
- Repo-side implementation checkpoints: `507f3b5`, `968c2d1`.
