"""Track 39 governance contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.governance.commit_message import lint_commit_message, lint_commit_messages

ROOT = Path(__file__).resolve().parents[1]
TRACK39 = ROOT / "conductor" / "tracks" / "track39_governance_contributing_20260626"


def test_track39_repo_governance_artifacts_exist() -> None:
    """Track 39 should ship the governance and maintenance files."""
    expected = [
        ROOT / "CONTRIBUTING.md",
        ROOT / "CODE_OF_CONDUCT.md",
        ROOT / "SECURITY.md",
        ROOT / ".github" / "CODEOWNERS",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.md",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.md",
        ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md",
        ROOT / ".github" / "release-drafter.yml",
        ROOT / ".github" / "workflows" / "release-drafter.yml",
        ROOT / ".github" / "workflows" / "stale.yml",
        ROOT / "scripts" / "check_commit_message.py",
        TRACK39 / "index.md",
        TRACK39 / "metadata.json",
        TRACK39 / "plan.md",
        TRACK39 / "spec.md",
    ]

    assert [path for path in expected if not path.is_file()] == []


def test_track39_registry_metadata_and_plan_are_linked() -> None:
    """The registry and track metadata should identify Track 39 as in progress."""
    registry = (ROOT / "conductor" / "tracks.md").read_text(encoding="utf-8")
    metadata = json.loads((TRACK39 / "metadata.json").read_text(encoding="utf-8"))
    plan = (TRACK39 / "plan.md").read_text(encoding="utf-8")
    spec = (TRACK39 / "spec.md").read_text(encoding="utf-8")

    assert "Track 39: Repository Governance & Contribution Framework" in registry
    assert "./conductor/tracks/track39_governance_contributing_20260626/" in registry
    assert metadata["track_id"] == "track39_governance_contributing_20260626"
    assert metadata["status"] in {"planned", "in_progress", "complete"}
    assert "contribution framework" in spec.lower()
    assert "commit message linting" in spec.lower()
    assert "CONTRIBUTING.md" in plan
    assert "CODEOWNERS" in plan
    assert "release-drafter" in plan


def test_track39_governance_files_reference_repo_conventions() -> None:
    """Governance docs should describe the repo's actual workflow."""
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    codeowners = (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    pr_template = (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
    release_drafter = (ROOT / ".github" / "release-drafter.yml").read_text(encoding="utf-8")
    stale_workflow = (ROOT / ".github" / "workflows" / "stale.yml").read_text(encoding="utf-8")
    release_workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    ci_workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    pre_commit = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    assert "pixi install" in contributing
    assert "pixi run check" in contributing
    assert "@edithatogo" in codeowners
    assert "/src/nlp_policy_nz/analysis/" in codeowners
    assert "quality gates" in pr_template.lower()
    assert "What's Changed" in release_drafter
    assert "track/39" in release_drafter
    assert "90" in stale_workflow
    assert "14" in stale_workflow
    assert "release_notes" in release_workflow
    assert "generate_release_notes" not in release_workflow
    assert "Commit message lint" in ci_workflow
    assert "commit-msg" in pre_commit
    assert "check_commit_message.py" in pre_commit


def test_track39_commit_message_linting_accepts_conventional_messages() -> None:
    """The commit-message lint helper should accept conventional commits and reject others."""
    assert lint_commit_message("feat(governance): add contribution guide") == []
    assert lint_commit_message("fix: correct stale workflow") == []
    assert lint_commit_message("update docs") != []
    assert lint_commit_messages(["docs: add security policy", "bad message"]) != []
