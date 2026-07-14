# DSPy Program Optimization Decision

Track 57 evaluates whether DSPy should become a required dependency for legal NLP
prompt/program optimization. The repo-side decision is to keep DSPy out of the
default dependency set and treat it as optional prototype territory only.

## What Was Evaluated

- three signature candidates for deontic extraction, grounded annotation, and evaluation recommendation
- one deterministic optimizer experiment comparing a baseline program against a structured prompt/program variant
- source anchor and review metadata coverage for every generated candidate
- a rollback plan that keeps the deterministic helpers and removes the optional layer cleanly

## Decision

DSPy is documented as rejected as a required dependency for this repository.
The repo already has deterministic extraction, retrieval, and evaluation helpers
that cover the current use cases without introducing another runtime dependency.

## Rollback

1. Remove the optional Track 57 helper module if it is no longer needed.
2. Keep the deterministic eval fixtures and baseline templates.
3. Re-run the Track 57 evidence tests before changing dependency policy again.

## Evidence Boundary

The repo-side experiment is synthetic and deterministic. It is enough to support
the dependency decision, but it is not a substitute for a live external DSPy
benchmark if one is later introduced.

