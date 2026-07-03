# Track 62 Evidence

## Summary

Track 62 evaluates vLLM as an optional high-throughput local generation
runtime and OpenAI-compatible serving layer. The implementation is repo-side
only, keeps Python fallback behavior canonical, and is now archived.

## Implementation Notes

- `src/nlp_policy_nz/semantic/vllm_runtime.py`
  - Adds optional offline and OpenAI-compatible completion helpers.
  - Adds a deterministic baseline comparison helper and evidence report
    dataclasses.
- `tests/test_track62_vllm_runtime.py`
  - Covers the fake endpoint path, offline engine path, missing-dependency
    behavior, the evidence report, and the baseline comparison helper.
- `docs/vllm_local_inference_runtime.md`
  - Records supported and unsupported runtime modes plus DSPy and spaCy-llm
    integration points.
- `conductor/tracks.md`
  - Registers Track 62 in the Phase VIII registry and moves it to the archived
    section.

## Validation

- `uv run python -m pytest tests/test_smoke.py tests/test_track62_vllm_runtime.py -q`
  - Passed: `17 passed`
- `uv run ruff check src/nlp_policy_nz/semantic/vllm_runtime.py src/nlp_policy_nz/semantic/__init__.py src/nlp_policy_nz/__init__.py tests/test_track62_vllm_runtime.py`
  - Passed with no lint findings.

## GitHub Mirror

- GitHub issue `#64` is updated with the archived Track 62 implementation
  state.
- The issue is present in GitHub Projects `#3` and `#4` with completed status
  and mirrored Track 62 metadata.

## Residual Notes

- The archived track now lives under
  `conductor/archive/track62_vllm_local_inference_runtime_20260701/`.
