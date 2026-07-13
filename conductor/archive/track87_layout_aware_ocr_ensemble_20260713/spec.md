# Track 87 Specification: Layout-Aware OCR Ensemble

## Goal

Add a replaceable document-image pipeline that preserves supplied OCR and independently re-OCRs historical pages for verification.

## Requirements

- Normalize PDF/image inputs into page and layout-block observations with coordinates and reading order.
- Benchmark pinned Docling, PP-StructureV3, Surya, and olmOCR adapters; avoid declaring a winner without NZ historical-page evidence.
- Use a cost-aware cascade with GPU/VLM escalation for low-confidence pages.
- Align OCR alternatives at line/token level and retain confidence, CER/WER proxies, disagreement, engine/model digest, and runtime provenance.
- Preserve tables, multi-column text, marginalia, headers, footnotes, illustrations, and page labels.
- Run corpus OCR only on cloud workers dispatched by GitHub Actions.

## Acceptance

Golden-page tests prove coordinates, order, alternatives, deterministic routing, resumability, and no destructive replacement of source OCR.
