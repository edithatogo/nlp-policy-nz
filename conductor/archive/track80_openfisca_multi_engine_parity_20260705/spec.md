# Track 80: OpenFisca and Multi-Engine Parity

## Overview

Extend the PolicyEngine pilot into a multi-engine rules-as-code validation path by adding OpenFisca-compatible export and parity tests, then document how additional engines should be onboarded after the semantic contract is stable.

## Functional Requirements

- Generate OpenFisca-compatible package artifacts from the same promoted pilot handoff used by PolicyEngine.
- Add parity fixtures that compare PolicyEngine and OpenFisca outputs for the pilot domain.
- Define an adapter contract for additional rules-as-code engines without binding the core NLP package to every runtime.
- Emit a parity report that includes source IDs, oracle fixtures, engine versions, output comparison, and known gaps.
- Update docs with engine support levels and promotion criteria.

## Non-Functional Requirements

- Multi-engine tests must be deterministic and safe for GitHub Actions.
- Optional engine dependencies must remain isolated behind extras or skipped tests.
- Parity reports must fail closed when engines disagree without an accepted reason.

## Acceptance Criteria

- [ ] OpenFisca package export exists for the pilot domain.
- [ ] PolicyEngine/OpenFisca parity tests run on deterministic fixtures.
- [ ] Engine adapter contract and support-level docs exist.
- [ ] Parity report records source IDs, engine versions, expected outputs, actual outputs, and known gaps.
- [ ] GitHub issue and project mirror are populated for this track.

## Out of Scope

- Broad all-engine formula coverage.
- Runtime service hosting.
- Legal review of new domains beyond the pilot.
