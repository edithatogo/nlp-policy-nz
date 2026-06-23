# Pydantic v2 vs msgspec Evaluation

Track 23 reviewed where `pydantic` v2 may fit alongside the existing `msgspec`
pipeline schema.

## Recommendation

Keep `msgspec` for high-throughput pipeline records and Parquet-facing
serialization. It is already used by `PipelineRecord`, has a small runtime
surface, and fits the project goal of fast local corpus processing.

Use `pydantic` v2 only at API boundaries where FastAPI request/response models,
OpenAPI schema generation, and user-facing validation errors are more valuable
than raw serialization speed.

## Practical Boundary

| Layer | Recommended validator | Reason |
| --- | --- | --- |
| Pipeline records | `msgspec` | Fast struct validation and low overhead |
| Parquet/storage paths | `msgspec` plus schema tests | Keeps the corpus path compact |
| FastAPI request payloads | `pydantic` v2 | Better OpenAPI and error messages |
| Internal model training specs | dataclasses or `msgspec` | Avoid API-framework coupling |

## Next Gate

Before adding `pydantic` as a runtime dependency, benchmark representative API
payload validation and confirm it does not pull the core corpus pipeline away
from the existing `msgspec` contract.
