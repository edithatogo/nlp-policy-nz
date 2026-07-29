# Implementation Plan

## Phase 1: Readiness and prerequisites

- [x] Confirm scope, rights, licensing, metadata, release, and persistence prerequisites in the parent issue.
- [x] Capture repository-specific validation commands and baseline results.

## Phase 2: Registry deliverables

- [x] [Issue #166](https://github.com/edithatogo/nlp-policy-nz/issues/166) — `data/registry/ocr_artifact.json` and `scripts/check_ocr_artifact_registry.py` record benchmark metadata, provenance links, and revision-pinned Hugging Face evidence. Authoritative versioned DOI remains an external gate; `doi` and `deposit_url` stay null while status is `metadata_complete_doi_pending`. 650aeb8
- [x] [Issue #167](https://github.com/edithatogo/nlp-policy-nz/issues/167) — `data/registry/huggingface_audit.json` is enforced offline via `scripts/audit_huggingface_targets.py` (default) and included in `scripts/check_registry_readiness.py`. Optional `--network` Croissant probes are available but not required in CI. 650aeb8
- [x] [Issue #168](https://github.com/edithatogo/nlp-policy-nz/issues/168) — `data/registry/ontology_submission_gate.json` and `scripts/check_ontology_submission_gate.py` record `no_submission` status, candidate artefacts, and promotion blockers. No external ontology registry acceptance is claimed. 650aeb8

## Phase: Review Fixes

- [x] Task: Apply review suggestions 355c92c

## Phase 3: Reconciliation and closeout

- [x] Reconcile Conductor status, issue state, project state, and recorded rights approval. 650aeb8
- [x] Run the repository's documented validation workflow. 650aeb8
- [x] Archive this track only after all automatable work is complete and every remaining external gate is explicit.
