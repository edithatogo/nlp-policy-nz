# Track 76 Evidence

## Fixture Contract

- Fixture source contract: `data/track76/source_inventory_fixtures.json`
- Deterministic manifest: `data/track76/source_inventory.json`
- Deterministic summary: `data/track76/source_inventory.md`

## Coverage Signals

- Total records: 7
- Available records: 2
- Known gaps: 5
- Required status buckets covered: available, redirected, pdf_only, malformed,
  access_blocked, unavailable

## Claim Boundary

This inventory is fixture-bounded. It proves offline source readiness only and
does not claim whole-corpus completeness, live crawling, or universal rights
clearance.

## Live Probe Policy

The live probe helper is opt-in and skips by default. It reports a skip on
Windows and in GitHub Actions so CI stays non-networked.

## Validation

- `pixi run pytest tests/test_source_inventory.py -q`
- `git diff --check`
