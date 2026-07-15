# Track 90 Specification: Hugging Face Archive Publication

## Goal

Publish discoverable, streaming-friendly, rights-safe structured HathiTrust-NZ products through the existing Hugging Face collection and child datasets.

## Requirements

- Materialize inventory, documents, pages, blocks, tokens, speeches, entities/relations, topics/embeddings, graph, and quality/provenance configurations.
- Partition large tables, validate Dataset Viewer compatibility, and use content-addressed image/object references.
- Generate dataset cards with coverage, rights, quality bands, source citations, limitations, schema versions, and DOI links.
- Produce immutable release manifests, checksums, SBOM/attestations, and Zenodo handoff metadata.
- Support dry-run, staging, idempotent resume, rollback, and fail-closed publication.

## Acceptance

Smoke publication proves streaming loads and cross-configuration joins; no restricted content can reach a public repository.
