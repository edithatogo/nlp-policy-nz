# Track 61: Unstructured Ingestion Adapter Evaluation

## Overview

Track 61 evaluates and implements an optional `unstructured`-backed ingestion
adapter for messy documents such as PDFs, DOCX, HTML exports, and scanned-like
inputs. The adapter is deliberately scoped as a fallback path. The canonical
legislative parsers for XML, Akoma-Ntoso, HTML, and JSONL remain the source of
truth and must not be substituted by the adapter.

## Requirements

- Add an optional adapter that can partition a local file into
  `DocumentChunk` records.
- Preserve provenance metadata, element type, and quality flags in the emitted
  chunk attributes.
- Keep the adapter behind an explicit optional dependency or feature flag.
- Leave the existing XML / HTML / JSONL ingestion surface unchanged for
  ordinary pipeline use.
- Document the allowed use cases and the banned canonical-source substitution
  path.

## Acceptance Criteria

- [x] An optional `UnstructuredIngestionEngine` exists and can partition a
  local file into `DocumentChunk` records.
- [x] The adapter preserves source provenance and quality flags in chunk
  attributes.
- [x] Tests cover successful partitioning, missing-dependency behavior, and
  file-not-found behavior.
- [x] Packaging metadata exposes an optional `unstructured` extra or feature.
- [x] Documentation states that the adapter is fallback-only and cannot replace
  the canonical legislative parsers.
- [x] The Conductor registry and GitHub mirror are synchronized with the local
  track state.

## Non-Goals

- Replacing the XML / HTML / JSONL parsers.
- Adding production reliance on `unstructured` as the primary source parser.
- Introducing OCR or remote hosted partitioning services.
