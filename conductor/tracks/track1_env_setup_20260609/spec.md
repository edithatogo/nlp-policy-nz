# Specification: Track 1 Environment Setup & Quality Tooling

This track establishes the development workspace for the `nlp-policy-nz` project, integrating Python 3.14 (free-threaded/No-GIL) with Pixi and uv environment managers.

---

## 1. Requirements & Objectives
- Set up `pixi` and `uv` workspace environments, enabling C/Rust compile capability and package pinning.
- Configure `pyproject.toml` with `hatchling` as the build backend, integrated with PyO3/Maturin config blocks.
- Configure `ruff` with strict rules activated early (enabling all standard error codes, import sorting, formatting).
- Integrate modularity and complexity checks: `Tach` config, `import-linter` rules, `Complexipy` cognitive checking.
- Configure testing harness framework: `pytest`, `Hypothesis` (property-based), `Mutatest` (mutation framework).
- Configure automated GitHub Actions CI workflow to run check pipelines.

## 2. Interface and Boundary Definitions
- **Dependency boundaries**: Pixi handles overall dependencies (including C/Rust tooling and Vale binaries). `uv` handles Python packages.
- **Python package structure**: `nlp_policy_nz` package initialized with clean entry points.

## 3. Parallelization & Guardrails
- **Multiple Subagents**: Subagents can work in parallel to scaffold test configs, linters config, and CI actions simultaneously.
- **Modularity**: Strict file separation prevents race conditions between subagents editing the same files.
