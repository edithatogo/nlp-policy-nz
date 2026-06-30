<!-- vale off -->

# Pydantic v2 vs msgspec Evaluation

Track 23 reviewed where `pydantic` v2 may fit alongside the existing `msgspec`
pipeline schema.

## Recommendation

Keep `msgspec` as the canonical pipeline struct and Parquet-facing serializer.
It is already used by `PipelineRecord`, has a small runtime surface, and fits
the project goal of fast local corpus processing.

Use `pydantic` v2 at API boundaries where FastAPI request/response models,
OpenAPI schema generation, and user-facing validation errors matter. The
measured JSON round-trip benchmark on this schema removes the performance
objection to that boundary choice.

## Measured Benchmark

Track 23 benchmarked a representative `PipelineRecord` JSON round-trip over a
128-record batch (`175,366` bytes):

| Library | Decode avg | Encode avg | Round-trip avg |
| --- | ---: | ---: | ---: |
| `msgspec` | `11.940 ms` | `0.556 ms` | `12.496 ms` |
| `pydantic` v2 | `2.910 ms` | `1.002 ms` | `3.912 ms` |

Both libraries produced identical JSON bytes for the benchmark payload.

## Practical Boundary

| Layer | Recommended validator | Reason |
| --- | --- | --- |
| Pipeline records | `msgspec` | Fast struct validation and low overhead |
| Parquet/storage paths | `msgspec` plus schema tests | Keeps the corpus path compact |
| FastAPI request payloads | `pydantic` v2 | Better OpenAPI and error messages |
| Internal model training specs | dataclasses or `msgspec` | Avoid API-framework coupling |

## Next Gate

If the API grows beyond a thin FastAPI boundary, benchmark the request/response
payloads in that shape too. For now, the pipeline path should stay on
`msgspec`, and `pydantic` v2 can be considered for server-facing validation.

<!-- vale on -->
