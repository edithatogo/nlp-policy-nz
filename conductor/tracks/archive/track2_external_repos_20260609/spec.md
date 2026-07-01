# Track 2: Configure External Integrations & Data Sovereignty Registry

**Status**: Complete

## Goal

Provide external integration scaffolding for legal-policy datasets while keeping credentialed network activity explicit, configurable, and auditable.

## Scope

- Hugging Face Hub dataset loading helpers for NZ Hansard and legislation datasets.
- Zenodo Sandbox deposit, upload, and publish helpers for archival workflows.
- JSON-backed data sovereignty registry records for dataset provenance.
- Offline tests that verify request construction and local registry behavior without requiring live API calls.

## Acceptance Criteria

- Integration modules expose documented import surfaces under `nlp_policy_nz.integrations`.
- API tokens are supplied by callers or environment variables, not hard-coded.
- Zenodo helpers can be tested with mocked request objects.
- Data sovereignty records preserve dataset identity, storage location, jurisdiction, licensing, consent, access restrictions, and lineage metadata.
- Live Hugging Face and Zenodo operations remain external gates requiring credentials and explicit operator intent.

## Evidence Boundary

Track 2 is complete for repo-side integration scaffolding. It does not claim that live Hugging Face datasets were downloaded or that Zenodo deposits were published in production.
