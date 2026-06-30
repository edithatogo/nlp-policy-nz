# Extraction Runtime Direction

Track 56 evaluates faster and Rust-backed runtime options for the broad
legislation extraction framework.

## Current Decision

Keep the public extraction contract on Pydantic 2 and continue using `orjson`
for deterministic JSON export. Do not add a custom Rust/PyO3 extension until a
profiled extraction hot path is both stable and too slow for Python-level
optimisation.

## Local Benchmark

`scripts/benchmark_extraction_manifest_runtime.py` compares:

- stdlib JSON over `model_dump(mode="json")`;
- Pydantic 2 `model_dump_json()`;
- `msgspec` JSON over the dumped manifest payload;
- the package `orjson` manifest renderer;
- direct `orjson` rendering over the dumped manifest payload; and
- a Polars table projection for bulk analytics.

The checked local evidence is
`artifacts/track56/extraction_manifest_runtime_50.json`.

For that fixture, direct `orjson` was the fastest JSON lane. Polars produced a
smaller table projection, but that projection is not a substitute for the
source-grounded manifest because it drops nested trace and attribute structure.

## Dependency Policy

Core:

- Pydantic 2 for public manifest schemas.
- `orjson` for deterministic JSON output.
- Existing `msgspec` pipeline structs for internal pipeline rows.

Optional:

- Polars/Arrow projections for bulk analytics, reports, and tabular export.
- Rust-backed tokenizers only where they preserve exact source spans and
  outperform the current spaCy/tokenizer path in a measured fixture.

Rejected for now:

- Custom PyO3/maturin extensions for extraction manifests.
- Executable rules-engine runtimes in this package.

## Next Gate

Before adding any Rust extension, capture a profile showing:

- the hot path is in extraction or serialization code owned by this package;
- Python-level improvements have already been tried;
- the FFI boundary can preserve citation paths, source SHA256 pins, character
  spans, and Pydantic-compatible output; and
- a benchmark regression gate can run offline with local fixtures.

## Future FFI Boundary

If a Rust extension becomes justified, it should sit behind a narrow Python
adapter and exchange plain data structures only. The boundary must preserve the
public Pydantic manifest contract.

Allowed inputs:

- normalized source text;
- citation path;
- source SHA256;
- source URL;
- retrieved timestamp; and
- extractor configuration with explicit version fields.

Allowed outputs:

- record ID;
- extraction family;
- label;
- raw and normalized values;
- confidence;
- character spans in the normalized source text; and
- JSON-compatible attributes.

Not allowed across the FFI boundary:

- `PipelineRecord` objects;
- Pydantic model instances;
- executable RuleSpec or rules-engine objects;
- network clients; or
- database connections.

The Python adapter must convert Rust output into `ExtractionRecord`,
`SourceTrace`, and `ExtractionManifest` instances, then run the same validation
and benchmark gates as the pure Python path.
