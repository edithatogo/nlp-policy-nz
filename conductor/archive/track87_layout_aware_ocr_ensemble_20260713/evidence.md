# Track 87 Evidence

## Implemented

- `nlp_policy_nz.ocr.ensemble` defines normalized page geometry, layout blocks, reading order, OCR tokens, observations, token alignments, quality metrics, cache keys, adapter protocols, and CPU/GPU cascade decisions.
- `nlp_policy_nz.ocr.benchmark` evaluates CER, WER, disagreement, layout, reading order, tables, confidence calibration, cost per page, and throughput with fail-closed promotion gates.
- `data/track87/engine_registry.json` records Docling, PP-StructureV3, Surya, and olmOCR as adapter-contract-only candidates until immutable model/container digests and benchmark results exist.
- `data/track87/golden_page_fixtures.json` defines metadata-only stratification across historical year bands and single-column, multi-column, table, and marginalia layouts.
- No OCR engine package is imported by the core runtime and no corpus payload is downloaded locally.

## Verification

- OCR and benchmark tests: 16 passed.
- OCR package coverage: 99% total, with 99% ensemble coverage and 98% benchmark coverage.
- `basedpyright src/nlp_policy_nz/ocr`: 0 errors, 0 warnings, 0 notes.
- Ruff check and format checks passed.
- Engine promotion remains fail-closed while registry digests are null.

## Boundary

This track delivers the versioned contract, benchmark harness, and routing logic. Cloud engine execution, pinned image/model acquisition, and corpus-scale GitHub Actions orchestration remain Track 91 responsibilities.

## Independent audit disposition — 2026-07-15

The three-review panel confirmed that the harness, schemas, metrics, routing,
and fail-closed registry are implemented. All four engine digests remain null,
however, and the fixtures contain metadata rather than rights-cleared annotated
page payloads. Track 91's Tesseract operations pilot does not constitute the
declared four-engine historical benchmark. No engine is promoted. The missing
empirical benchmark is tracked by Track 95 / issue #131.
