# Track 79 Evidence

## Selected Pilot Domain

- Domain: commencement after Royal assent
- Source citation path: `nz/statutes/commencement/2026/1`
- Source excerpt: `This Act commences on the day after Royal assent.`
- Entity: `person`
- Period: `day`
- Parameter: `royal_assent_date`
- Formula: `assessment_date > royal_assent_date`

## Generated Artifacts

- `src/nlp_policy_nz/policyengine_pilot.py`
- `data/track79/policyengine_pilot_manifest.json`
- `data/track79/oracles/policyengine_oracles.json`
- `data/track79/reviews/policyengine_pilot_review.md`
- `docs/policyengine-pilot.md`
- `policyengine-pilot` CLI subcommand in `src/nlp_policy_nz/cli/main.py`

## Validation

- `pixi run ruff check src/nlp_policy_nz/policyengine_pilot.py src/nlp_policy_nz/cli/main.py tests/test_policyengine_pilot.py`
- `pixi run pytest tests/test_policyengine_pilot.py -q`
- `pixi run pytest tests/test_cli.py -q`
- `git diff --check`

## GitHub Mirror

- Issue `#85` exists for Track 79 and has the expected track markers and labels.
- The project-field mirror could not be re-queried after the GraphQL quota was exhausted, so the local archive records the issue-side mirror evidence and leaves the project-field refresh for the next sync window if needed.
