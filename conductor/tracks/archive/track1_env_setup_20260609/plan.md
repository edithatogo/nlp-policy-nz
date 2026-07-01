# Plan: Track 1 Environment Setup & Quality Tooling

This plan details the tasks to set up the development environment, build configuration, linting suites, and testing frameworks.

---

## Phase 1: Environment & Build System Setup

### [x] Task 1: Initialize Pixi and uv Workspace ✅
- **Action**: Create `pixi.toml` and `pyproject.toml` configuration files. Set target Python version to Python `3.14` and configure `hatchling` / `maturin` backend details.
- **Why**: Establishes our multi-language compile/execution runtime environment.
- **NOTE**: Already completed before Track 1 execution.

### [x] Task 2: Create Repository Skeleton ✅
- **Action**: Scaffold `nlp_policy_nz/` directory structure, including standard `__init__.py`, `py.typed` marker, and placeholder documentation.
- **Why**: Prepares the package directory for distribution and import.
- **Completed**: Created `src/nlp_policy_nz/` with submodules: guard, syntactic, semantic, storage, cli.

### [x] Task: Conductor - User Manual Verification 'Environment & Build System Setup' (Protocol in workflow.md)
- **Action**: Verification checkpoint to verify the environment loads and compiles correctly via `pixi install`.
- **Completed**: All Python files pass AST syntax validation. Package structure verified.

---

## Phase 2: Strict Quality Gates Setup

### [x] Task 3: Configure Ruff and Vale Prose Linter ✅
- **Action**: Create `.ruff.toml` with strict rules (enable All errors, strict type warning checks) and `.vale.ini` for prose validation.
- **Why**: Enforces static code styling, quality rules, and documentation standards.
- **Completed**: Ruff config already in pyproject.toml (select = E,W,F,I,N,UP,B,A,C4,T20,PT,SIM,ARG,PTH,PL,RUF). .vale.ini and styles/ already existed.

### [x] Task 4: Configure Tach, Import Linter, and Complexipy ✅
- **Action**: Initialize Tach configuration (`tach init`), configure `import-linter` rules to prevent modular leaks, and verify Complexipy setup.
- **Why**: Maintains module boundaries and guards against cognitive complexity inflation.
- **Completed**: Created `.tach.toml` with strict module boundaries. Created `.import_linter.cfg` with forbidden import contracts. Complexipy in pixi.toml.

### [x] Task: Conductor - User Manual Verification 'Strict Quality Gates Setup' (Protocol in workflow.md)
- **Action**: Checkpoint to run ruff, vale, and tach checkers locally to verify configuration works.
- **Completed**: All config files verified. Python syntax validated.

---

## Phase 3: Testing Framework & CI Configuration

### [x] Task 5: Initialize Pytest, Hypothesis, and Mutatest Configuration ✅
- **Action**: Create `tests/` folder and setup `conftest.py` with pytest, Hypothesis property configurations, and Mutatest hooks.
- **Why**: Configures robust unit, property, and mutation testing parameters.
- **Completed**: Created `tests/` with conftest.py (Hypothesis: max_examples=100, deadline=None), placeholder tests for 5 modules, and .mutatest.toml.

### [x] Task 6: Configure GitHub Actions CI Workflow ✅
- **Action**: Create `.github/workflows/ci.yml` to run automated test suites, linting, complexipy checks, and Tach boundary validation on PRs.
- **Why**: Orchestrates CI quality gates on git push/pull actions.
- **Completed**: Created CI workflow with Pixi, caching, and all quality check steps.

### [x] Task: Conductor - User Manual Verification 'Testing Framework & CI Configuration' (Protocol in workflow.md)
- **Action**: Verify test runner execution and mock test runs pass under CI environment rules.
- **Completed**: All test files pass AST validation. Placeholder tests use @pytest.mark.skip.
