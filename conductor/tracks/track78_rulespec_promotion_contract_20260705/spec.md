# Track 78: RuleSpec Promotion Contract

## Overview

Define the reviewed promotion contract that turns NLP-generated RAC candidates into RuleSpec-ready source modules without making this repository the executable rules runtime.

## Functional Requirements

- Define review states for candidate, reviewed, rejected, deferred, and promoted provisions.
- Specify the minimal RuleSpec handoff payload: durable ID, source verification, legal effect, entities, periods, parameters, formulas, oracle fixture references, and reviewer evidence.
- Add validation helpers that reject promotion when source spans, source hashes, formula status, or oracle references are missing.
- Emit handoff artifacts consumable by `rulespec-nz` while keeping executable semantics downstream.
- Document how reviewed RuleSpec modules feed PolicyEngine and OpenFisca work.

## Non-Functional Requirements

- Promotion validation must be offline and deterministic.
- The contract must fail closed when legal review or oracle evidence is absent.
- This repo must not import the RuleSpec runtime as a core dependency.

## Acceptance Criteria

- [ ] Promotion schema and validation helpers exist.
- [ ] Tests cover promotion success, missing source proof, missing legal review, missing oracle fixtures, and rejection/deferment.
- [ ] Handoff docs identify which artifacts belong in this repo versus `rulespec-nz`.
- [ ] GitHub issue and project mirror are populated for this track.

## Out of Scope

- Implementing reviewed formulas for all NZ legislation.
- Adding a hard runtime dependency on `rulespec-nz`.
- Executing PolicyEngine or OpenFisca.
