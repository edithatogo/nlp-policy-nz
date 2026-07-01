# Track 22 Evidence Boundary - 2026-06-24

This note records the current repo-side Isaacus integration evidence. It does not claim that Isaacus datasets, models, proprietary APIs, semchunk, Blackstone Graph, or Hugging Face publication gates have been executed.

## Repo-side evidence

- `src/nlp_policy_nz/training/isaacus_adapter.py` defines offline Isaacus dataset, model, and tool manifests.
- Australian legal source rows can be normalized and converted into the existing `PipelineRecord` schema.
- `data/track22/nz_mleb_fixture.json` provides a deterministic local NZ-MLEB fixture with three NZ documents, three retrieval queries, and relevance judgements.
- `data/track22/nz_mleb_fixture.schema.json` records the local fixture contract, and `load_nz_mleb_fixture` / `validate_nz_mleb_fixture` enforce the schema-critical invariants without live Isaacus access.
- Track 22 evidence reporting now treats the repo-side contract as satisfied only when the local NZ-MLEB fixture has at least three validated queries and schema validation is true.
- External operations fail closed through explicit network/proprietary API access gates.
- `scripts/download_isaacus_datasets.sh` and `scripts/evaluate_isaacus_models.sh` are audit-only wrappers that set offline/no-telemetry environment guards and reject live mode.
- `docs/isaacus_integration.md` records the local integration boundary and external execution requirements.
- `src/nlp_policy_nz/training/track22_evidence.py` separates repo-side contracts from external acceptance gates.

## Validation

- `python -B -m pytest -p no:cacheprovider -q tests\test_isaacus_adapter.py tests\test_track22_evidence.py tests\test_track22_script_contracts.py --basetemp C:\tmp\nlp-policy-nz-track22-fixture` passed with escalation for Git Bash process access: 16 passed.
- The same pytest command without escalation collected and ran the Python Track 22 tests, but Git Bash wrapper tests failed under sandboxed process access with `fatal error - couldn't create signal pipe, Win32 error 5`; the rerun with normal process access passed.
- `python -m ruff check --no-cache src\nlp_policy_nz\training\isaacus_adapter.py src\nlp_policy_nz\training\track22_evidence.py src\nlp_policy_nz\training\__init__.py tests\test_isaacus_adapter.py tests\test_track22_evidence.py tests\test_track22_script_contracts.py` passed.
- `python -m json.tool data\track22\nz_mleb_fixture.json > nul && python -m json.tool data\track22\nz_mleb_fixture.schema.json > nul` passed.
- `python -B -m py_compile src\nlp_policy_nz\training\isaacus_adapter.py` was attempted but could not write `__pycache__` in this workspace (`Permission denied`); the focused pytest import path above validated the module with bytecode disabled.
- `python -B -m pytest -p no:cacheprovider -q tests\test_isaacus_adapter.py tests\test_track22_evidence.py tests\test_track22_script_contracts.py` passed: 16 passed.
- `python -m ruff check --no-cache src\nlp_policy_nz\training\isaacus_adapter.py src\nlp_policy_nz\training\track22_evidence.py src\nlp_policy_nz\training\__init__.py tests\test_isaacus_adapter.py tests\test_track22_evidence.py tests\test_track22_script_contracts.py` passed.

## External gates not satisfied

- Download, hash, normalize, and merge `isaacus/open-australian-legal-corpus` with NZ corpora.
- Download and evaluate Isaacus open models on NZ legal benchmarks.
- Evaluate Kanon 2 Embedder through a credentialed API or air-gapped deployment.
- Publish measured NZ-MLEB baselines from retrieval runs over full legislation, Hansard, and court-decision corpora.
- Install and evaluate `semchunk` against local legal chunking.
- Integrate Blackstone Graph only after a stable upstream release exists.

## Repo-Side Closeout - 2026-07-01

Track 22 is now repo-side complete. The repository contains the offline Isaacus
manifests, AU legal row normalization, PipelineRecord conversion, deterministic
local NZ-MLEB fixture and schema validation, fail-closed network/proprietary API
gates, audit-only shell wrappers, integration documentation, evidence helpers,
focused tests, and `external_gate_manifest.json`.

The external gate manifest records the evidence required before Track 22 may
claim live Isaacus integration:

- Open Australian Legal Corpus download, hashing, normalization, and NZ-AU
  merged corpus artifacts.
- Measured Isaacus open-model evaluation against NZ legal tasks.
- Credentialed Kanon 2 API or air-gapped retrieval evaluation.
- Measured NZ-MLEB baselines and publication artifacts.
- semchunk segmentation comparison against local chunking.
- Blackstone Graph stable-release monitoring with dated upstream evidence.

Latest validation:

- `pixi run pytest -p no:tach -p no:cacheprovider -q tests/test_isaacus_adapter.py tests/test_track22_evidence.py tests/test_track22_script_contracts.py tests/test_track22_external_gate_manifest.py` passed.
- `pixi run ruff check src/nlp_policy_nz/training/isaacus_adapter.py src/nlp_policy_nz/training/track22_evidence.py tests/test_isaacus_adapter.py tests/test_track22_evidence.py tests/test_track22_script_contracts.py tests/test_track22_external_gate_manifest.py` passed.
- `pixi run python -m json.tool conductor/archive/track22_isaacus_integration_20260613/external_gate_manifest.json` passed.
- `pixi run python -m json.tool conductor/archive/track22_isaacus_integration_20260613/metadata.json` passed.
