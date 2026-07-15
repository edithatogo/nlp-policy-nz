# Track 89 Specification: Multi-Layer Archive Schema

## Goal

Define lossless, versioned schemas that connect archive objects, page geometry, OCR observations, parliamentary structure, semantic assertions, and provenance.

## Requirements

- Add document, page, region, line, token, table, speech, entity/relation, embedding, graph, and run schemas.
- Support normalized and original coordinates, text alternatives, confidence calibration, review state, and immutable source traces.
- Export deterministic Parquet, JSONL, JSON-LD/PROV-O, RDF, Markdown, and graph views without losing lineage.
- Version schemas and migrations; validate referential integrity and round trips.
- Keep restricted source text out of public exports while retaining safe metadata lineage.

## Acceptance

Contract, migration, round-trip, property, and adversarial rights tests pass under strict typing and coverage gates.
