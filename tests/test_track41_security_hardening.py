"""Track 41 security hardening contract tests."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACK41 = ROOT / "conductor" / "tracks" / "track41_sast_security_20260626"


def test_track41_artifacts_exist() -> None:
    """Track 41 should ship the expected SAST and secrets-scanning artifacts."""
    expected = [
        ROOT / ".bandit",
        ROOT / ".github" / "SECURITY.md",
        ROOT / ".github" / "dependabot.yml",
        ROOT / ".pre-commit-config.yaml",
        ROOT / ".secrets.baseline",
        ROOT / "scripts" / "check_dependency_security.py",
        TRACK41 / "index.md",
        TRACK41 / "metadata.json",
        TRACK41 / "plan.md",
        TRACK41 / "spec.md",
    ]

    assert [path for path in expected if not path.is_file()] == []


def test_track41_registry_and_plan_are_in_sync() -> None:
    """Track 41 should be registered and marked in progress."""
    registry = (ROOT / "conductor" / "tracks.md").read_text(encoding="utf-8")
    metadata = json.loads((TRACK41 / "metadata.json").read_text(encoding="utf-8"))
    plan = (TRACK41 / "plan.md").read_text(encoding="utf-8")
    security_policy = (ROOT / ".github" / "SECURITY.md").read_text(encoding="utf-8")

    assert "Track 41: SAST, Secrets Detection & Security Hardening" in registry
    assert "./conductor/tracks/track41_sast_security_20260626/" in registry
    assert metadata["track_id"] == "track41_sast_security_20260626"
    assert metadata["status"] == "complete"
    assert "Bandit" in plan
    assert "Semgrep" in plan
    assert "detect-secrets" in plan
    assert "Reporting a Vulnerability" in security_policy


def test_track41_security_wiring_references_expected_commands() -> None:
    """The CI and local security entry points should reference the new scans."""
    ci_workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    pre_commit = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    baseline = (ROOT / ".secrets.baseline").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    pixi = (ROOT / "pixi.toml").read_text(encoding="utf-8")
    pixi_toml = tomllib.loads(pixi)

    assert "Static application security testing" in ci_workflow
    assert "bandit -c .bandit -r src/nlp_policy_nz/ -lll -iii" in ci_workflow
    assert "semgrep scan --config p/python --severity WARNING --error --metrics=off" in ci_workflow
    assert "security-sast" in makefile
    assert "security-secrets" in makefile
    assert "detect-secrets" in pre_commit
    assert "plugins_used" in baseline
    assert "bandit>=1.8.3" in pyproject
    assert "semgrep>=1.93.0" in pyproject
    assert "detect-secrets>=1.5.0" in pyproject
    assert 'bandit = ">=1.8.3"' in pixi
    assert "semgrep" in pixi_toml["feature"]["security"]["pypi-dependencies"]
    assert 'detect-secrets = ">=1.5.0"' in pixi
