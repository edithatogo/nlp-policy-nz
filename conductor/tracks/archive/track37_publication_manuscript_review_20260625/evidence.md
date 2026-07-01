# Track 37 Evidence

## Generated manuscript package

- `artifacts/manuscript/manuscript_manifest.json`
- `artifacts/manuscript/manuscript.md`
- `artifacts/manuscript/abstract.md`
- `artifacts/manuscript/supplement.md`
- `artifacts/manuscript/submission_requirements.md`
- `artifacts/manuscript/reproducibility_checklist.md`
- `artifacts/manuscript/review_rubrics.json`
- `artifacts/manuscript/manuscript_review_log.json`
- `artifacts/manuscript/scripts/manuscript/main.tex`
- `artifacts/manuscript/scripts/manuscript/macros.tex`
- `artifacts/manuscript/scripts/manuscript/references.bib`
- `artifacts/manuscript/scripts/manuscript/Makefile`
- `scripts/manuscript/main.tex`
- `scripts/manuscript/macros.tex`
- `scripts/manuscript/references.bib`
- `scripts/manuscript/Makefile`

## Source implementation

- `src/nlp_policy_nz/publication/manuscript.py`
- `src/nlp_policy_nz/publication/__init__.py`
- `src/nlp_policy_nz/cli/main.py`
- `.github/workflows/manuscript-review.yml`

## Review loop

The deterministic offline review log records six reviewer dimensions and an overall minimum score above 95. The first recorded loop scored below threshold and the second loop records the applied fixes and final passing score.

## Validation

- `pixi run python -m pytest -q tests\test_track37_manuscript_review.py tests\test_track37_conductor.py tests\test_cli.py`

## Blocker boundary

The package is generated from checked-in Track 34-36 repo evidence. Full-corpus statistics, live arXiv submission, live external reviewer agents, authenticated API publication, and production-scale graph/vector claims remain external gates until canonical exports and credentials are supplied.
