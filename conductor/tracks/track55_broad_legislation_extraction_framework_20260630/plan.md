# Track 55: Broad Legislation Extraction Framework

**Dependencies**: Tracks 4, 10, 11, 14, 15, 18, 26, 27, 54
**Parallelization Node**: Source-Grounded Legislative Extraction
**Status**: Complete

## Phase 1: Export Schema Foundation

**Status**: Complete

| # | Task | Status | Evidence |
|---|------|--------|----------|
| 1.1 | Add Pydantic 2 extraction family, span, source trace, record, summary, and manifest schemas | [x] | `src/nlp_policy_nz/extraction/schemas.py` |
| 1.2 | Add deterministic JSON rendering for extraction manifests using fast JSON serialization | [x] | `render_extraction_manifest_json()` |
| 1.3 | Add tests for extraction family coverage, source trace validation, summary consistency, and span validation | [x] | `tests/test_extraction_schemas.py` |
| 1.4 | Declare Pydantic 2 and supporting extraction dependencies | [x] | `pyproject.toml`, `pixi.toml` |
| 1.5 | Task: Conductor - User Manual Verification 'Phase 1: Export Schema Foundation' (Protocol in workflow.md) | [x] | Focused pytest, Ruff, and Pixi extraction schema test passed |

## Phase 2: Extractor Manifest and Trace Contracts

**Status**: Complete

| # | Task | Status | Evidence |
|---|------|--------|----------|
| 2.1 | Define extractor manifest schema for obligations, definitions, dates, entities, amendments, and rules-as-code | [x] | `ExtractorManifest`, `ExtractorSpec` |
| 2.2 | Add source-to-output trace report format that maps records to checksum-pinned source spans | [x] | `SourceTraceReport`, `source_trace_reports_from_records()` |
| 2.3 | Add known-gap ratchet schema for corpus, parser, and extraction debt | [x] | `KnownGap`, `GapType`, `GapStatus` |
| 2.4 | Add fixture tests for trace manifests and gap ratchets | [x] | `tests/test_extraction_schemas.py` |
| 2.5 | Task: Conductor - User Manual Verification 'Phase 2: Extractor Manifest and Trace Contracts' (Protocol in workflow.md) | [x] | Focused pytest and Ruff validation passed |

## Phase 3: CLI and Storage Integration

**Status**: Complete

| # | Task | Status | Evidence |
|---|------|--------|----------|
| 3.1 | Add CLI command or option to emit extraction manifests from existing pipeline records | [x] | `export-extractions`, `export_extraction_manifest_from_parquet()` |
| 3.2 | Add optional SQLite-backed extraction catalog for run summaries and stale-output audits | [x] | `src/nlp_policy_nz/extraction/catalog.py` |
| 3.3 | Add documentation for downstream consumers using extraction manifests | [x] | `docs/extraction-framework.md` |
| 3.4 | Add integration tests with local fixtures only | [x] | `tests/test_extraction_exporter.py` |
| 3.5 | Task: Conductor - User Manual Verification 'Phase 3: CLI and Storage Integration' (Protocol in workflow.md) | [x] | Focused pytest and Ruff validation passed |
