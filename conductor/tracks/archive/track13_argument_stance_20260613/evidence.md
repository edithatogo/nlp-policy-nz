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
## Silver Label Triangulation - 2026-06-23

- Added `silver_label_manifest.json` with a silver-label alternative for the 500-record annotation blocker.
- Added `ai_provider_labelling_plan.json` for installed local providers (`cline`, `opencode`, `mimo`, `agy`, `agent`) plus configured API providers (`openrouter`, `nvidia_nim`).
- Added `external_gate_manifest.json` with both the original gold gate and the accepted silver alternative gate.
- Added deterministic consensus tooling in `src/nlp_policy_nz/training/track13_silver.py` and tests in `tests/test_track13_silver_labels.py`.
- Human-labelled calibration sources are preferred where available: UKP argument annotations, IAM, ECHR legal argument mining, and LAMUS as LLM plus human-in-the-loop refinement.
- Silver labels remain silver evidence only and must not be reported as 500 human gold labels.
## Ontology Triangulation - 2026-06-23

- Added `ontology_triangulation_manifest.json` for HPO/UMLS/SNOMED CT/MeSH/MedDRA/ICD concept alignment in health-policy records.
- HPO downloads document UMLS-created xrefs, including UMLS and SNOMEDCT_US references; SNOMED International and Monarch also have a two-way HPO/SNOMED CT mapping effort.
- The ontology bridge is weighted as `weak_rule` evidence only. It can improve concept/topic triangulation for biomedical or health-policy text, but it cannot independently prove claim, premise, stance, support, or attack labels.
## Human-labelled Calibration Pull - 2026-06-23

- Pulled and mapped bounded calibration rows into `data/track13/calibration/`.
- UKP Argument Annotated Essays v2: 40 human-labelled BRAT spans mapped from the TUdatalib archive.
- IAM: 80 human-labelled claim/evidence rows mapped from public GitHub training splits.
- ECHR legal argument mining: 40 human-labelled legal argument rows mapped from public GitHub CSV annotations.
- LAMUS: 40 human-in-the-loop legal argument rows mapped from public GitHub CSV data.
- Combined calibration file: `data/track13/calibration/human_calibration_votes.jsonl` with 200 rows.
- These are external calibration rows only; they do not label the NZ target corpus directly and must not be represented as NZ Hansard human-gold labels.
## Silver Consensus Aggregation - 2026-06-23

- Ran Track 13 consensus aggregation over `data/track13/provider_votes/opencode.jsonl` and `data/track13/provider_votes/nvidia_nim.jsonl`.
- Produced `data/track13/silver_argument_labels.jsonl` and `data/track13/silver_argument_disagreements.jsonl`.
- Accepted silver labels: 0.
- Disagreements/review queue rows: 13.
- Reason: the current consensus contract requires at least three independent AI votes, or two AI votes plus a human-calibration vote for the same record. The target corpus currently has two independent provider votes per record, so all records were routed to the disagreement queue rather than over-accepted.
## Silver Model Evaluation - 2026-06-23

- Added `scripts/evaluate_track13_silver.py` to evaluate Track 13 argument/stance models against accepted silver labels when available.
- Produced `artifacts/track13/silver_eval_metrics.json` and `artifacts/track13/silver_eval_report.md`.
- Current accepted silver label count: 0, so accepted silver evaluation is blocked rather than overclaimed.
- Diagnostic-only disagreement queue metrics were computed over 13 rows: claim accuracy 0.615, premise accuracy 0.615, relation accuracy 0.462, stance-proxy accuracy 0.615.
- No fine-tuned Legal-BERT Track 13 artifact was loaded. The diagnostic uses the repo-side argument detector and stance classifier and is not acceptance evidence.
## Repo-Complete Review Handoff - 2026-06-29

- Added `Track13ImplementationStatus`, `summarize_track13_implementation_status()`, and `track13_implementation_status_contract()` so Track 13 can be reported as repo-side complete and review-ready without closing external gold-label or held-out Legal-BERT gates.
- The status contract carries accepted silver-label and disagreement-queue counts, and explicitly records that silver labels are not accepted as gold evidence.
- Current silver status remains unchanged: 0 accepted silver labels and 13 disagreement queue rows.
- Verification:
  - `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_track13_evidence.py --basetemp C:\tmp\nlp-policy-nz-track13-status` -> 7 passed.
  - `.\.venv\Scripts\python.exe -m ruff check --no-cache src\nlp_policy_nz\training\track13_evidence.py src\nlp_policy_nz\training\__init__.py tests\test_track13_evidence.py` -> passed; removed-rule warnings only.
  - `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_argument.py tests\test_stance.py tests\test_argument_training.py tests\test_argument_api_graph.py tests\test_track13_evidence.py tests\test_track13_external_gate_manifest.py tests\test_track13_silver_labels.py --basetemp C:\tmp\nlp-policy-nz-track13-broad` -> 31 passed.
## Legal Model Recommendation Update - 2026-06-29

- Added model recommendations to `ai_provider_labelling_plan.json`.
- `isaacus/emubert` is the preferred local Australasian legal encoder baseline to evaluate before treating `nlpaueb/legal-bert-base-uncased` as the default Track 13 classifier.
- `nlpaueb/legal-bert-base-uncased` remains a reproducible legacy encoder comparator.
- `Equall/Saul-7B-Instruct-v1` and `isaacus/open-australian-legal-llm` are candidate legal LLM adjudicators for silver-label disagreement queues and must not be counted as gold labels.
- Kanon 2 embedding/reranking remains scoped to retrieval, RAG, and semantic-linking evaluation where API or air-gapped access is available.
- Opened follow-up issue for revisiting model choices after NZ-legislation fine-tuning: https://github.com/edithatogo/nlp-policy-nz/issues/2
- Track 13 closed out after review and archive preparation on 2026-06-29.
- Verification:
  - `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_track13_silver_labels.py --basetemp C:\tmp\nlp-policy-nz-track13-models` -> 10 passed.
  - `.\.venv\Scripts\python.exe -B -m json.tool conductor\tracks\track13_argument_stance_20260613\ai_provider_labelling_plan.json > $null` -> passed.
