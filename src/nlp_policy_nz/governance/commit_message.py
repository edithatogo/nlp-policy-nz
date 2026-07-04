"""Conventional commit linting helpers used by pre-commit and CI."""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Iterable

COMMIT_MESSAGE_PATTERN = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|test|chore|build|ci|perf)"
    r"(?:\([a-z0-9._/-]+\))?"
    r"(?P<breaking>!)?: "
    r"(?P<description>.+)$",
)


def lint_commit_message(message: str) -> list[str]:
    """Return validation errors for a single commit subject line."""
    subject = _first_meaningful_line(message)
    if subject is None:
        return ["commit message is empty"]
    if COMMIT_MESSAGE_PATTERN.match(subject) is None:
        return [
            "commit message must use conventional format "
            "`type(scope): description` with an allowed type"
        ]
    return []


def lint_commit_messages(messages: Iterable[str]) -> list[str]:
    """Return validation errors for a sequence of commit messages."""
    errors: list[str] = []
    for message in messages:
        for error in lint_commit_message(message):
            errors.append(f"{_first_meaningful_line(message) or '<empty>'}: {error}")
    return errors


def load_commit_messages_from_git() -> list[str]:
    """Load commit subjects from the current CI context."""
    base_ref = os.environ.get("GITHUB_BASE_REF", "").strip()
    if base_ref:
        range_spec = f"origin/{base_ref}..HEAD"
        return _git_subjects(range_spec)
    return _git_subjects("HEAD~1..HEAD", fallback_single=True)


def _git_subjects(range_spec: str, *, fallback_single: bool = False) -> list[str]:
    try:
        result = subprocess.run(  # noqa: S603
            ["git", "log", "--no-merges", "--format=%s", range_spec],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        if not fallback_single:
            raise
        single = subprocess.run(  # noqa: S603
            ["git", "log", "--no-merges", "-1", "--format=%s"],
            check=True,
            capture_output=True,
            text=True,
        )
        return _filter_commit_subjects(single.stdout.splitlines())
    return _filter_commit_subjects(result.stdout.splitlines())


def _filter_commit_subjects(lines: Iterable[str]) -> list[str]:
    return [
        line
        for line in lines
        if (subject := line.strip()) and not subject.startswith("Merge ")
    ]


def _first_meaningful_line(message: str) -> str | None:
    for line in message.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return None
