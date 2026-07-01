# Track 56 Evidence

## Phase 1: Baseline and Candidate Selection

Implemented a local benchmark harness:

- `scripts/benchmark_extraction_manifest_runtime.py` builds synthetic
  `PipelineRecord` rows, exports them through the Track 55 extraction manifest
  path, and compares stdlib JSON, Pydantic 2 JSON, `msgspec`, `orjson`, and a
  Polars table projection.
- `tests/test_track56_extraction_runtime.py` verifies the benchmark evidence
  contract without asserting brittle timing thresholds.
- `artifacts/track56/extraction_manifest_runtime_50.json` records a local
  measured run with 50 pipeline records and 400 extraction records.

## Measured Local Run

Command:

```powershell
.\.venv\Scripts\python.exe scripts\benchmark_extraction_manifest_runtime.py --records 50 --iterations 3 --evidence artifacts\track56\extraction_manifest_runtime_50.json
```

Results from this run:

| Lane | Avg ms | P95 ms | Output bytes | Status |
| --- | ---: | ---: | ---: | --- |
| stdlib JSON | 11.418467 | 14.3291 | 344645 | measured |
| Pydantic `model_dump_json` | 5.093067 | 7.5345 | 344645 | measured |
| `msgspec` JSON | 8.367433 | 14.7435 | 344645 | measured |
| `orjson` helper | 5.7108 | 6.2407 | 344646 | measured |
| `orjson` direct | 3.5227 | 3.8124 | 344645 | measured |
| Polars table projection | 6.595567 | 16.2083 | 95941 | measured |

Interpretation:

- Keep Pydantic 2 as the public schema layer.
- Keep `orjson` for deterministic JSON export; the direct `orjson` lane is the
  fastest JSON renderer in this fixture.
- Treat Polars/Arrow as a bulk analytics/export projection, not a replacement
  for source-grounded JSON manifests.
- Do not add a custom Rust/PyO3 extension yet. The current bottleneck is not
  proven severe enough to justify an FFI boundary.

## Verification

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track56_extraction_runtime.py
.\.venv\Scripts\python.exe -m ruff check scripts\benchmark_extraction_manifest_runtime.py tests\test_track56_extraction_runtime.py
```

Latest result: 1 test passed and Ruff passed.

## Phase 3 Partial: Dependency Policy Documentation

Runtime dependency policy is documented outside Conductor:

- `docs/extraction-runtime.md` records the current decision to keep Pydantic 2
  and `orjson` in the core path, use Polars/Arrow as optional table projections,
  defer custom PyO3/maturin extensions, and keep executable rules engines
  downstream.
- `docs/extraction-framework.md` links the extraction framework to that runtime
  policy.

## Focused Regression Verification

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track56_extraction_runtime.py tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py
.\.venv\Scripts\python.exe -m ruff check scripts\benchmark_extraction_manifest_runtime.py src\nlp_policy_nz\extraction tests\test_track56_extraction_runtime.py tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py
```

Latest result: 11 tests passed and Ruff passed.

## Phase 2 and 3 Complete: Rust Deferral and FFI Boundary

The optional Rust/PyO3 path is explicitly deferred:

- Phase 1 benchmark results do not justify adding a custom extension for
  extraction manifest rendering.
- `docs/extraction-runtime.md` now defines a future FFI boundary if profiling
  later justifies a Rust component.
- The boundary allows plain normalized source inputs and JSON-compatible
  extraction outputs, and rejects `PipelineRecord` objects, Pydantic model
  instances, executable RuleSpec objects, network clients, and database
  connections across FFI.
- `tests/test_track56_extraction_runtime.py` verifies both the benchmark
  evidence contract and the runtime policy documentation.

Verification:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track56_extraction_runtime.py
.\.venv\Scripts\python.exe -m ruff check scripts\benchmark_extraction_manifest_runtime.py tests\test_track56_extraction_runtime.py
```

Latest result: 2 tests passed and Ruff passed.

Combined extraction, Axiom, rules-as-code, Track 54, Track 55, and Track 56
focused validation:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track56_extraction_runtime.py tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py
.\.venv\Scripts\python.exe -m ruff check scripts\benchmark_extraction_manifest_runtime.py src\nlp_policy_nz\extraction src\nlp_policy_nz\axiom src\nlp_policy_nz\ontology\rac_bridge.py src\nlp_policy_nz\cli\main.py tests\test_track56_extraction_runtime.py tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py
```

Latest result: 34 tests passed and Ruff passed.

## Conductor Registry Synchronization

Track 56 is marked complete in:

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
