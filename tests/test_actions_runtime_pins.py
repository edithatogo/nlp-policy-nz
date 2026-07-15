from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
APPROVED = {
    "actions/checkout": "9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0",
    "actions/upload-artifact": "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a",
    "actions/download-artifact": "3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c",
}


def test_checkout_and_artifact_actions_use_approved_node24_commit_pins() -> None:
    references: list[tuple[Path, str, str]] = []
    pattern = re.compile(
        r"uses:\s+(actions/(?:checkout|upload-artifact|download-artifact))@([^\s#]+)"
    )
    for workflow in sorted((ROOT / ".github/workflows").glob("*.y*ml")):
        for action, revision in pattern.findall(workflow.read_text(encoding="utf-8")):
            references.append((workflow, action, revision))

    assert references
    failures = [
        f"{path.relative_to(ROOT)}: {action}@{revision}"
        for path, action, revision in references
        if APPROVED[action] != revision
    ]
    assert failures == []
