# Track 22 Evidence Boundary - 2026-06-23

This note records the current repo-side Isaacus integration evidence. It does not claim that Isaacus datasets, models, proprietary APIs, semchunk, Blackstone Graph, or Hugging Face publication gates have been executed.

## Repo-side evidence

- `src/nlp_policy_nz/training/isaacus_adapter.py` defines offline Isaacus dataset, model, and tool manifests.
- Australian legal source rows can be normalized and converted into the existing `PipelineRecord` schema.
- NZ-MLEB query scaffolding validates relevance judgements before benchmark use.
- External operations fail closed through explicit network/proprietary API access gates.
- `scripts/download_isaacus_datasets.sh` and `scripts/evaluate_isaacus_models.sh` are audit-only wrappers that set offline/no-telemetry environment guards and reject live mode.
- `docs/isaacus_integration.md` records the local integration boundary and external execution requirements.
- `src/nlp_policy_nz/training/track22_evidence.py` separates repo-side contracts from external acceptance gates.

## Validation

- `python -B -m pytest -p no:cacheprovider -q tests\test_isaacus_adapter.py tests\test_track22_evidence.py --basetemp C:\tmp\nlp-policy-nz-track22-final` passed: 10 tests.
- `python -m ruff check --no-cache src\nlp_policy_nz\training\isaacus_adapter.py src\nlp_policy_nz\training\track22_evidence.py src\nlp_policy_nz\training\__init__.py tests\test_isaacus_adapter.py tests\test_track22_evidence.py` passed.
- `python -B -m json.tool conductor\tracks\track22_isaacus_integration_20260613\metadata.json > nul` passed before this evidence update and should be rerun after metadata edits.

## External gates not satisfied

- Download, hash, normalize, and merge `isaacus/open-australian-legal-corpus` with NZ corpora.
- Download and evaluate Isaacus open models on NZ legal benchmarks.
- Evaluate Kanon 2 Embedder through a credentialed API or air-gapped deployment.
- Extend MLEB with NZ legislation, Hansard, and court-decision relevance judgements; publish measured baselines.
- Install and evaluate `semchunk` against local legal chunking.
- Integrate Blackstone Graph only after a stable upstream release exists.
