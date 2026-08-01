import subprocess
from unittest import mock

import pytest

from nlp_policy_nz.governance.commit_message import (
    _first_meaningful_line,
    _git_subjects,
    lint_commit_message,
    lint_commit_messages,
    load_commit_messages_from_git,
)


def test_first_meaningful_line():
    assert _first_meaningful_line("test") == "test"
    assert _first_meaningful_line("  test  ") == "test"
    assert _first_meaningful_line("# comment\ntest") == "test"
    assert _first_meaningful_line("\n\ntest\nline 2") == "test"
    assert _first_meaningful_line("# comment 1\n# comment 2\ntest") == "test"
    assert _first_meaningful_line("") is None
    assert _first_meaningful_line("# comment only") is None
    assert _first_meaningful_line("   \n  \n") is None


def test_lint_commit_message():
    # Valid messages
    assert lint_commit_message("feat: add something") == []
    assert lint_commit_message("fix(scope): fix bug") == []
    assert lint_commit_message("docs(readme)!: update docs") == []
    assert lint_commit_message("test: add test\n\nbody") == []
    assert lint_commit_message("chore(deps): update dependencies") == []
    assert lint_commit_message("build: update build script") == []
    assert lint_commit_message("ci: update ci") == []
    assert lint_commit_message("perf: improve performance") == []
    assert lint_commit_message("style: format code") == []
    assert lint_commit_message("refactor: refactor something") == []

    # Invalid messages
    assert lint_commit_message("") == ["commit message is empty"]
    assert lint_commit_message("# comment") == ["commit message is empty"]

    invalid_format_error = [
        "commit message must use conventional format "
        "`type(scope): description` with an allowed type"
    ]
    assert lint_commit_message("Add something") == invalid_format_error
    assert lint_commit_message("feat : add something") == invalid_format_error
    assert lint_commit_message("unknown: something") == invalid_format_error
    assert lint_commit_message("feat(scope) : something") == invalid_format_error


def test_lint_commit_messages():
    messages = [
        "feat: add something",
        "Add something",
        "# comment\nfix(scope): bug",
        "",
    ]

    errors = lint_commit_messages(messages)

    assert len(errors) == 2
    assert "Add something: commit message must use conventional format" in errors[0]
    assert "<empty>: commit message is empty" in errors[1]


@mock.patch("subprocess.run")
def test_git_subjects(mock_run):
    mock_run.return_value.stdout = "feat: one\nfix: two\n\n"

    subjects = _git_subjects("HEAD~1..HEAD")

    assert subjects == ["feat: one", "fix: two"]
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0] == ["git", "log", "--no-merges", "--format=%s", "HEAD~1..HEAD"]
    assert kwargs["check"] is True
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True


@mock.patch("subprocess.run")
def test_git_subjects_fallback(mock_run):
    # Setup first call to fail, second call (fallback) to succeed
    def side_effect(*args, **kwargs):
        if len(args[0]) > 4 and args[0][4] == "bad_range":
            raise subprocess.CalledProcessError(1, args[0])
        mock_result = mock.Mock()
        mock_result.stdout = "feat: single\n"
        return mock_result

    mock_run.side_effect = side_effect

    # Test fallback works when enabled
    subjects = _git_subjects("bad_range", fallback_single=True)
    assert subjects == ["feat: single"]
    assert mock_run.call_count == 2
    assert mock_run.call_args_list[1][0][0] == ["git", "log", "-1", "--format=%s"]

    # Test failure when fallback disabled
    mock_run.reset_mock()
    with pytest.raises(subprocess.CalledProcessError):
        _git_subjects("bad_range", fallback_single=False)


@mock.patch("os.environ.get")
@mock.patch("nlp_policy_nz.governance.commit_message._git_subjects")
def test_load_commit_messages_from_git(mock_git_subjects, mock_env_get):
    # Test with GITHUB_BASE_REF
    mock_env_get.return_value = "main"
    mock_git_subjects.return_value = ["feat: one"]

    subjects = load_commit_messages_from_git()

    assert subjects == ["feat: one"]
    mock_env_get.assert_called_with("GITHUB_BASE_REF", "")
    mock_git_subjects.assert_called_with("origin/main..HEAD")

    # Test without GITHUB_BASE_REF
    mock_env_get.reset_mock()
    mock_git_subjects.reset_mock()
    mock_env_get.return_value = ""
    mock_git_subjects.return_value = ["feat: one"]

    subjects = load_commit_messages_from_git()

    assert subjects == ["feat: one"]
    mock_git_subjects.assert_called_with("HEAD~1..HEAD", fallback_single=True)
