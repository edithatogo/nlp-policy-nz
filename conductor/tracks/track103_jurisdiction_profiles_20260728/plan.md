# Plan: Track 103 Jurisdiction profiles

Track issue: [#200](https://github.com/edithatogo/nlp-policy-nz/issues/200)

## Phase 0: Profile schema + loader ([#212](https://github.com/edithatogo/nlp-policy-nz/issues/212))

- [ ] Task: Red — profile schema validation tests (version, digest, fail-closed)
- [ ] Task: Green — `config/jurisdictions/` + ProfileLoader
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 1: Schema generalization ([#213](https://github.com/edithatogo/nlp-policy-nz/issues/213))

- [ ] Task: Red — non-NZ country/corpus_id acceptance tests
- [ ] Task: Green — parameterize shared schema; keep NZ default fixtures green
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: NZ + AU profiles ([#214](https://github.com/edithatogo/nlp-policy-nz/issues/214))

- [ ] Task: Red — adapter routing tests via profile_id (NZ, CTH, NSW)
- [ ] Task: Green — migrate foio_nz/au to profile-backed config without behaviour regression
- [ ] Task: Cross-link Track 98 / #144 evidence boundaries
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: DX cookbook ([#215](https://github.com/edithatogo/nlp-policy-nz/issues/215))

- [ ] Task: Docs + example for adding a profile
- [ ] Task: Ontology export `--profile` generalization
- [ ] Task: Document stable `extraction` API surface
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
