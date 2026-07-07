# Track 79: PolicyEngine Executable Pilot

## Overview

Implement the first reviewed executable PolicyEngine package generated from promoted New Zealand legislation candidates. This is the primary runtime target because the expected policy use case is PolicyEngine-first.

## Functional Requirements

- Select a narrow pilot domain with reviewed source provisions, legal formulas, entities, periods, parameters, and oracle fixtures.
- Generate a real PolicyEngine-compatible package from promoted handoff artifacts.
- Replace placeholder `NotImplementedError` skeleton formulas with reviewed executable formulas for the pilot domain only.
- Add CLI/API support to build the pilot package from deterministic fixtures.
- Add tests that execute PolicyEngine calculations against oracle fixtures.
- Preserve source citation, checksum, and review evidence in generated package metadata.

## Non-Functional Requirements

- The pilot must run offline in GitHub Actions.
- Formula generation must fail closed for unreviewed or missing-oracle candidates.
- This repo may generate the package, but broad executable-law maintenance should remain downstream after the pilot is proven.

## Acceptance Criteria

- [ ] A reviewed pilot domain is selected and documented.
- [ ] Generated PolicyEngine package executes at least one real formula against oracle fixtures.
- [ ] Tests prove source provenance, package metadata, formula output, and failure behavior.
- [ ] Documentation explains how to extend from pilot to broader legislation.
- [ ] GitHub issue and project mirror are populated for this track.

## Out of Scope

- All-legislation formula coverage.
- OpenFisca parity.
- Live service deployment.
