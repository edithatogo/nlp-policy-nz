# Track 78 Evidence

## Implementation

- Added `src/nlp_policy_nz/rulespec_promotion.py` with fail-closed promotion models, validation, and deterministic JSON/YAML handoff writers.
- Added fixture payloads in `data/track78/promotion_handoff_fixtures.json` and `data/track78/promotion_handoff_fixtures.md`.
- Added focused tests in `tests/test_rulespec_promotion.py`.
- Documented the promotion contract in `docs/rulespec-promotion.md` and linked it from `README.md` and `docs/extraction-framework.md`.

## Validation

- `pixi run ruff check src/nlp_policy_nz/rulespec_promotion.py tests/test_rulespec_promotion.py README.md docs/extraction-framework.md docs/rulespec-promotion.md conductor/tracks.md conductor/tracks/track78_rulespec_promotion_contract_20260705/plan.md`
- `pixi run pytest tests/test_rulespec_promotion.py -q`
- `pixi run pytest tests/test_rac_bridge.py -q`

## GitHub Mirror

- GitHub issue `#84` exists for Track 78 and is present in both Conductor projects.
- Project item reads show the issue in `nlp-policy-nz Conductor Roadmap` and `Rare Insights on Open Policy from Aotearoa`.
- Field-write attempts against the Track 78 project row returned `The item does not exist in the project`, so the mirror is currently verified by membership and issue-body metadata rather than refreshed custom fields.
