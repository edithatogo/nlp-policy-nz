# Track 57: DSPy Program Optimization for Legal NLP

**Dependencies**: Tracks 20, 22, 23, 53, 55  
**Parallelization Node**: LLM Program Optimization  
**Status**: Planned

---

## Goal

Evaluate DSPy as an optional typed program optimization layer for legal
extraction, retrieval-grounded annotation, and model evaluation without
replacing the deterministic rule and retrieval paths already used by the repo.

## Context

The repository already has deterministic extraction, evaluation, and retrieval
helpers. Track 57 tests whether DSPy adds measurable value for prompt/program
optimization, or whether the repo should keep the dependency out of the default
stack and rely on local shims and prompt templates instead.

## Scope

- Define at least three candidate signatures for legal NLP program optimization.
- Run one deterministic optimizer experiment against a small gold or synthetic
  evaluation set.
- Compare generated candidates against the current baseline helpers.
- Record source anchors and review metadata on every candidate.
- Decide whether DSPy should remain optional, stay experimental, or be rejected
  as a required dependency.

## Acceptance Criteria

- [ ] DSPy is documented as optional, experimental, or rejected in dependency policy.
- [ ] At least three signatures and one optimizer experiment are implemented.
- [ ] A gold or synthetic eval set compares DSPy output with current baselines.
- [ ] All generated candidates include source anchors and review metadata.
- [ ] A go/no-go recommendation is recorded with evidence and rollback steps.

