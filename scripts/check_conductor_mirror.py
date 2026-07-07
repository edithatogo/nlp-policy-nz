"""Check that the GitHub conductor mirror matches closed/open issue state."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = os.environ.get("GITHUB_REPOSITORY", "edithatogo/nlp-policy-nz")
DEFAULT_PROJECTS = (3, 4)
OPEN_STATUSES = {"planned", "new", "in_progress"}
CLOSED_STATUSES = {"archived", "completed"}


@dataclass(frozen=True, slots=True)
class MirrorFinding:
    """Describe one mismatch between issue state and mirror state."""

    project: int
    issue_number: int
    title: str
    issue_state: str
    project_status: str
    conductor_status: str | None
    status_labels: tuple[str, ...]

    def render(self) -> str:
        labels = ", ".join(self.status_labels) or "(none)"
        return (
            f"project {self.project} issue #{self.issue_number} {self.title!r}: "
            f"issue={self.issue_state}, project={self.project_status}, "
            f"conductor={self.conductor_status or '(unset)'}, labels={labels}"
        )


def _run_gh(args: list[str]) -> dict[str, Any]:
    result = subprocess.run(
        ["gh", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"gh {' '.join(args)} failed with exit code {result.returncode}: "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
    return json.loads(result.stdout)


def _project_items(project_number: int) -> list[dict[str, Any]]:
    payload = _run_gh(
        ["project", "item-list", str(project_number), "--owner", "@me", "--limit", "200", "--format", "json"],
    )
    return [
        item
        for item in payload.get("items", [])
        if item.get("repository") == f"https://github.com/{DEFAULT_REPO}"
    ]


def _issue(number: int) -> dict[str, Any]:
    return _run_gh(["api", f"repos/{DEFAULT_REPO}/issues/{number}"])


def _status_labels(issue_payload: dict[str, Any]) -> tuple[str, ...]:
    return tuple(
        label["name"]
        for label in issue_payload.get("labels", [])
        if isinstance(label, dict) and str(label.get("name", "")).startswith("status:")
    )


def _status_values(labels: tuple[str, ...]) -> set[str]:
    return {label.removeprefix("status:") for label in labels}


def _findings_for_project(project_number: int) -> list[MirrorFinding]:
    findings: list[MirrorFinding] = []
    for item in _project_items(project_number):
        track_number = item.get("track Number")
        content = item.get("content") or {}
        issue_number = content.get("number")
        if not isinstance(track_number, int) or not isinstance(issue_number, int):
            continue
        issue_payload = _issue(issue_number)
        issue_state = str(issue_payload.get("state", "")).lower()
        project_status = str(item.get("status", ""))
        conductor_status = item.get("conductor Status")
        status_labels = _status_labels(issue_payload)

        label_values = _status_values(status_labels)

        if issue_state == "closed":
            if conductor_status in OPEN_STATUSES:
                findings.append(
                    MirrorFinding(
                        project=project_number,
                        issue_number=issue_number,
                        title=str(item.get("title", "")),
                        issue_state=issue_state,
                        project_status=project_status,
                        conductor_status=str(conductor_status) if conductor_status else None,
                        status_labels=status_labels,
                    ),
                )
                continue
            if not label_values or not label_values & CLOSED_STATUSES:
                findings.append(
                    MirrorFinding(
                        project=project_number,
                        issue_number=issue_number,
                        title=str(item.get("title", "")),
                        issue_state=issue_state,
                        project_status=project_status,
                        conductor_status=str(conductor_status) if conductor_status else None,
                        status_labels=status_labels,
                    ),
                )
        elif issue_state == "open" and conductor_status in CLOSED_STATUSES:
            findings.append(
                MirrorFinding(
                    project=project_number,
                    issue_number=issue_number,
                    title=str(item.get("title", "")),
                    issue_state=issue_state,
                    project_status=project_status,
                    conductor_status=str(conductor_status) if conductor_status else None,
                    status_labels=status_labels,
                ),
            )
    return findings


def main(argv: list[str] | None = None) -> int:
    _ = argv
    try:
        findings = [finding for project in DEFAULT_PROJECTS for finding in _findings_for_project(project)]
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"mirror check failed: {exc}\n")
        return 2

    if findings:
        for finding in findings:
            sys.stderr.write(f"{finding.render()}\n")
        return 1

    sys.stdout.write("Conductor mirror is aligned.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
