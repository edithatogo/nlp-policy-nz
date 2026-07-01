# Track 55 Evidence

## Phase 1: Export Schema Foundation

The initial broad extraction framework slice is implemented:

- `src/nlp_policy_nz/extraction/schemas.py` defines Pydantic 2 models for
  extraction families, source spans, source traces, extraction records,
  summaries, and manifests.
- `ExtractionFamily` includes rules-as-code as one family alongside
  definitions, obligations, powers, dates, entities, amendments, penalties,
  review rights, and other legislative outputs.
- `render_extraction_manifest_json()` uses `orjson` for deterministic JSON.
- `pyproject.toml` and `pixi.toml` declare Pydantic 2, `orjson`, `pypdf`,
  `PyYAML`, and `sqlite-utils` for extraction schemas, fast JSON export,
  optional PDF ingestion, future YAML manifests, and local catalogs.

## Verification

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_extraction_schemas.py tests\test_track54_axiom_conductor.py
.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\extraction tests\test_extraction_schemas.py
& 'C:\Users\60217257\.pixi\bin\pixi.exe' install
& 'C:\Users\60217257\.pixi\bin\pixi.exe' run pytest -q tests/test_extraction_schemas.py
```

Latest result: 7 tests passed, Ruff passed, and Pixi installed the refreshed
default environment. The Pixi extraction schema test also passed with 3 tests.

Combined extraction, Axiom, rules-as-code, and Conductor focused validation:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py
.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\extraction src\nlp_policy_nz\axiom src\nlp_policy_nz\ontology\rac_bridge.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py
```

Latest result: 25 tests passed and Ruff passed.

## Phase 2: Extractor Manifest and Trace Contracts

The second framework slice is implemented:

- `ExtractorSpec` and `ExtractorManifest` describe versioned extraction modules
  and their produced fields without coupling the project to a runtime engine.
- `KnownGap`, `GapType`, and `GapStatus` provide the Axiom-style ratchet shape
  for corpus, parser, extraction, and validation debt.
- `SourceTraceReport` and `source_trace_reports_from_records()` group extracted
  records by citation path and source SHA256 so downstream consumers can audit
  which records came from which checksum-pinned source spans.
- `render_extractor_manifest_yaml()` emits review-friendly YAML for extractor
  catalogs and handoff documents.
- `tests/test_extraction_schemas.py` covers stable extractor YAML rendering,
  duplicate extractor rejection, trace report grouping, invalid empty trace
  reports, known gaps, and extraction manifest trace report generation.

## Phase 2 Verification

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_extraction_schemas.py
.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\extraction tests\test_extraction_schemas.py
```

Latest result: 6 extraction schema tests passed and Ruff passed after import
ordering fixes.

Combined extraction, Axiom, rules-as-code, and Conductor focused validation:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py
.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\extraction src\nlp_policy_nz\axiom src\nlp_policy_nz\ontology\rac_bridge.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py
```

Latest result: 28 tests passed and Ruff passed.

## Phase 3 Partial: Downstream Consumer Documentation

`docs/extraction-framework.md` documents the public extraction contract for
downstream projects:

- extraction manifests as the stable handoff artifact;
- source identity using citation path plus source SHA256;
- rules-as-code candidates as one extraction family;
- the current library baseline; and
- Track 56 runtime acceleration candidates for future profiling-driven adoption.

## Phase 3 Partial: Pipeline Manifest Export

Pipeline records can now be exported as deterministic extraction manifests:

- `extraction_manifest_from_pipeline_records()` converts in-memory
  `PipelineRecord` rows into source-grounded `ExtractionManifest` objects.
- `export_extraction_manifest_from_parquet()` loads existing pipeline Parquet
  output and writes manifest JSON.
- The `export-extractions` CLI command exposes the Parquet-to-manifest path with
  explicit `--retrieved-at` provenance and configurable `--source-url-base`.
- `tests/test_extraction_exporter.py` covers broad family extraction from local
  records and the CLI manifest writer using temporary Parquet fixtures.

## Phase 3 Partial Verification

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_extraction_exporter.py tests\test_extraction_schemas.py
.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\extraction src\nlp_policy_nz\cli\main.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py
```

Latest result: 8 tests passed and Ruff passed.

Combined extraction, Axiom, rules-as-code, and Conductor focused validation
after adding the exporter:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py
.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\extraction src\nlp_policy_nz\axiom src\nlp_policy_nz\ontology\rac_bridge.py src\nlp_policy_nz\cli\main.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py
```

Latest result: 30 tests passed and Ruff passed.

A broader run including all of `tests/test_cli.py` was stopped after it hung in
the existing full CLI test file. The new CLI path is covered by the focused
temporary-Parquet exporter test above.

## Phase 3 Complete: SQLite Catalog and Stale-Source Audits

The optional local catalog is implemented:

- `initialise_extraction_catalog()` creates the SQLite schema.
- `write_manifest_to_catalog()` stores manifest run metadata and per-record
  source identities.
- `list_catalog_runs()` returns recorded run summaries.
- `report_catalog_source_staleness()` compares stored citation path/source hash
  pairs against current source text and reports `current`, `stale`, or
  `missing` without mutating catalog data.
- `tests/test_extraction_catalog.py` covers run recording and current, stale,
  and missing source audit results with local fixtures.

## Phase 3 Final Verification

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py
.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\extraction tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py
```

Latest result: 10 tests passed and Ruff passed.

Combined extraction, Axiom, rules-as-code, and Conductor focused validation
after completing the catalog:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py
.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\extraction src\nlp_policy_nz\axiom src\nlp_policy_nz\ontology\rac_bridge.py src\nlp_policy_nz\cli\main.py tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py
```

Latest result: 32 tests passed and Ruff passed.

## Conductor Registry Synchronization

Track 55 is marked complete in:

- `conductor/tracks.md`;
- `metadata.json`; and
- `plan.md`.

`tests/test_track55_56_conductor.py` verifies the registry marker, required
track files, metadata, plan status, and evidence content for Tracks 55 and 56.

Final focused validation:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track55_56_conductor.py tests\test_track56_extraction_runtime.py tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py
.\.venv\Scripts\python.exe -m ruff check tests\test_track55_56_conductor.py tests\test_track56_extraction_runtime.py tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py scripts\benchmark_extraction_manifest_runtime.py src\nlp_policy_nz\extraction src\nlp_policy_nz\axiom src\nlp_policy_nz\ontology\rac_bridge.py src\nlp_policy_nz\cli\main.py
```

Latest result: 37 tests passed and Ruff passed.
