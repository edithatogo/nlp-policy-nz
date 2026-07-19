# Track 86 Contract Artifacts

- `hathi_capability_registry.json` is the stable read-only capability snapshot for future CLI, API, SDK, and MCP adapters.
- `render_hathi_json_schema()` in `nlp_policy_nz.extraction.hathi_ingestion` emits the versioned JSON Schema for archive items.
- These artifacts describe metadata and work planning only. Corpus acquisition remains delegated to cloud workflows.

Rights provenance is represented by `HathiRightsEvidence`, which requires a controlled basis, authoritative record URI,
immutable snapshot hash, timezone-aware access time, territorial applicability, and separate permissions for acquisition,
processing, full-text publication, and derived-feature publication. Public full-text routing fails closed unless the
record contains affirmative evidence for all required purposes in New Zealand. No live rights evidence is included here.

The Hathi capability entries deliberately use `not_implemented` for CLI, API, SDK, and MCP surfaces. They are metadata
only until executable adapters and conformance tests exist.
