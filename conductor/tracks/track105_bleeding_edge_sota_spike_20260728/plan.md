# Plan: Track 105 Bleeding-edge SOTA spike

Track issue: [#202](https://github.com/edithatogo/nlp-policy-nz/issues/202)

## Phase 0: Decision record ([#219](https://github.com/edithatogo/nlp-policy-nz/issues/219))

- [ ] Task: Write allowed/banned decision record (mirror Track 99/58 style)
- [ ] Task: Define optional extra name(s) e.g. `sota` / `graphrag` / `structured`
- [ ] Task: Update maturity-checklist + tech-stack before code adoption
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 1: Constrained decoding ([#220](https://github.com/edithatogo/nlp-policy-nz/issues/220))

- [ ] Task: Red — fixture test expecting schema-valid candidate JSON
- [ ] Task: Green — optional spike module; skip if extra missing
- [ ] Task: Evidence note: limitations, offline-only, candidate-only
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Hybrid GraphRAG ([#221](https://github.com/edithatogo/nlp-policy-nz/issues/221))

- [ ] Task: Red — hybrid retrieval contract over citation fixture graph
- [ ] Task: Green — NetworkX + LanceDB recipe behind optional extra
- [ ] Task: Evidence note vs pure vector baseline
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: MCP + eval harness ([#222](https://github.com/edithatogo/nlp-policy-nz/issues/222))

- [ ] Task: Red — MCP contract tests for declared tools
- [ ] Task: Green — harden MCP surface; document agent adopter path
- [ ] Task: Spike local eval harness; assert `promotion_allowed=false`
- [ ] Task: Could — Docling/C2PA spike notes only if timeboxed
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
