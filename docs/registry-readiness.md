# Research Artifact Registry Readiness

Status: `rights_approved_huggingface_metadata_verified_doi_pending`

Roadmap: `research_artifact_registry_readiness_20260721`

This document is the repository-side evidence contract for the research-artifact
registry work. It does not claim that a Zenodo DOI, Hugging Face repository
acceptance, or ontology registry submission has been published or accepted.

## Current evidence

- `data_registry.json` records `nz-legislation-v1`, its version, CC BY 4.0
  licence, deposit URL, DOI, and capture timestamp.
- The package metadata declares an MIT software licence and project version.
- `data/registry/ocr_artifact.json` records the OCR benchmark artifact metadata,
  provenance links to the track131 manifest and track87 engine registry, and
  revision-pinned Hugging Face evidence. Status is `metadata_complete_doi_pending`;
  `doi` and `deposit_url` remain null until an authoritative external record is
  verified (#166).
- `data/registry/huggingface_audit.json` records a dated, revision-pinned audit
  of the existing legislation, Hansard, and cloud-OCR target datasets. It
  preserves the provider-reported differences between `other`, `MIT`, and
  missing card licences. Repository-owner rights approval is recorded there;
  current Hugging Face card revisions and authenticated Croissant responses are
  also recorded (#167).
- `data/registry/ontology_submission_gate.json` records the candidate ontology
  namespace, review-bounded scope, and `no_submission` status. No external
  ontology registry response is claimed (#168).
- The Conductor track and GitHub issues [#165](https://github.com/edithatogo/nlp-policy-nz/issues/165)
  and [#166](https://github.com/edithatogo/nlp-policy-nz/issues/166) through
  [#168](https://github.com/edithatogo/nlp-policy-nz/issues/168) are the canonical
  planning and evidence locations.

## Automatable gates

Repository-side checks enforce the evidence contract without network access:

- `scripts/check_registry_readiness.py` — aggregate contract for all registry
  artefacts and this document.
- `scripts/check_ocr_artifact_registry.py` — OCR artifact paths, manifest
  alignment, Hugging Face revision pinning, and DOI/deposit null gates (#166).
- `scripts/audit_huggingface_targets.py` — offline Hugging Face audit JSON
  validation by default; pass `--network` to probe live Croissant endpoints
  (#167).
- `scripts/check_ontology_submission_gate.py` — ontology candidate artefacts,
  namespace spot-check, and no-submission gate (#168).

## Required repository work

1. Keep the OCR benchmark artifact metadata, provenance, version, checksum, and
   DOI/persistence evidence together (#166).
2. Record the Hugging Face dataset/model licence, card metadata, and Croissant
   or equivalent machine-readable metadata before any publication claim (#167).
3. Treat the proposed ontology namespace as a candidate until its namespace,
   scope, and registry response are documented (#168).

The Hugging Face card and Croissant checks now pass for all three targets.
The remaining registry gate is an authoritative versioned DOI for the OCR
artifact; no DOI or provider acceptance is claimed until that external record
is verified.

## External boundary

External deposit, DOI resolution, Hugging Face publication acceptance, and
ontology registry acceptance require authoritative provider evidence. Local
tests only verify that this contract and its referenced artefacts remain present.
OCR DOI deposit and any future ontology registry response remain external gates
outside the default offline CI workflow.
