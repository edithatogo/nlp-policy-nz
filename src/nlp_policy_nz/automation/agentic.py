"""Deterministic helpers for agent review, auto-fix, track advancement, and judge eval."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from nlp_policy_nz.training.eval import exact_match, token_f1

Runner = Callable[..., subprocess.CompletedProcess[str]]

_TRACK_HEADING_RE = re.compile(r"^## \[(?P<status>[~ x])\] (?P<title>Track \d+: .+)$")
_TASK_ROW_RE = re.compile(r"^\|\s*\d+\s*\|.*?\|\s*\[(?P<status>[~ x])\]\s*\|", re.MULTILINE)
_TRACK_LINK_RE = re.compile(r"\./conductor/tracks/(?P<track_id>[^/]+)/")


@dataclass(frozen=True, slots=True)
class JudgeCase:
    """A single candidate output to compare against a reference."""

    model_id: str
    prompt: str
    prediction: str
    reference: str
    task: str = "general"


def _normalize_status(value: str) -> str:
    return value.strip().casefold()


def build_review_summary(checks: Mapping[str, Mapping[str, str]]) -> dict[str, Any]:
    """Build a structured PR review summary from named quality-gate results."""
    passed_gates: list[str] = []
    failed_gates: list[str] = []
    lines = ["# Agent Review Summary", ""]

    for gate, result in sorted(checks.items()):
        status = _normalize_status(result.get("status", "unknown"))
        detail = result.get("detail", "").strip()
        remediation = result.get("remediation", "").strip()
        if status in {"pass", "passed", "ok", "success"}:
            passed_gates.append(gate)
            status_label = "PASS"
        else:
            failed_gates.append(gate)
            status_label = "FAIL"
        lines.append(f"- `{gate}`: {status_label}{f' - {detail}' if detail else ''}")
        if remediation:
            lines.append(f"  - Remediation: {remediation}")

    decision = "approve" if not failed_gates else "request_changes"
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Outcome: {decision}",
            f"- Passed gates: {', '.join(passed_gates) if passed_gates else 'none'}",
            f"- Failed gates: {', '.join(failed_gates) if failed_gates else 'none'}",
        ],
    )

    return {
        "decision": decision,
        "passed_gates": passed_gates,
        "failed_gates": failed_gates,
        "summary": {
            "passed": len(passed_gates),
            "failed": len(failed_gates),
        },
        "markdown": "\n".join(lines) + "\n",
    }


def render_review_markdown(summary: Mapping[str, Any]) -> str:
    """Return the review markdown from :func:`build_review_summary`."""
    markdown = summary.get("markdown")
    if not isinstance(markdown, str):
        raise TypeError("summary must include markdown text")
    return markdown


def run_auto_fix(root: Path, runner: Runner = subprocess.run) -> dict[str, Any]:
    """Run the auto-fix sequence used by the CI healing workflow."""
    commands = [
        [sys.executable, "-m", "ruff", "check", "--fix", "src", "tests", "scripts"],
        [sys.executable, "-m", "ruff", "format", "src", "tests", "scripts"],
        [sys.executable, "-m", "basedpyright", "src"],
    ]
    command_results: list[dict[str, Any]] = []
    ruff_fixed = True
    basedpyright_passed = True

    for command in commands:
        completed = runner(  # noqa: S603
            command,
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        command_results.append(
            {
                "command": command,
                "returncode": completed.returncode,
                "stdout": getattr(completed, "stdout", ""),
                "stderr": getattr(completed, "stderr", ""),
            },
        )
        if command[2] == "ruff" and completed.returncode != 0:
            ruff_fixed = False
        if command[2] == "basedpyright" and completed.returncode != 0:
            basedpyright_passed = False

    return {
        "ruff_fixed": ruff_fixed,
        "basedpyright_passed": basedpyright_passed,
        "commands": command_results,
    }


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _track_title_from_plan(plan_path: Path) -> str:
    first_line = _read_text(plan_path).splitlines()[0].strip()
    if not first_line.startswith("# "):
        raise ValueError(f"{plan_path} does not start with a markdown heading")
    return first_line[2:]


def _plan_is_complete(plan_text: str) -> bool:
    task_rows = [
        match.group("status")
        for match in _TASK_ROW_RE.finditer(plan_text)
    ]
    return bool(task_rows) and all(status == "x" for status in task_rows)


def _registry_entries(registry_text: str) -> list[dict[str, str]]:
    lines = registry_text.splitlines()
    entries: list[dict[str, str]] = []
    idx = 0
    while idx < len(lines):
        match = _TRACK_HEADING_RE.match(lines[idx].strip())
        if not match:
            idx += 1
            continue
        track_title = match.group("title")
        track_status = match.group("status")
        track_id = ""
        lookahead = idx + 1
        while lookahead < len(lines) and not lines[lookahead].startswith("## "):
            link_match = _TRACK_LINK_RE.search(lines[lookahead])
            if link_match:
                track_id = link_match.group("track_id")
                break
            lookahead += 1
        entries.append(
            {
                "title": track_title,
                "status": track_status,
                "track_id": track_id,
                "line_index": str(idx),
            },
        )
        idx = lookahead + 1
    return entries


def _update_registry_status(registry_text: str, title: str, new_status: str) -> str:
    pattern = re.compile(rf"^## \[[~ x]\] {re.escape(title)}$", re.MULTILINE)
    replacement = f"## [{new_status}] {title}"
    updated_text, count = pattern.subn(replacement, registry_text, count=1)
    if count == 0:
        raise ValueError(f"Track heading '{title}' was not found in the registry")
    return updated_text


def _next_incomplete_track(entries: Sequence[Mapping[str, str]], current_index: int) -> str | None:
    for entry in entries[current_index + 1 :]:
        if entry["status"] != "x":
            return entry["track_id"] or None
    return None


def advance_completed_track(repo_root: Path, track_id: str) -> dict[str, Any]:
    """Advance a completed track by updating its metadata and registry state."""
    track_dir = repo_root / "conductor" / "tracks" / track_id
    plan_path = track_dir / "plan.md"
    metadata_path = track_dir / "metadata.json"
    registry_path = repo_root / "conductor" / "tracks.md"

    plan_text = _read_text(plan_path)
    track_title = _track_title_from_plan(plan_path)
    plan_complete = _plan_is_complete(plan_text)

    metadata = json.loads(_read_text(metadata_path))
    registry_text = _read_text(registry_path)
    entries = _registry_entries(registry_text)
    current_index = next(
        (index for index, entry in enumerate(entries) if entry["track_id"] == track_id),
        -1,
    )
    if current_index < 0:
        raise ValueError(f"Track '{track_id}' is not registered in conductor/tracks.md")

    if plan_complete:
        metadata["status"] = "complete"
        metadata["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        registry_path.write_text(
            _update_registry_status(registry_text, track_title, "x"),
            encoding="utf-8",
        )
        registry_status = "complete"
    else:
        registry_status = entries[current_index]["status"]

    return {
        "track_id": track_id,
        "track_status": "complete" if plan_complete else "incomplete",
        "registry_status": registry_status,
        "next_track_id": _next_incomplete_track(entries, current_index),
        "plan_complete": plan_complete,
    }


def evaluate_judge_run(cases: Sequence[Mapping[str, str]]) -> dict[str, Any]:
    """Score multiple model outputs with deterministic judge metrics."""
    if not cases:
        raise ValueError("At least one evaluation case is required")

    per_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        model_id = case["model_id"]
        prediction = case["prediction"]
        reference = case["reference"]
        case_metrics = {
            "model_id": model_id,
            "task": case.get("task", "general"),
            "prompt": case.get("prompt", ""),
            "prediction": prediction,
            "reference": reference,
            "exact_match": exact_match(prediction, reference),
            "token_f1": token_f1(prediction.split(), reference.split()),
        }
        case_metrics["judge_score"] = round(
            (case_metrics["exact_match"] + case_metrics["token_f1"]) / 2,
            6,
        )
        per_model[model_id].append(case_metrics)

    ranked_models = []
    for model_id, rows in per_model.items():
        judge_score = round(sum(row["judge_score"] for row in rows) / len(rows), 6)
        exact_match_score = round(sum(row["exact_match"] for row in rows) / len(rows), 6)
        token_f1_score = round(sum(row["token_f1"] for row in rows) / len(rows), 6)
        ranked_models.append(
            {
                "model_id": model_id,
                "judge_score": judge_score,
                "exact_match": exact_match_score,
                "token_f1": token_f1_score,
                "cases": rows,
            },
        )

    ranked_models.sort(
        key=lambda item: (item["judge_score"], item["exact_match"], item["token_f1"]),
        reverse=True,
    )
    best_model_id = ranked_models[0]["model_id"]

    lines = [
        "# LLM-as-Judge Evaluation",
        "",
        "| Model | Judge score | Exact match | Token F1 |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in ranked_models:
        lines.append(
            f"| {row['model_id']} | {row['judge_score']:.3f} | "
            f"{row['exact_match']:.3f} | {row['token_f1']:.3f} |"
        )

    return {
        "best_model_id": best_model_id,
        "ranked_models": ranked_models,
        "markdown": "\n".join(lines) + "\n",
    }
