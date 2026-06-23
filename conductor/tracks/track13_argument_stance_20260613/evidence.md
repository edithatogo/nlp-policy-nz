# Track 13 Evidence

## Acceptance Status

- argument_component_classifier: pending
- stance_classifier: pending
- aif_jsonld_export: satisfied
- pipeline_schema_fields: satisfied
- coverage: satisfied
- repo_side_contracts: satisfied

## Current Repo-Side Evidence

- Argument and stance deterministic fixtures validate detector/classifier wiring.
- `src/nlp_policy_nz/training/track13_evidence.py` prevents heuristic fixture scores from satisfying the held-out transformer gates.
- `track13_acceptance_contract()` emits stable JSON-ready gate entries with observed metrics, required thresholds, segment counts, model IDs, evaluation sources, and repo/external scope.
- `track13_residual_external_gates()` lists only the pending classifier/evaluation gates, keeping repo-side coverage or schema gaps separate.
- AIF JSON-LD export and PipelineRecord argument/stance fields are covered by focused tests.
- Gold-label-only training extraction and Legal-BERT job specs are covered by focused tests.

## Verification

- `pytest tests\test_track13_evidence.py -q` -> 5 passed
- `pytest tests\test_argument_training.py tests\test_track13_evidence.py tests\test_training_eval.py -q` -> 16 passed
- `ruff check src\nlp_policy_nz\training\track13_evidence.py src\nlp_policy_nz\training\__init__.py tests\test_track13_evidence.py` -> passed
- `python -B -m pytest -p no:cacheprovider -q tests\test_argument.py tests\test_stance.py tests\test_argument_training.py tests\test_argument_api_graph.py tests\test_track13_evidence.py tests\test_storage.py --basetemp C:\tmp\nlp-policy-nz-track13-final3` -> 35 passed
- `python -m ruff check --no-cache src\nlp_policy_nz\discourse src\nlp_policy_nz\training\track13_evidence.py src\nlp_policy_nz\training\data.py src\nlp_policy_nz\training\trainers.py src\nlp_policy_nz\training\__init__.py src\nlp_policy_nz\cli\graph.py src\nlp_policy_nz\api\server.py src\nlp_policy_nz\storage\serialization.py src\nlp_policy_nz\pipeline_api.py tests\test_argument.py tests\test_stance.py tests\test_argument_training.py tests\test_argument_api_graph.py tests\test_track13_evidence.py` -> passed
- `python -B -m py_compile src\nlp_policy_nz\discourse\argument.py src\nlp_policy_nz\discourse\stance.py src\nlp_policy_nz\training\track13_evidence.py` -> passed
- `python -B -m json.tool conductor\tracks\track13_argument_stance_20260613\metadata.json > nul` -> passed

## External Gates Still Required

- 500+ human/gold Hansard argument-component labels.
- 500+ human/gold Hansard stance labels.
- Fine-tuned transformer model IDs for argument component and stance classifiers.
- Held-out Hansard F1 and accuracy reports meeting the Track 13 thresholds.
