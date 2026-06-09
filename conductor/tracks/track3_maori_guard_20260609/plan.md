# Plan: Track 3 Māori Language Guard (SOTA)

This track implements the Māori Language Guard layer — a set of linguistic safety components that ensure Te Reo Māori text is preserved correctly through the NLP pipeline.

---

## Phase 1: Unicode Normalization & Tokenizer Exceptions [b65c685]

### [x] Task 3.1: Build Unicode Normalization Layer
- **Action**: Implement NFC unicode normalizer to handle macron variations (ā vs a vs aa).
- **Why**: Ensures consistent character representation across documents.
- **Completed**: Created `guard/normalizer.py` with `normalize_text()`, `is_macronized()`, `preserve_macrons()`, `MACRON_MAP` dictionary for variant-to-canonical mapping, and generic double-vowel to macron substitution.

### [x] Task 3.2: Implement Tokenizer Exceptions
- **Action**: Configure spaCy tokenizer rules to protect Te Reo Māori vocabulary from subword splits.
- **Why**: Prevents fragmentation of Māori words like tikanga, taonga, kāwanatanga.
- **Completed**: Created `guard/tokenizer_exceptions.py` with `TE_REO_LEXICAL_ATOM_SET` (frozenset of ~30 Māori lexical atoms), `TE_REO_PREFIXES`, `build_tokenizer_exceptions()`, and `create_maori_guard_component()` factory that registers orth exceptions and adds `"maori_guard"` pipeline component.

---

## Phase 2: Language Identification [b65c685]

### [x] Task 3.3: Build Language Identifier
- **Action**: Code phrase-level sequence classifier identifying Te Reo Māori vs English sections using lingua-rs.
- **Why**: Enables targeted processing and code-switching detection in bilingual texts.
- **Completed**: Created `guard/language_id.py` with `LanguageIdentifier` class wrapping lingua-rs detector, `LanguageResult` (msgspec frozen Struct), and methods for `detect()`, `detect_sentences()`, and `detect_code_switching()` with ISO 639-1 mapping (en/mi/un).

---
