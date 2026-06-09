# Rust Code Style Guide (nlp-policy-nz)

This document establishes the coding standards and best practices for developing custom Rust-native extensions and Polars plugins within the `nlp-policy-nz` project.

---

## 1. General Principles

- **Safety**: Leverage Rust's borrow checker to guarantee memory safety. Minimize the use of `unsafe` blocks. If `unsafe` is required (e.g., interfacing with certain C-FFI layers), it must be accompanied by a `// SAFETY:` comment explaining why it is correct.
- **Performance**: Optimize for high-throughput batch text processing. Prefer zero-copy operations, heap allocation reuse, and iterator pipelines.
- **Portability**: Code must be platform-independent and compile cleanly on Linux, macOS, and Windows.

---

## 2. Formatting & Linting

- **Tooling**: Enforce `cargo fmt` and `cargo clippy` strict checks (with `#![deny(clippy::all, clippy::pedantic)]` where appropriate).
- **Naming Conventions**:
  - Files and modules: `snake_case` (e.g., `maori_tokenizer.rs`).
  - Structs, Enums, Traits: `PascalCase` (e.g., `MacronNormalizer`).
  - Functions, Variables, Methods: `snake_case` (e.g., `normalize_text`).
  - Constants: `SCREAMING_SNAKE_CASE` (e.g., `MAX_TOKEN_LENGTH`).

---

## 3. Polars Plugins Best Practices

- **Zero-Copy Serialization**: Pass inputs and outputs using the Arrow memory layout. When writing a Polars expression plugin, return `PolarsResult<Series>` directly.
- **Memory Reuse**: Avoid reallocating strings during tokenization or cleaning. Use buffers where possible (e.g. `String::with_capacity`).
- **Error Handling**: Propagate errors gracefully using Polars errors (`PolarsError`). Do not panic or use `.unwrap()` in production code.

---

## 4. PyO3 & Maturin Integration

- **GIL Interaction**: When using `pyo3`, minimize the time threads hold the Python GIL. Release the GIL (`Python::allow_threads`) before starting heavy CPU-bound text preprocessing loops.
- **Type Conversion**: Use PyO3's native conversion mechanisms to map types between Rust and Python (e.g. converting Python lists to Rust `Vec` and Polars DataFrames via Arrow buffers).
