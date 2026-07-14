# Track 71: Mojo Linux CI Sandbox

## Overview

Create a Linux-only Mojo sandbox that proves toolchain installation, Python fallback behavior, and parity testing without touching production imports.

## Requirements

- Proceed only after Track 70 confirms a viable install path.
- Add an optional `experiments/mojo/` sandbox with a tiny deterministic kernel and Python reference output.
- Add a non-blocking Linux GitHub Actions job or matrix entry.
- Keep Windows and default CI free of Mojo requirements.
- Emit or preserve benchmark/parity artifacts for inspection.

## Acceptance Criteria

- [ ] Linux GitHub Actions can install Mojo and run the sandbox.
- [ ] Windows jobs skip Mojo cleanly and continue to exercise Python fallback.
- [ ] Python and Mojo outputs match for the sandbox fixture.
- [ ] Sandbox failures do not block ordinary validation before production gates pass.
- [ ] Documentation explains usage, skip behavior, and removal criteria.

## Out of Scope

- Accelerating production pipeline code.
- Adding Mojo to default dependencies.
- Replacing existing benchmark gates.
- Migrating legal reasoning, ontology, or publication paths.
