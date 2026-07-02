# Track 62: vLLM Local Inference Runtime Evaluation

## Overview

Track 62 evaluates whether vLLM should become the repository's optional
high-throughput local generation runtime and OpenAI-compatible serving layer.
The track is intentionally evaluation-first: Python fallback behavior remains
canonical, and no required dependency on vLLM is allowed unless the evidence
later justifies it.

## Requirements

- Keep vLLM optional and separate from the default inference path.
- Support both offline local generation and OpenAI-compatible endpoint mode.
- Preserve deterministic fixtures for CI and local evaluation.
- Record comparison evidence against a simple baseline completion path.
- Document supported and unsupported hardware/runtime modes.
- Document integration points for DSPy and spaCy-llm without forcing either.

## Acceptance Criteria

- [ ] vLLM generation helpers exist for offline and OpenAI-compatible modes.
- [ ] Tests cover a local fake endpoint fixture and a dependency-missing path.
- [ ] Benchmarks compare at least one prompt against a baseline completion path.
- [ ] Documentation records supported and unsupported runtime modes.
- [ ] Documentation records how DSPy and spaCy-llm could target the runtime.
- [ ] A go/no-go decision records whether vLLM is default, optional, or rejected.

## Out of Scope

- Making vLLM required for default imports or Windows development.
- Replacing deterministic extraction, schema projection, or publication tasks.
- Adding a production dependency on GPU-serving infrastructure.
