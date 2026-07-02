"""Track 50 public sector compliance and accessibility contract tests."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACK50 = ROOT / "conductor" / "tracks" / "track50_compliance_accessibility_20260626"


def test_track50_repo_artifacts_exist() -> None:
    """Track 50 should ship the privacy policy, a11y workflow, and Space changes."""
    expected = [
        ROOT / "PRIVACY.md",
        ROOT / ".github" / "workflows" / "a11y-scan.yml",
        TRACK50 / "index.md",
        TRACK50 / "metadata.json",
        TRACK50 / "plan.md",
        TRACK50 / "screen_reader_audit.md",
        TRACK50 / "spec.md",
        ROOT / "spaces" / "app.py",
    ]

    assert [path for path in expected if not path.is_file()] == []


def test_track50_registry_and_plan_are_linked() -> None:
    """Track 50 should be registered and marked complete."""
    registry = (ROOT / "conductor" / "tracks.md").read_text(encoding="utf-8")
    metadata = json.loads((TRACK50 / "metadata.json").read_text(encoding="utf-8"))
    plan = (TRACK50 / "plan.md").read_text(encoding="utf-8")
    audit = (TRACK50 / "screen_reader_audit.md").read_text(encoding="utf-8")
    privacy = (ROOT / "PRIVACY.md").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "a11y-scan.yml").read_text(encoding="utf-8")
    space = (ROOT / "spaces" / "app.py").read_text(encoding="utf-8")

    assert "Track 50: Public Sector Compliance & Accessibility" in registry
    assert "./conductor/tracks/track50_compliance_accessibility_20260626/" in registry
    assert metadata["track_id"] == "track50_compliance_accessibility_20260626"
    assert metadata["status"] == "complete"
    assert "WCAG 2.1 AA" in plan or "WCAG 2.1 AA" in privacy
    assert "NVDA" in audit
    assert "VoiceOver" in audit
    assert "external launch gate" in audit
    assert "privacy@nlp-policy-nz.example" in privacy
    assert "axe" in workflow.lower()
    assert "HF_SPACE_URL" in workflow
    assert "privacy-footer" in space
    assert "focus-visible" in space
    assert "main-content" in space
