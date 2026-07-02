# LangGraph Orchestration Evaluation

This repository evaluates LangGraph only as an optional orchestration layer for durable, inspectable, human-in-the-loop legal NLP workflows.

## Candidate workflow

The current candidate workflow is deliberately explicit:

`intake -> triage -> draft -> review -> recover -> complete`

The evaluation harness treats `review` as the human-in-the-loop gate and `recover` as the durable replay path.

## Allowed contexts

- Durable legal review queues.
- Inspectable ontology mapping assistance.
- Recovery-aware annotation workflows.

## Banned contexts

- Core deterministic extraction pipelines.
- Raw-speed-only benchmarking exercises.
- Production flows without a Python fallback.
- External-service-dependent workflows in CI.

## Operational-value benchmark

The repository does not benchmark LangGraph by wall-clock speed. It scores:

- explicit state coverage,
- review-gate presence,
- recovery-path presence,
- telemetry density,
- and checkpoint cleanup readiness.

That keeps the decision tied to workflow quality instead of runtime hype.

## Runtime policy

LangGraph remains optional. The default path stays pure Python so GitHub Actions, Windows development, and offline validation continue to work without extra services.
