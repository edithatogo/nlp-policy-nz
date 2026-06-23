# Build Backend Evaluation

Track 23 evaluated the current build backend against the proposed `uv_build`
switch.

## Current State

The package currently uses `hatchling`:

```toml
[build-system]
requires = ["hatchling>=1.25.0"]
build-backend = "hatchling.build"
```

This is stable with the existing `src/` package layout and does not require
changing package metadata during the current quality-infrastructure pass.

## Decision

Keep `hatchling` for now and continue using `uv build` as the build command
where available. Defer a switch to `uv_build` until a dedicated packaging track
can validate wheel contents, editable installs, source distributions, and CI
publishing behaviour on Windows, Linux, and macOS.

## Follow-Up Gate

A future backend switch should include:

- `uv build` output comparison against the current hatchling wheel.
- Install smoke test from the built wheel.
- Verification that `src/nlp_policy_nz/py.typed` is included.
- CI matrix evidence on Windows and Linux.
