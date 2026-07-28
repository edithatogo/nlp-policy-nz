# Plan: Track 101 Core coverage & auth honesty

Track issue: [#198](https://github.com/edithatogo/nlp-policy-nz/issues/198)

## Phase 0: Coverage gate ([#207](https://github.com/edithatogo/nlp-policy-nz/issues/207))

- [ ] Task: Red — tests exercising universal_framework_v3 / AKN emitter critical paths
- [ ] Task: Green — remove or narrowly justify coverage omit; update docs/coverage.md
- [ ] Task: Verify coverage report includes framework modules
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 1: Auth honesty ([#208](https://github.com/edithatogo/nlp-policy-nz/issues/208))

- [ ] Task: Red — Compose/prod config tests for `REQUIRE_API_AUTH`
- [ ] Task: Green — set prod/Compose defaults; clarify local override
- [ ] Task: Align `docs/ops/api_security.md` and SECURITY notes
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Env ignore ([#209](https://github.com/edithatogo/nlp-policy-nz/issues/209))

- [ ] Task: Update `.gitignore` for `.env.dev/.staging/.prod`
- [ ] Task: Confirm `.env.example` remains key-only
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Maturity refresh (Should)

- [ ] Task: Update maturity-checklist pydantic / typer / checksums statuses for Phase XV
- [ ] Task: Optional mutation schedule design note (S-QH-1)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
