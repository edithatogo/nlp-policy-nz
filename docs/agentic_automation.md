# Agentic Automation

This repository uses deterministic repo-side automation to support agentic workflows.

## Workflows

- `agent-review.yml` runs quality gates and renders a structured PR review summary.
- `auto-fix-ci.yml` attempts lint and formatting fixes, then commits them when the PR branch is writable.
- `conductor-advance.yml` advances completed Conductor tracks when their plans are fully marked done.
- `self-healing-ci.yml` reacts to failed CI runs and replays the auto-fix path before opening a repair PR.

## Scripts

- `scripts/agent_review.py` renders a markdown review from gate results.
- `scripts/ci_auto_fix.py` runs the lint/typecheck repair sequence.
- `scripts/conductor_advance_agent.py` updates Conductor registry state when a plan is complete.
- `scripts/llm_judge_eval.py` scores model outputs with deterministic judge metrics.
- `scripts/jules_integration.sh` provides a shell entrypoint for GPU dispatch payloads.

## Operating Notes

- These workflows are designed to be deterministic and testable in repo CI.
- External agent runtimes, GitHub write permissions, and GPU dispatch are still required for live automation.
