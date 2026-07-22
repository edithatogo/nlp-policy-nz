# Track 95 Evidence

## Repository-side implementation

- The OCR engine registry declares Docling, PP-StructureV3, Surya, and OlmOCR
  with an explicit `adapter_contract_only` status and no fabricated pins.
- Immutable engine/model/container/SBOM and licence fields are validated before
  a registry can enter `benchmark_ready`.
- The benchmark manifest and scaffold bind case IDs, registry and fixture
  hashes, metrics, thresholds, and the `no_cost_only` compute policy.
- The benchmark evaluator covers character/word error, disagreement, layout,
  reading order, table accuracy, calibration, cost, and throughput gates.

## Verification

- `tests/test_ocr_engine_registry.py` verifies the four-engine registry remains
  explicitly unpinned and metadata-only.
- `tests/test_ocr_benchmark.py` verifies passing metrics, failed quality/cost
  gates, invalid runtime inputs, and structural defaults.
- Issue #131 was closed after PR #139 merged the zero-cost benchmark scaffold.

## Remaining external gates

No rights-cleared historical pages, gold annotations, pinned engine artefacts,
SBOMs, or measured comparison run are present in this checkout. The status is
therefore deferred/no-promotion, not an empirical benchmark claim.
