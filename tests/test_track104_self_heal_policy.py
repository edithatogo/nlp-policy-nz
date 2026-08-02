"""Tests for Track 104 self-heal and experimental-runtime policy."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_self_heal_requires_explicit_label():
    workflow = (ROOT / ".github/workflows/self-healing-ci.yml").read_text(encoding="utf-8")

    assert "self-heal-approved" in workflow
    assert "steps.approval.outputs.approved" in workflow


def test_ci_policy_documents_experimental_and_dependency_ownership():
    policy = (ROOT / "docs/ci-policy.md").read_text(encoding="utf-8")

    assert "experimental Python probes are informative" in policy
    assert "Dependabot owns" in policy
    assert "Renovate" in policy
