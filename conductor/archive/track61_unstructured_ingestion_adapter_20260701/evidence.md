# Track 61 Evidence

## Implemented Changes

- Added `src/nlp_policy_nz/unstructured_ingestion.py` with an optional
  `UnstructuredIngestionEngine` that partitions local files and emits
  `DocumentChunk` records.
- Added `compare_with_html_parser(...)` so the adapter can be compared against
  the canonical HTML parser on selected fixtures.
- Routed `get_ingestion_engine("UNSTRUCTURED")` through the optional adapter
  in `src/nlp_policy_nz/universal_framework_v3.py`.
- Exported `UnstructuredIngestionEngine` from `src/nlp_policy_nz/__init__.py`.
- Added an optional `unstructured` dependency extra in `pyproject.toml` and an
  opt-in Pixi feature in `pixi.toml`.
- Updated the product, requirements, dependency policy, and tech stack docs to
  mark `unstructured` as fallback-only.
- Added the local Conductor track registry entry in
  `conductor/tracks.md`.

## Validation

- `uv run python -m pytest tests/test_track61_unstructured_ingestion.py -q`
  - Result: `5 passed`
- `uv run python -m ruff check src/nlp_policy_nz/unstructured_ingestion.py src/nlp_policy_nz/universal_framework_v3.py src/nlp_policy_nz/__init__.py tests/test_track61_unstructured_ingestion.py conductor/requirements.md conductor/product.md conductor/dependency-policy-matrix.md conductor/tech-stack.md conductor/tracks.md`
  - Result: `All checks passed!`
- `git diff --check`
  - Result: clean

## Environment Note

- `pixi run pytest` hit a local `msgspec._core` import failure in the Pixi
  environment, so validation was rerun with `uv run python -m pytest` in a
  clean environment.
