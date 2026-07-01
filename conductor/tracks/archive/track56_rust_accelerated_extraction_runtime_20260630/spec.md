# Track 56: Rust-Accelerated Extraction Runtime

**Dependencies**: Tracks 21, 23, 42, 55
**Parallelization Node**: Performance and Runtime Modernization
**Status**: Complete

## Goal

Evaluate and incrementally adopt Rust-backed or bleeding-edge libraries where
they improve extraction throughput, schema validation, serialization, parsing,
or downstream handoff without destabilizing the public Python API.

## Candidate Directions

- Keep Pydantic 2 for public schemas, backed by `pydantic-core`.
- Continue using `msgspec` where internal high-throughput serialization is
  measurably better.
- Use `orjson` for fast deterministic JSON export.
- Use Polars and Arrow-native layouts for corpus-scale extraction tables.
- Evaluate Rust-backed tokenization and parsing libraries where they improve
  span alignment or throughput.
- Consider PyO3/maturin extensions only after Python implementations have
  measured bottlenecks.
- Keep executable `axiom-rules-engine` style runtime outside the core package
  unless a concrete downstream contract requires it.

## Acceptance Criteria

- [x] Benchmark current Python/Pydantic/msgspec/orjson extraction rendering.
- [x] Identify bottlenecks before adding any custom Rust extension.
- [x] Define a stable FFI boundary for any future Rust component.
- [x] Keep Python API and Pydantic export schemas stable.
- [x] Document which experimental dependencies are optional.
