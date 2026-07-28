# Track 99 Evidence

## Scope completed (repository-side)

- Decision record: `docs/haystack-governance-decision.md`
- Sovereign/air-gap checklist: `docs/haystack-sovereign-deploy.md`
- Pure-Python orchestration package: `src/nlp_policy_nz/orchestration/haystack/`
- Contract tests: `tests/test_track99_haystack_governance.py` (13 passed)
- Optional extras: `rag` and `orchestration` both map to `haystack-ai>=2.0.0` without making it required

## Validation

```text
pixi run --frozen -e py312 pytest tests/test_track99_haystack_governance.py -q
13 passed
```

## Explicit boundaries (not claimed)

- No legal promotion, rights clearance, or publication from this track
- `haystack-ai` is not a default runtime dependency
- Extractive QA uses a local token-overlap proxy, not a pinned Transformers reader
- FaithfulnessEvaluator is non-authoritative for OIA/promotion evidence
- Full PROV-O `ProvenanceRecorder.finish()` dual-write remains scaffolding via `ProvenanceStepRecorder`

## GitHub cross-refs

- Parent: #189
- Subissues: #190–#194
