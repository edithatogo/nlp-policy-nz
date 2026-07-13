# Track 87 OCR Artifacts

`engine_registry.json` records the four candidate engine families and keeps them adapter-contract-only until immutable model and container digests are supplied. This prevents an unpinned OCR runtime from entering a reproducible archive release.

The runtime contracts live in `nlp_policy_nz.ocr.ensemble`. Corpus execution belongs in cloud workers dispatched by GitHub Actions; this repository contains only contracts, fixtures, metrics, and routing logic.
