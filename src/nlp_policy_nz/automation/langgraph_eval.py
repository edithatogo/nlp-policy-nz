"""Deterministic LangGraph evaluation helpers for legal NLP orchestration."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import Any

TRACK_ID = "track58_langgraph_orchestration_eval_20260701"

WORKFLOW_STATES: tuple[str, ...] = (
    "intake",
    "triage",
    "draft",
    "review",
    "recover",
    "complete",
)

ALLOWED_CONTEXTS: tuple[str, ...] = (
    "durable legal review queues",
    "inspectable ontology mapping assistance",
    "recovery-aware annotation workflows",
)

BANNED_CONTEXTS: tuple[str, ...] = (
    "core deterministic extraction pipelines",
    "raw-speed-only benchmarking exercises",
    "production flows without a Python fallback",
    "external-service-dependent workflows in CI",
)

TELEMETRY_EVENTS: tuple[str, ...] = (
    "state_transition",
    "review_gate",
    "checkpoint_cleanup",
    "decision_record",
)

DEFAULT_ITEMS: tuple[dict[str, Any], ...] = (
    {
        "item_id": "legal-review-queue",
        "needs_review": True,
        "needs_recovery": True,
        "checkpoint_files": ("review.checkpoint", "review.stale"),
    },
    {
        "item_id": "ontology-mapping-queue",
        "needs_review": False,
        "needs_recovery": False,
        "checkpoint_files": (),
    },
)


@dataclass(frozen=True, slots=True)
class CandidateTransition:
    """A single state transition in the candidate workflow."""

    state: str
    next_state: str | None
    rationale: str


@dataclass(frozen=True, slots=True)
class CandidateWorkflow:
    """The explicit LangGraph candidate workflow under evaluation."""

    name: str
    states: tuple[str, ...]
    transitions: tuple[CandidateTransition, ...]
    human_in_loop_states: tuple[str, ...]
    telemetry_events: tuple[str, ...]
    allowed_contexts: tuple[str, ...]
    banned_contexts: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation."""
        payload = asdict(self)
        payload["transitions"] = [asdict(transition) for transition in self.transitions]
        return payload


def build_candidate_workflow() -> CandidateWorkflow:
    """Build the deterministic candidate workflow used in evaluation."""
    transitions = (
        CandidateTransition(
            state="intake",
            next_state="triage",
            rationale="Capture the item, normalize input, and attach trace metadata.",
        ),
        CandidateTransition(
            state="triage",
            next_state="draft",
            rationale="Route the item to the legal drafting or ontology helper path.",
        ),
        CandidateTransition(
            state="draft",
            next_state="review",
            rationale="Require a human review gate before completion.",
        ),
        CandidateTransition(
            state="review",
            next_state="recover",
            rationale="Allow a durable recovery loop when a checkpoint needs replay.",
        ),
        CandidateTransition(
            state="recover",
            next_state="complete",
            rationale="Replay the recovered state and complete the item deterministically.",
        ),
        CandidateTransition(
            state="complete",
            next_state=None,
            rationale="Mark the item complete and emit the decision record.",
        ),
    )
    return CandidateWorkflow(
        name="legal-nlp-human-in-loop-orchestration",
        states=WORKFLOW_STATES,
        transitions=transitions,
        human_in_loop_states=("review",),
        telemetry_events=TELEMETRY_EVENTS,
        allowed_contexts=ALLOWED_CONTEXTS,
        banned_contexts=BANNED_CONTEXTS,
    )


def build_decision_record(workflow: CandidateWorkflow | None = None) -> dict[str, Any]:
    """Build the explicit allow / ban decision record."""
    selected = workflow or build_candidate_workflow()
    return {
        "track_id": TRACK_ID,
        "allowed": list(selected.allowed_contexts),
        "banned": list(selected.banned_contexts),
        "telemetry_required": list(selected.telemetry_events),
        "checkpoint_cleanup_required": True,
        "python_fallback_required": True,
        "promotion_rule": "Allow LangGraph only for durable inspectable workflows that preserve deterministic fallback paths.",
    }


def cleanup_checkpoints(checkpoint_dir: Path, *, suffixes: Sequence[str] = (".checkpoint", ".stale")) -> dict[str, Any]:
    """Remove stale checkpoint files from a directory and report what changed."""
    removed: list[str] = []
    if not checkpoint_dir.exists():
        return {"removed": removed, "remaining": []}
    for path in sorted(checkpoint_dir.iterdir()):
        if path.is_file() and any(path.name.endswith(suffix) for suffix in suffixes):
            path.unlink()
            removed.append(path.name)
    remaining = [path.name for path in sorted(checkpoint_dir.iterdir()) if path.is_file()]
    return {"removed": removed, "remaining": remaining}


def _run_item(item: Mapping[str, Any], workflow: CandidateWorkflow) -> dict[str, Any]:
    """Run one deterministic prototype item through the explicit states."""
    item_id = str(item["item_id"])
    needs_review = bool(item.get("needs_review", False))
    needs_recovery = bool(item.get("needs_recovery", False))
    transition_map = {transition.state: transition.next_state for transition in workflow.transitions}
    trace: list[str] = []
    telemetry: list[str] = []
    state = "intake"
    while state is not None:
        trace.append(state)
        telemetry.append(f"{item_id}:{state}")
        if state == "complete":
            break
        next_state = transition_map.get(state)
        if (state == "draft" and not needs_review) or (
            state == "review" and not needs_recovery
        ) or state == "recover":
            next_state = "complete"
        state = next_state
    if any(state not in workflow.states for state in trace):
        raise ValueError(f"Unexpected state in prototype trace for {item_id}")
    checkpoints = tuple(str(name) for name in item.get("checkpoint_files", ()))
    return {
        "item_id": item_id,
        "trace": trace,
        "telemetry": telemetry,
        "checkpoint_files": list(checkpoints),
        "requires_review": needs_review,
        "requires_recovery": needs_recovery,
    }


def _score_operational_value(runs: Sequence[Mapping[str, Any]], workflow: CandidateWorkflow) -> dict[str, Any]:
    """Score the prototype on operational value instead of throughput."""
    visited_states = {state for run in runs for state in run["trace"]}
    state_coverage = len(visited_states.intersection(workflow.states)) / len(workflow.states)
    review_gate_count = sum(1 for run in runs if run["requires_review"])
    recovery_count = sum(1 for run in runs if run["requires_recovery"])
    telemetry_density = sum(len(run["telemetry"]) for run in runs) / max(1, sum(len(run["trace"]) for run in runs))
    cleanup_ready_count = sum(1 for run in runs if run["checkpoint_files"])
    candidate_score = round(
        100.0
        * (
            0.35 * state_coverage
            + 0.25 * min(1.0, review_gate_count / max(1, len(runs)))
            + 0.20 * min(1.0, recovery_count / max(1, len(runs)))
            + 0.20 * min(1.0, telemetry_density)
        ),
        2,
    )

    baseline_score = round(
        100.0
        * (
            0.35 * (3 / len(workflow.states))
            + 0.25 * 0.0
            + 0.20 * 0.0
            + 0.20 * 0.5
        ),
        2,
    )

    return {
        "candidate_score": candidate_score,
        "baseline_score": baseline_score,
        "delta": round(candidate_score - baseline_score, 2),
        "state_coverage": round(state_coverage, 3),
        "review_gate_count": review_gate_count,
        "recovery_count": recovery_count,
        "telemetry_density": round(telemetry_density, 3),
        "cleanup_ready_count": cleanup_ready_count,
        "decision": "proceed" if candidate_score >= baseline_score else "defer",
    }


def run_deterministic_prototype(
    items: Sequence[Mapping[str, Any]] | None = None,
    *,
    workflow: CandidateWorkflow | None = None,
) -> dict[str, Any]:
    """Run the deterministic prototype without external services."""
    selected = workflow or build_candidate_workflow()
    selected_items = items or DEFAULT_ITEMS
    runs = [_run_item(item, selected) for item in selected_items]
    benchmark = _score_operational_value(runs, selected)
    checkpoint_dir = Path(".tmp") / "track58_checkpoint_probe"
    cleanup = cleanup_checkpoints(checkpoint_dir)
    decision = build_decision_record(selected)
    return {
        "track_id": TRACK_ID,
        "workflow": selected.to_dict(),
        "runs": runs,
        "benchmark": benchmark,
        "checkpoint_cleanup": cleanup,
        "decision_record": decision,
        "langgraph_available": find_spec("langgraph") is not None,
    }


def render_evaluation_report(result: Mapping[str, Any]) -> str:
    """Render a compact markdown report for docs and evidence."""
    workflow = result["workflow"]
    benchmark = result["benchmark"]
    decision = result["decision_record"]
    lines = [
        "# Track 58 LangGraph Evaluation",
        "",
        f"- Track: `{result['track_id']}`",
        f"- Workflow: `{workflow['name']}`",
        f"- Operational score: `{benchmark['candidate_score']}` vs baseline `{benchmark['baseline_score']}`",
        f"- Decision: `{benchmark['decision']}`",
        "",
        "## States",
        "",
        ", ".join(workflow["states"]),
        "",
        "## Allowed",
        "",
    ]
    lines.extend(f"- {item}" for item in decision["allowed"])
    lines.extend(["", "## Banned", ""])
    lines.extend(f"- {item}" for item in decision["banned"])
    lines.extend(
        [
            "",
            "## Telemetry",
            "",
        ]
    )
    lines.extend(f"- {event}" for event in decision["telemetry_required"])
    lines.extend(
        [
            "",
            "## Checkpoint cleanup",
            "",
            json.dumps(result["checkpoint_cleanup"], indent=2, sort_keys=True),
            "",
        ],
    )
    return "\n".join(lines)


def evaluation_fingerprint(result: Mapping[str, Any]) -> str:
    """Return a stable fingerprint for the evaluation result."""
    payload = json.dumps(result, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
