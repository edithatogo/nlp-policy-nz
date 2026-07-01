# Track 37: Publication Manuscript and Review Agents

## Key files

- `src/nlp_policy_nz/publication/manuscript.py`
- `artifacts/manuscript/manuscript_manifest.json`
- `artifacts/manuscript/manuscript.md`
- `artifacts/manuscript/supplement.md`
- `artifacts/manuscript/manuscript_review_log.json`
- `scripts/manuscript/main.tex`
- `scripts/manuscript/Makefile`
- `.github/workflows/manuscript-review.yml`
- `tests/test_track37_manuscript_review.py`
- `tests/test_track37_conductor.py`
- `conductor/tracks/track37_publication_manuscript_review_20260625/evidence.md`

## Implementation decision

Track 37 uses deterministic offline reviewer scoring and checked-in manuscript artifacts. This keeps the manuscript review workflow executable in GitHub Actions without credentials while preserving explicit blockers for live external reviewer agents and full-corpus evidence.
