"""Tests for the Track 102 documentation claim gate."""

from scripts.check_adoption_claims import check, find_violations


def test_lint_rejects_empirical_claims_when_not_ready():
    violations = find_violations("This is a SOTA system.", path="README.md")

    assert violations


def test_repository_docs_pass_the_current_blocked_gate():
    assert check() == []
