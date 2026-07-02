# Track 47: Cross-Platform CI Matrix & Binary Distribution [7fee249]

**Dependencies**: Tracks 1, 23, 38
**Parallelization Node**: CI/CD Automation
**Status**: In Progress

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Add `strategy.matrix.os` to `.github/workflows/ci.yml` with `[ubuntu-latest, windows-latest, macos-latest]`; set up per-platform pixi cache keys | [x] | conductor_orchestrator |
| 2 | Identify and fix platform-specific failures: Windows path separators, macOS temp dirs, Linux glibc version constraints; add `conftest.py` platform markers | [x] | conductor_orchestrator |
| 3 | Add CI step that reports per-platform pass/fail badge status | [x] | conductor_orchestrator |
| 4 | Create `.github/workflows/build-binaries.yml` using PyInstaller for each OS; upload artifacts to release | [x] | conductor_orchestrator |
| 5 | Set `python_requires` in `pyproject.toml`; test against Python 3.11 and 3.12 | [x] | conductor_orchestrator |
| 6 | Document system requirements in `docs/install/system_requirements.md` per platform | [x] | conductor_orchestrator |
| 7 | Verify full matrix passes on a test PR (run CI, inspect per-platform results) | [ ] | conductor_orchestrator |

## Evidence Boundary

CI matrix YAML, platform-specific fixes, binary build workflow, and system requirements doc satisfy repo-side evidence.
