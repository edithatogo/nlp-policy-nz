# Track 3: Implement Māori Language Guard

**Status**: Complete

## Goal

Preserve Te Reo Māori orthography and phrase identity through the NLP pipeline so New Zealand legal and parliamentary text is not degraded by normalization, tokenization, or language-identification steps.

## Scope

- Unicode NFC normalization and macron preservation helpers.
- Canonical mapping for common non-macronized Māori forms.
- spaCy tokenizer exception rules for Te Reo Māori lexical atoms.
- A reusable Māori guard spaCy component factory.
- Optional phrase-level language identification for English, Te Reo Māori, and uncertain text.

## Acceptance Criteria

- Macronized text survives normalization without decomposition.
- Known Māori words such as `Māori`, `Pākehā`, `kāwanatanga`, `tikanga`, and `rangatiratanga` are represented as protected lexical atoms.
- Tokenizer exceptions can be installed idempotently into a spaCy pipeline.
- Language identification is available when the optional `lingua` dependency is installed.
- Tests cover normalization, tokenizer exception construction, pipeline insertion, and language identification.

## Evidence Boundary

Track 3 is complete for repo-side guard implementation. It does not claim exhaustive linguistic coverage of every Te Reo Māori phrase or dialectal variant.
