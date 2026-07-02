# Track 71 Evidence

- Local sandbox helper: `experiments/mojo/sandbox.py`
- Deterministic fixture: `experiments/mojo/kernel.mojo`
- Usage and removal guidance: `docs/mojo_sandbox.md`
- CI hook: `.github/workflows/ci.yml`

## Validation

- `pixi run python -m pytest -p no:tach tests/test_track71_mojo_sandbox.py -q`
- `pixi run python -m py_compile experiments/__init__.py experiments/mojo/__init__.py experiments/mojo/sandbox.py tests/test_track71_mojo_sandbox.py`

## Decision

Track 71 is complete as a Linux-only, non-blocking Mojo sandbox. It keeps Windows on Python fallback, compares a deterministic reference payload against the Mojo kernel fixture, and provides a clear removal path if the sandbox stops being useful for Track 72 benchmarking.

