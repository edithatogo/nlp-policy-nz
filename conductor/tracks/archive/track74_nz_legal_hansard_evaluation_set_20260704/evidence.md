# Track 74 Evidence

- Held-out evaluation manifest: `data/track74/held_out_evaluation_set.json`
- Baseline report: `data/track74/baseline_report.json`
- Held-out source files:
  - `data/track74/sources/legislation_commencement.txt`
  - `data/track74/sources/hansard_water_services.txt`
  - `data/track74/sources/legislation_tikanga.txt`
  - `data/track74/sources/hansard_treaty.txt`

## Validation

- `pixi run -e py311 python -m pytest -q tests/test_track74_evaluation_set.py`
- `pixi run -e py311 ruff check src/nlp_policy_nz/training/track74_evaluation.py src/nlp_policy_nz/training/__init__.py tests/test_track74_evaluation_set.py`
- `git diff --check`

## Decision

Track 74 is complete as a repo-side held-out NZ legal/Hansard evaluation gate. The manifest is leakage-free against the explicit training pool, the baseline report is stable, and the GitHub issue/project mirror now points at the evaluation set rather than the earlier Track 13 revisit note.
