# Track 97 Evidence

## Repository-side implementation

- `scripts/archive_assurance.py` builds a deterministic mixed-access archive
  graph and exercises public/private effective-access projections.
- All public serializers are checked for restricted text and vector canary
  leakage: JSON, JSONL, JSON-LD, Markdown, Parquet, and RDF.
- Public and private JSON round trips are validated separately.
- Projection scaling is checked at widths 32 and 64 with a fixed ceiling and
  ratio bound.
- A fixed-seed mutation sample covers the archive schema and assurance tests.

## Verification

- `pixi run archive-assurance`: passed; serializer canaries, compatibility,
  performance, and 4 fixed-seed mutants passed.
- `pixi run pytest -p no:tach -q tests/test_archive_schema.py tests/test_archive_assurance.py`:
  15 passed.
- Scoped Ruff checks for the archive schema, assurance script, and tests passed.
- `git diff --check`: passed.

## Remaining external gates

This track is repository-side complete with external gates. The repository
does not contain authoritative territorial rights records, independent
adversarial review, or legal/profile-owner approval, so no promotion or live
publication claim is made. These gates remain linked to issue #133.
