# Track 53 Evidence

## Baseline Definition

- Defined explicit role groups for encoder baselines, silver-label adjudicators,
  and retrieval/linking candidates.
- Kept local encoder models separate from silver-label and retrieval roles.

## Evaluation Context

- Recorded the dataset, metric, and hardware-constraint matrix for Track 53 in
  `evaluation_context.json`.
- Kept encoder, adjudicator, and retrieval roles separated in the evaluation
  context.

## Comparison Manifest

- Recorded the model comparison manifest in `model_comparison_manifest.json`.
- Preferred `isaacus/emubert` for local encoder work and `Equall/Saul-7B-Instruct-v1`
  for silver-label adjudication.
- Kept Kanon-style retrieval candidates scoped to retrieval and semantic-linking
  work.

## Recommendation

- Wrote the final recommendation summary in `recommendation.md`.
- Retained a follow-up issue for revisiting model choices after NZ-legislation
  fine-tuning.

## Verification

- `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_track53_evidence.py` -> 6 passed
- `.\.venv\Scripts\python.exe -m ruff check --no-cache src\nlp_policy_nz\training\track53_evidence.py src\nlp_policy_nz\training\__init__.py tests\test_track53_evidence.py` -> passed; removed-rule warnings only
- `.\.venv\Scripts\python.exe -B -m json.tool conductor\tracks\archive\track53_legal_model_evaluation_20260629\evaluation_context.json > $null` -> passed
- `.\.venv\Scripts\python.exe -B -m json.tool conductor\tracks\archive\track53_legal_model_evaluation_20260629\model_comparison_manifest.json > $null` -> passed
- `.\.venv\Scripts\python.exe -B -m json.tool conductor\tracks\archive\track53_legal_model_evaluation_20260629\metadata.json > $null` -> passed
