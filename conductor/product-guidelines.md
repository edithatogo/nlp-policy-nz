# Product Guidelines: nlp-policy-nz

This document defines the architectural, code style, data processing, and design guidelines for the `nlp-policy-nz` shared core engine.

---

## 1. Architectural Guidelines

To balance clean programmatic usage with robustness, the codebase enforces a hybrid architectural approach:

### 1.1 Stateless Functional Core
- All text transformation, clean-up, and citation matching operations must be written as pure, stateless functions.
- These functions must accept raw inputs (e.g., text, metadata) and return structured outputs (e.g., tokens, dicts, DataFrames) without mutating external state.
- Pure functions enable memory safety, ease of unit testing, and parallel processing via `nlp.pipe` streaming.

### 1.2 Custom spaCy Components (Object-Oriented)
- Functional utilities must be wrapped in custom, object-oriented spaCy pipeline components (e.g., `MaoriLanguageGuard`, `LegislationEntityRuler`).
- These components must register with spaCy using the `@Language.component` or `@Language.factory` decorators to integrate seamlessly with standard `spacy.load` and `.cfg` pipelines.

### 1.3 Command-Line Interface (CLI-First)
- The library must include a simple, robust CLI entry point (e.g. using `argparse` or `typer`) for bulk dataset processing.
- This allows researchers to run batch pipelines over raw folders of JSON/text files to produce standardized Parquet outputs directly from the terminal.

---

## 2. Text Preprocessing & Cleaning Rules

- **Macron Normalization**: Apply Unicode Form C (NFC) normalization to all text inputs to ensure consistent character representation (e.g., standardizing the macron characters `ā`, `ē`, `ī`, `ō`, `ū`).
- **Whitespace Management**: Strip duplicate whitespaces, trailing newlines, and non-printable control characters, but preserve paragraph breaks necessary for semantic parsing.
- **Te Reo Preservation**: Under no circumstances should the tokenizer split Māori words with macrons or distinct prefixes/suffixes into subwords. The custom tokenizer exceptions rule takes absolute precedence over English statistical tokenizers.

---

## 3. Code Style & Quality Standards

- **Typing**: Use static type hinting (`typing` module) on all function signatures.
- **Documentation**: Write Google-style docstrings for all classes, methods, and public functions.
- **Test-Driven Design**: Write robust unit tests with `pytest` for all functional extraction utilities.
- **Error Handling**: Use structured warning logs instead of crashing for minor text parsing/formatting errors. Crash early (fail-fast) only on core configuration errors, such as missing model weights or invalid paths.
