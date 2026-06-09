# Plan: Track 1 Environment Setup & Quality Tooling

This plan details the tasks to set up the development environment, build configuration, linting suites, and testing frameworks.

---

## Phase 1: Environment & Build System Setup

### [ ] Task 1: Initialize Pixi and uv Workspace
- **Action**: Create `pixi.toml` and `pyproject.toml` configuration files. Set target Python version to Python `3.14` and configure `hatchling` / `maturin` backend details.
- **Why**: Establishes our multi-language compile/execution runtime environment.

### [ ] Task 2: Create Repository Skeleton
- **Action**: Scaffold `nlp_policy_nz/` directory structure, including standard `__init__.py`, `py.typed` marker, and placeholder documentation.
- **Why**: Prepares the package directory for distribution and import.

### [ ] Task: Conductor - User Manual Verification 'Environment & Build System Setup' (Protocol in workflow.md)
- **Action**: Verification checkpoint to verify the environment loads and compiles correctly via `pixi install`.

---

## Phase 2: Strict Quality Gates Setup

### [ ] Task 3: Configure Ruff and Vale Prose Linter
- **Action**: Create `.ruff.toml` with strict rules (enable All errors, strict type warning checks) and `.vale.ini` for prose validation.
- **Why**: Enforces static code styling, quality rules, and documentation standards.

### [ ] Task 4: Configure Tach, Import Linter, and Complexipy
- **Action**: Initialize Tach configuration (`tach init`), configure `import-linter` rules to prevent modular leaks, and verify Complexipy setup.
- **Why**: Maintains module boundaries and guards against cognitive complexity inflation.

### [ ] Task: Conductor - User Manual Verification 'Strict Quality Gates Setup' (Protocol in workflow.md)
- **Action**: Checkpoint to run ruff, vale, and tach checkers locally to verify configuration works.

---

## Phase 3: Testing Framework & CI Configuration

### [ ] Task 5: Initialize Pytest, Hypothesis, and Mutatest Configuration
- **Action**: Create `tests/` folder and setup `conftest.py` with pytest, Hypothesis property configurations, and Mutatest hooks.
- **Why**: Configures robust unit, property, and mutation testing parameters.

### [ ] Task 6: Configure GitHub Actions CI Workflow
- **Action**: Create `.github/workflows/ci.yml` to run automated test suites, linting, complexipy checks, and Tach boundary validation on PRs.
- **Why**: Orchestrates CI quality gates on git push/pull actions.

### [ ] Task: Conductor - User Manual Verification 'Testing Framework & CI Configuration' (Protocol in workflow.md)
- **Action**: Verify test runner execution and mock test runs pass under CI environment rules.
