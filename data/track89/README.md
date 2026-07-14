# Track 89 Multi-Layer Archive Schema

The canonical archive bundle connects source and document identity, page geometry,
regions, immutable source spans, OCR lines/tokens, tables, speeches, embeddings,
semantic assertions, graph edges, and reproducible runs.

Schema version `1.0.0` is materialized through deterministic JSON, JSONL, JSON-LD,
RDF/Turtle, Markdown, and Parquet views. `public_projection()` removes restricted
source text, OCR alternatives, and restricted vectors while retaining identifiers,
rights class, checksums, and source lineage.

The `0.9.0` to `1.0.0` migration is explicit and fail-closed for unknown versions.
