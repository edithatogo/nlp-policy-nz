# Plan: Track 100 Adopter DX & slim install

Track issue: [#197](https://github.com/edithatogo/nlp-policy-nz/issues/197)

## Phase 0: Inventory and single path ([#204](https://github.com/edithatogo/nlp-policy-nz/issues/204))

- [ ] Task: Inventory divergent install/quickstart claims in README, QUICKSTART, docs-site
  - [ ] Write failing doc/contract test or checklist asserting one canonical first-run command
  - [ ] Document chosen command (`process` fixture + `--no-embeddings`)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 1: Slim install extras ([#205](https://github.com/edithatogo/nlp-policy-nz/issues/205))

- [ ] Task: Red — extras/install tests for default vs optional dependency sets
- [ ] Task: Green — move Gradio/API/heavy ML to extras where feasible; update pyproject/pixi
- [ ] Task: Docs — extras matrix in README and docs-site
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Compose honesty ([#206](https://github.com/edithatogo/nlp-policy-nz/issues/206))

- [ ] Task: Red — docs lint/assertion that stub services are labelled
- [ ] Task: Green — rewrite QUICKSTART as “API path (optional)” after fixture path
- [ ] Task: Align docs-site install hedging with root Docker story
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Operator UX (Should)

- [ ] Task: Evaluate Typer/Rich migration for subset of CLI commands (S-ADX-1)
- [ ] Task: Optional `doctor` spike behind flag (C-ADX-1)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
