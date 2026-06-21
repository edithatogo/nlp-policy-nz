"""Contract tests for the repository mirror GitHub Actions workflow."""

from pathlib import Path

WORKFLOW_PATH = Path(".github/workflows/mirror_sync.yml")


def test_mirror_sync_triggers_on_canonical_branch_pushes() -> None:
    """Mirror sync must run for canonical branch pushes and manual dispatch."""
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "push:" in workflow
    assert "branches: [main, master]" in workflow
    assert "workflow_dispatch:" in workflow


def test_mirror_sync_supports_gitlab_and_codeberg_targets() -> None:
    """The workflow must configure separate GitLab and Codeberg mirrors."""
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "GITLAB_MIRROR_URL" in workflow
    assert "CODEBERG_MIRROR_URL" in workflow
    assert 'mirror_to_remote gitlab "$GITLAB_MIRROR_URL"' in workflow
    assert 'mirror_to_remote codeberg "$CODEBERG_MIRROR_URL"' in workflow
    assert 'git remote add "$remote_name" "$mirror_url"' in workflow


def test_mirror_sync_bypasses_when_credentials_are_empty() -> None:
    """Empty URL or SSH key secrets must skip instead of failing the job."""
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert '[ -z "$GIT_MIRROR_SSH_PRIVATE_KEY" ]' in workflow
    assert "No mirror URLs configured; skipping mirror sync." in workflow
    assert "Mirror SSH key is not set; skipping mirror sync." in workflow
