# Research Artifact Registry Readiness

Status: `repository_ready_external_gates_pending`

Roadmap: `research_artifact_registry_readiness_20260721`

This document is the repository-side evidence contract for the research-artifact
registry work. It does not claim that a Zenodo record, Hugging Face repository,
or ontology registry submission has been published or accepted.

## Current evidence

- `data_registry.json` records `nz-legislation-v1`, its version, CC BY 4.0
  licence, deposit URL, DOI, and capture timestamp.
- The package metadata declares an MIT software licence and project version.
- The Conductor track and GitHub issues [#165](https://github.com/edithatogo/nlp-policy-nz/issues/165)
  and [#166](https://github.com/edithatogo/nlp-policy-nz/issues/166) through
  [#168](https://github.com/edithatogo/nlp-policy-nz/issues/168) are the canonical
  planning and evidence locations.

## Required repository work

1. Keep the OCR benchmark artifact metadata, provenance, version, checksum, and
   DOI/persistence evidence together (#166).
2. Record the Hugging Face dataset/model licence, card metadata, and Croissant
   or equivalent machine-readable metadata before any publication claim (#167).
3. Treat the proposed ontology namespace as a candidate until its namespace,
   scope, and registry response are documented (#168).

## External boundary

External deposit, DOI resolution, Hugging Face publication, and ontology
registry acceptance require authoritative provider evidence. Local tests only
verify that this contract and its referenced artefacts remain present.
