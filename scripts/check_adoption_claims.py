"""Reject empirical adoption claims when the readiness gate is blocked."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "adoption_readiness.json"
CLAIM_PATTERNS = (
    re.compile(r"\bSOTA\b", re.IGNORECASE),
    re.compile(r"state[- ]of[- ]the[- ]art", re.IGNORECASE),
)


def find_violations(text: str, *, path: str = "document") -> list[str]:
    """Return over-claim diagnostics for one documentation string."""
    return [f"{path}: unsupported empirical adoption claim ({pattern.pattern})" for pattern in CLAIM_PATTERNS if pattern.search(text)]


def check() -> list[str]:
    """Check tracked Markdown documentation against the readiness manifest."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["status"] == "ready":
        return []

    violations: list[str] = []
    paths = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]
    for path in paths:
        violations.extend(find_violations(path.read_text(encoding="utf-8"), path=path.relative_to(ROOT).as_posix()))
    return violations


if __name__ == "__main__":
    errors = check()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise SystemExit(1)
    print("adoption claim lint: OK")
