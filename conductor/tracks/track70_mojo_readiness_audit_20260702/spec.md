# Track 70: Mojo Readiness Audit

## Overview

Verify whether Mojo is currently suitable for this repo's Linux GitHub Actions acceleration profile without destabilizing the Windows Python fallback workflow.

## Requirements

- Re-check current Mojo package, compiler, documentation, license, supported platforms, and GitHub Actions install path.
- Confirm whether Mojo should be installed through `mojo`, `mojo-compiler`, Pixi, uv, or a dedicated setup action.
- Verify compatibility with the repo's Python-first public API and optional dependency model.
- Shortlist deterministic candidate kernels only where profiling or existing performance evidence suggests a possible gain.
- Compare Mojo readiness against Rust/PyO3, Polars, LanceDB-native paths, and current Python/Rust-backed libraries.

## Acceptance Criteria

- [ ] OS support, package availability, licensing, and redistribution constraints are documented with source links.
- [ ] GitHub Actions install strategy is selected or Mojo is deferred.
- [ ] Pixi/uv compatibility and lockfile implications are recorded.
- [ ] Candidate kernel shortlist is ranked with evidence and alternatives.
- [ ] The readiness decision states whether Track 71 may proceed.

## Out of Scope

- Adding Mojo runtime code.
- Adding Mojo to required dependencies.
- Creating the `experiments/mojo/` sandbox.
- Changing production pipeline behavior.
