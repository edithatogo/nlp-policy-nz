# Track 13: Argument Mining & Policy Stance Detection

**Dependencies**: Track 5, Track 7
**Parallelization Node**: Discourse Analysis
**Status**: In Progress

---

## Implementation Note

Repo-side argument/stance contracts are implemented: deterministic Hansard annotation, PipelineRecord storage, AIF JSON-LD graph export, API serialization, supervised training-example extraction for explicitly gold-labelled records, serializable Legal-BERT fine-tuning job specs, and machine-readable evidence reporting. The original Track 13 acceptance gates for fine-tuned transformers, 500-segment human annotation sets, and held-out Hansard F1/accuracy remain open until those external artifacts and evaluation reports are added.

## Phase 1: Argument Component Detection

**Status**: In Progress

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Annotate 500 Hansard speech segments for argument components (premise, conclusion, none) | [ ] | |
| 1.2 | Fine-tune Legal-BERT for argument component sequence classification and record held-out F1 | [ ] | |
| 1.3 | Create `src/nlp_policy_nz/discourse/argument.py` with argument detector | [x] | |
| 1.4 | Write tests for component detection | [x] | |
| 1.5 | Add annotated-record extraction path and Legal-BERT argument job spec | [x] | |
| 1.6 | Add machine-readable evidence contract so fixture scores cannot satisfy held-out transformer gates | [x] | local |
| 1.7 | Add silver-label alternative lane with human-labelled calibration corpora and multi-provider AI consensus | [x] | local |
| 1.8 | Add repo-complete/external-blocked status summary for review handoff | [x] | local |
| 1.9 | Record local legal model recommendations and follow-up issue for NZ fine-tuning revisit | [x] | local |

## Phase 2: Stance Classification & Argument Graph

**Status**: In Progress

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Annotate 500 speech segments for stance (pro/con/neutral) | [ ] | |
| 2.2 | Fine-tune stance classifier on annotated debate data and record held-out accuracy | [ ] | |
| 2.3 | Implement ArgumentGraph with support/attack relations | [x] | |
| 2.4 | Add issue-argument linking via semantic similarity | [x] | |
| 2.5 | Add annotated-record extraction path and Legal-BERT stance job spec | [x] | |
| 2.6 | Add stance evidence contract for 500-segment held-out transformer accuracy gate | [x] | local |
| 2.7 | Add stance-compatible silver-label triangulation contract and disagreement queue | [x] | local |

## Phase 3: Pipeline Integration

**Status**: Completed

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add `arguments` and `stance` fields to PipelineRecord | [x] | |
| 3.2 | Update process_hansard() to run argument mining | [x] | |
| 3.3 | Update Parquet schema | [x] | |
| 3.4 | Run focused Track 13 and storage compatibility test gates | [x] | |


## Silver-label alternative lane

The gold human-label and held-out Legal-BERT gates remain open, but Track 13 now has an accepted silver alternative: sourced human-labelled calibration datasets, multi-provider AI votes from available local/remote providers, weak-rule signals, weighted consensus, and a disagreement queue. Silver outputs must not be represented as human gold labels.

## Model Recommendation Update

Legal-BERT remains a reproducible legacy encoder baseline, but it is no longer treated as the assumed best local legal model. Track 13 should evaluate `isaacus/emubert` as the preferred Australasian legal encoder baseline for local argument and stance classifiers. `Equall/Saul-7B-Instruct-v1` and `isaacus/open-australian-legal-llm` are tracked as legal LLM candidates for silver-label adjudication and disagreement review, not as gold-label evidence. Kanon 2 embedding/reranking remains a retrieval and semantic-linking candidate where API or air-gapped access is available.

Follow-up issue: https://github.com/edithatogo/nlp-policy-nz/issues/2

## Files Created/Modified

| File | Action |
|------|--------|
| `src/nlp_policy_nz/discourse/__init__.py` | Created |
| `src/nlp_policy_nz/discourse/argument.py` | Created |
| `src/nlp_policy_nz/discourse/stance.py` | Created |
| `src/nlp_policy_nz/training/data.py` | Modified |
| `src/nlp_policy_nz/training/trainers.py` | Modified |
| `src/nlp_policy_nz/training/__init__.py` | Modified |
| `src/nlp_policy_nz/cli/graph.py` | Modified |
| `src/nlp_policy_nz/api/server.py` | Modified |
| `src/nlp_policy_nz/pipeline_api.py` | Modified |
| `src/nlp_policy_nz/storage/serialization.py` | Modified |
| `tests/test_argument.py` | Created |
| `tests/test_stance.py` | Created |
| `tests/test_argument_training.py` | Created |
| `tests/test_argument_api_graph.py` | Created |
| `src/nlp_policy_nz/training/track13_evidence.py` | Created |
| `tests/test_track13_evidence.py` | Created |
| `conductor/tracks/track13_argument_stance_20260613/evidence.md` | Created |

## Verification

- `pytest tests\test_argument.py tests\test_stance.py tests\test_argument_training.py tests\test_argument_api_graph.py tests\test_storage.py -p no:cacheprovider -q` -> 28 passed
- `ruff check src\nlp_policy_nz\__init__.py src\nlp_policy_nz\api\__init__.py src\nlp_policy_nz\discourse src\nlp_policy_nz\storage\serialization.py src\nlp_policy_nz\pipeline_api.py src\nlp_policy_nz\training\data.py src\nlp_policy_nz\training\trainers.py src\nlp_policy_nz\training\__init__.py src\nlp_policy_nz\cli\graph.py src\nlp_policy_nz\api\server.py tests\test_argument.py tests\test_stance.py tests\test_argument_training.py tests\test_argument_api_graph.py` -> passed; Ruff cache write warnings only
- `PYTHONPATH=src python -c "import sys; import nlp_policy_nz; import nlp_policy_nz.api.server; print('torch' in sys.modules, 'transformers' in sys.modules)"` -> `False False`
- `python -m pytest -p no:cacheprovider -q tests\test_track13_evidence.py tests\test_argument.py tests\test_stance.py tests\test_argument_training.py tests\test_argument_api_graph.py` -> 18 passed
- `python -m ruff check --no-cache src\nlp_policy_nz\training\track13_evidence.py src\nlp_policy_nz\training\__init__.py tests\test_track13_evidence.py` -> passed; Ruff cache write warnings only
- `pytest tests\test_track13_evidence.py -q` -> 5 passed
- `pytest tests\test_argument_training.py tests\test_track13_evidence.py tests\test_training_eval.py -q` -> 16 passed
- `ruff check src\nlp_policy_nz\training\track13_evidence.py src\nlp_policy_nz\training\__init__.py tests\test_track13_evidence.py` -> passed; removed-rule warnings only
- `python -B -m pytest -p no:cacheprovider -q tests\test_argument.py tests\test_stance.py tests\test_argument_training.py tests\test_argument_api_graph.py tests\test_track13_evidence.py tests\test_storage.py --basetemp C:\tmp\nlp-policy-nz-track13-final3` -> 35 passed
- `python -m ruff check --no-cache src\nlp_policy_nz\discourse src\nlp_policy_nz\training\track13_evidence.py src\nlp_policy_nz\training\data.py src\nlp_policy_nz\training\trainers.py src\nlp_policy_nz\training\__init__.py src\nlp_policy_nz\cli\graph.py src\nlp_policy_nz\api\server.py src\nlp_policy_nz\storage\serialization.py src\nlp_policy_nz\pipeline_api.py tests\test_argument.py tests\test_stance.py tests\test_argument_training.py tests\test_argument_api_graph.py tests\test_track13_evidence.py` -> passed; removed-rule warnings only
- `python -B -m py_compile src\nlp_policy_nz\discourse\argument.py src\nlp_policy_nz\discourse\stance.py src\nlp_policy_nz\training\track13_evidence.py` -> passed
- `python -B -m json.tool conductor\tracks\track13_argument_stance_20260613\metadata.json > nul` -> passed
- `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_track13_evidence.py --basetemp C:\tmp\nlp-policy-nz-track13-status` -> 7 passed
- `.\.venv\Scripts\python.exe -m ruff check --no-cache src\nlp_policy_nz\training\track13_evidence.py src\nlp_policy_nz\training\__init__.py tests\test_track13_evidence.py` -> passed; removed-rule warnings only
- `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_argument.py tests\test_stance.py tests\test_argument_training.py tests\test_argument_api_graph.py tests\test_track13_evidence.py tests\test_track13_external_gate_manifest.py tests\test_track13_silver_labels.py --basetemp C:\tmp\nlp-policy-nz-track13-broad` -> 31 passed
- `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_track13_silver_labels.py --basetemp C:\tmp\nlp-policy-nz-track13-models` -> 10 passed
