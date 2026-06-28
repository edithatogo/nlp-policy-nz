# Track 53 Evidence

## Baseline Definition

- Defined explicit role groups for encoder baselines, silver-label adjudicators,
  and retrieval/linking candidates.
- Kept local encoder models separate from silver-label and retrieval roles.
- Verification:
  - `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_track53_evidence.py` -> 3 passed
  - `.\.venv\Scripts\python.exe -m ruff check --no-cache src\nlp_policy_nz\training\track53_evidence.py src\nlp_policy_nz\training\__init__.py tests\test_track53_evidence.py` -> passed; removed-rule warnings only
