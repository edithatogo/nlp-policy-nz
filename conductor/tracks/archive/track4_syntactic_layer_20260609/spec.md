# Track 4: Build Syntactic Parsing and Citation Extractor

**Status**: Complete

## Goal

Provide the syntactic layer used by downstream legal NLP tasks: a spaCy pipeline with Māori Guard integration, New Zealand legal citation extraction, and sentence-level chunking with stable identifiers.

## Scope

- spaCy pipeline factory that installs the Track 3 Māori Guard component.
- EntityRuler patterns for New Zealand Act titles and section, part, and schedule references.
- Sentence-level chunking helpers for legislation and Hansard inputs.
- Structured identifier generation for legislation and Hansard chunks.

## Acceptance Criteria

- The pipeline factory returns a spaCy `Language` object with the expected components.
- Citation extraction runs after the Māori Guard component.
- NZ Act title and provision-reference patterns are exposed through the syntactic API.
- Chunking helpers generate stable, structured identifiers.
- Tests cover pipeline construction, citation ruler wiring, NZ citation examples, and pattern structure.

## Evidence Boundary

Track 4 is complete for repo-side syntactic scaffolding. It does not claim exhaustive recognition of every New Zealand legislative citation form.
