# Track 78 Promotion Handoff Fixtures

This fixture bundle exercises the fail-closed promotion contract for:

- `promoted`
- `rejected`
- `deferred`
- `blocked`

The examples are intentionally offline and deterministic. They model the repo-side
handoff boundary only. Executable RuleSpec content remains downstream in
`rulespec-nz`, with PolicyEngine and OpenFisca consuming reviewed artifacts after
promotion.

