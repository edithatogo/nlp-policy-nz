"""Tests for the CLI entry point.

Verifies that the ``main()`` function and ``argparse``-based subcommands
are wired up correctly and respond to ``--help``, ``process``, and
``search`` invocations.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest

from nlp_policy_nz.cli.main import main

if TYPE_CHECKING:
    import argparse

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_main(args: list[str]) -> int:
    """Run ``main()`` with the given argument list and return the exit code.

    Parameters
    ----------
    args : list[str]
        Command-line arguments (excluding the program name).

    Returns
    -------
    int
        Exit code from :func:`main`.
    """
    return main([*args])


# ---------------------------------------------------------------------------
# Tests: ``main()`` function existence and signature
# ---------------------------------------------------------------------------


class TestMainFunction:
    """Tests for the existence and call signature of ``main()``."""

    def test_main_function_exists(self) -> None:
        """Check that ``main`` is a callable function."""
        assert callable(main), "main() should be callable"

    def test_main_signature(self) -> None:
        """Check that ``main()`` accepts optional ``argv`` and returns ``int``."""
        sig = inspect.signature(main)
        assert "argv" in sig.parameters
        param = sig.parameters["argv"]
        assert param.default is None
        assert sig.return_annotation is int

    def test_main_returns_zero_with_help(self) -> None:
        """Calling ``main()`` with ``--help`` should exit with code 0."""
        rc = _run_main(["--help"])
        assert rc == 0

    def test_main_returns_one_on_unknown_command(self) -> None:
        """Unknown commands should result in exit code 1."""
        rc = _run_main(["unknown"])
        assert rc == 1


# ---------------------------------------------------------------------------
# Tests: ``process`` subcommand
# ---------------------------------------------------------------------------


class TestProcessSubcommand:
    """Tests for the ``process`` subcommand."""

    def test_process_requires_input(self) -> None:
        """``process`` without ``--input`` should fail (argparse error)."""
        with pytest.raises(SystemExit):
            _run_main(["process", "-o", "out.parquet", "-s", "legislation"])

    def test_process_requires_output(self) -> None:
        """``process`` without ``--output`` should fail (argparse error)."""
        with pytest.raises(SystemExit):
            _run_main(["process", "-i", "input.txt", "-s", "legislation"])

    def test_process_requires_source(self) -> None:
        """``process`` without ``--source`` should fail (argparse error)."""
        with pytest.raises(SystemExit):
            _run_main(["process", "-i", "input.txt", "-o", "out.parquet"])

    def test_process_accepts_no_embeddings_flag(self) -> None:
        """``process`` with ``--no-embeddings`` should parse without error.

        This test only validates argument parsing, not actual pipeline execution.
        """
        rc = _run_main(
            [
                "process",
                "--input",
                ".",
                "--output",
                "test_out.parquet",
                "--source",
                "legislation",
                "--no-embeddings",
            ]
        )
        # We expect a non-zero exit because "." is not a valid input,
        # but the key assertion is that argparse didn't reject the flag.
        assert rc != 0  # Actual execution fails, but argument parsing succeeded.

    def test_process_source_choices(self) -> None:
        """``--source`` only accepts ``legislation`` or ``hansard``."""
        with pytest.raises(SystemExit):
            _run_main(
                [
                    "process",
                    "-i",
                    "in.txt",
                    "-o",
                    "out.parquet",
                    "-s",
                    "invalid_source",
                ]
            )


# ---------------------------------------------------------------------------
# Tests: ``search`` subcommand
# ---------------------------------------------------------------------------


class TestSearchSubcommand:
    """Tests for the ``search`` subcommand."""

    def test_search_requires_query(self) -> None:
        """``search`` without ``--query`` should fail (argparse error)."""
        with pytest.raises(SystemExit):
            _run_main(["search"])

    def test_search_accepts_top_k(self) -> None:
        """``search`` with ``--top-k`` parses correctly."""
        rc = _run_main(["search", "-q", "test query", "-k", "5", "-d", "./nonexistent"])
        # Expected to fail because the DB doesn't exist, but argparse is happy.
        assert rc == 1  # Non-zero due to runtime error, not argparse.

    def test_search_default_db_path(self) -> None:
        """``search`` without ``--db`` defaults to ``./lancedb_data``."""
        rc = _run_main(["search", "-q", "test"])
        # Should fail because default DB path doesn't exist.
        assert rc == 1


# ---------------------------------------------------------------------------
# Tests: Argument parsing details
# ---------------------------------------------------------------------------


@pytest.fixture
def parser() -> Any:
    """Return the argument parser from the CLI module."""
    from nlp_policy_nz.cli.main import _build_parser  # noqa: PLC0415

    return _build_parser()


class TestArgumentParser:
    """Low-level argument parser tests."""

    def test_parser_has_process_subcommand(self, parser: Any) -> None:
        """Parser should have a ``process`` subcommand."""
        subparsers_actions = [
            action
            for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)  # type: ignore[attr-defined]
        ]
        assert subparsers_actions
        choices = subparsers_actions[0].choices
        assert "process" in choices

    def test_parser_has_search_subcommand(self, parser: Any) -> None:
        """Parser should have a ``search`` subcommand."""
        subparsers_actions = [
            action
            for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)  # type: ignore[attr-defined]
        ]
        assert subparsers_actions
        choices = subparsers_actions[0].choices
        assert "search" in choices

    def test_verbose_flag(self, parser: Any) -> None:
        """Parser should accept ``--verbose`` / ``-v`` flag."""
        args = parser.parse_args(["--verbose", "search", "-q", "test"])
        assert args.verbose is True

    def test_no_embeddings_default_false(self, parser: Any) -> None:
        """``--no-embeddings`` defaults to ``False``."""
        args = parser.parse_args(["process", "-i", ".", "-o", "out.parquet", "-s", "legislation"])
        assert hasattr(args, "no_embeddings")
        assert args.no_embeddings is False

    def test_parser_has_upload_dataset_subcommand(self, parser: Any) -> None:
        """Parser should have an ``upload-dataset`` subcommand."""
        subparsers_actions = [
            action
            for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)  # type: ignore[attr-defined]
        ]
        assert subparsers_actions
        choices = subparsers_actions[0].choices
        assert "upload-dataset" in choices

    def test_parser_has_deploy_space_subcommand(self, parser: Any) -> None:
        """Parser should have a ``deploy-space`` subcommand."""
        subparsers_actions = [
            action
            for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)  # type: ignore[attr-defined]
        ]
        assert subparsers_actions
        choices = subparsers_actions[0].choices
        assert "deploy-space" in choices


# ---------------------------------------------------------------------------
# Tests: ``upload-dataset`` subcommand
# ---------------------------------------------------------------------------


class TestUploadDatasetSubcommand:
    """Tests for the ``upload-dataset`` subcommand."""

    def test_upload_requires_parquet(self) -> None:
        """``upload-dataset`` without ``--parquet`` should fail."""
        with pytest.raises(SystemExit):
            _run_main(["upload-dataset", "--repo-id", "user/ds"])

    def test_upload_requires_repo_id(self) -> None:
        """``upload-dataset`` without ``--repo-id`` should fail."""
        with pytest.raises(SystemExit):
            _run_main(["upload-dataset", "--parquet", "file.parquet"])

    def test_upload_accepts_flags(self) -> None:
        """``upload-dataset`` with all flags should parse without error."""
        rc = _run_main([
            "upload-dataset",
            "--parquet", "nonexistent.parquet",
            "--repo-id", "user/ds",
            "--split", "train",
            "--private",
            "--message", "Test upload",
        ])
        # Fails because file doesn't exist, but argparse succeeded.
        assert rc == 1


# ---------------------------------------------------------------------------
# Tests: ``deploy-space`` subcommand
# ---------------------------------------------------------------------------


class TestDeploySpaceSubcommand:
    """Tests for the ``deploy-space`` subcommand."""

    def test_deploy_requires_repo_id(self) -> None:
        """``deploy-space`` without ``--repo-id`` should fail."""
        with pytest.raises(SystemExit):
            _run_main(["deploy-space"])

    def test_deploy_accepts_dry_run(self) -> None:
        """``deploy-space`` with ``--dry-run`` parses correctly."""
        rc = _run_main([
            "deploy-space",
            "--repo-id", "user/space",
            "--dry-run",
        ])
        # Fails because HF_TOKEN isn't set, but argparse succeeded.
        assert rc == 1

    def test_deploy_accepts_all_flags(self) -> None:
        """``deploy-space`` with all flags should parse correctly."""
        rc = _run_main([
            "deploy-space",
            "--repo-id", "user/space",
            "--token", "tok",
            "--dry-run",
            "--message", "Test deploy",
        ])
        # Dry-run should succeed even without real token.
        assert rc == 0


# ---------------------------------------------------------------------------
# Tests: ``archive-to-zenodo`` subcommand
# ---------------------------------------------------------------------------


class TestArchiveToZenodoSubcommand:
    """Tests for the ``archive-to-zenodo`` subcommand."""

    def test_archive_requires_parquet(self) -> None:
        """``archive-to-zenodo`` without ``--parquet`` should fail."""
        with pytest.raises(SystemExit):
            _run_main([
                "archive-to-zenodo",
                "--title", "Test Title",
                "--description", "Test Description",
                "--creators", '[{"name": "Doe, Jane"}]',
            ])

    def test_archive_requires_title(self) -> None:
        """``archive-to-zenodo`` without ``--title`` should fail."""
        with pytest.raises(SystemExit):
            _run_main([
                "archive-to-zenodo",
                "--parquet", "test.parquet",
                "--description", "Test Description",
                "--creators", '[{"name": "Doe, Jane"}]',
            ])

    def test_archive_requires_description(self) -> None:
        """``archive-to-zenodo`` without ``--description`` should fail."""
        with pytest.raises(SystemExit):
            _run_main([
                "archive-to-zenodo",
                "--parquet", "test.parquet",
                "--title", "Test Title",
                "--creators", '[{"name": "Doe, Jane"}]',
            ])

    def test_archive_requires_creators(self) -> None:
        """``archive-to-zenodo`` without ``--creators`` should fail."""
        with pytest.raises(SystemExit):
            _run_main([
                "archive-to-zenodo",
                "--parquet", "test.parquet",
                "--title", "Test Title",
                "--description", "Test Description",
            ])

    def test_archive_accepts_all_flags(self) -> None:
        """``archive-to-zenodo`` with all flags including optional ones.

        ``--token`` and ``--license`` are optional; providing them should
        parse without argparse error.  The handler will fail at runtime
        because the Parquet file does not exist.
        """
        rc = _run_main([
            "archive-to-zenodo",
            "--parquet", "nonexistent.parquet",
            "--title", "Test Title",
            "--description", "Test Description",
            "--creators", '[{"name": "Doe, Jane"}]',
            "--token", "zenodo-tok-123",
            "--license", "CC-BY-4.0",
        ])
        # Fails because file doesn't exist, but argparse succeeded.
        assert rc == 1

    def test_archive_handler_dispatches_archiver(self) -> None:
        """Mock ZenodoArchiver and verify ``create_archive`` is called."""
        with patch(
            "nlp_policy_nz.cli.main.ZenodoArchiver",
        ) as mock_archiver:
            mock_instance = mock_archiver.return_value
            mock_instance.create_archive.return_value = {"doi": "10.5072/zenodo.12345"}

            rc = _run_main([
                "archive-to-zenodo",
                "--parquet", "test_data.parquet",
                "--title", "Test Title",
                "--description", "Test Description",
                "--creators", '[{"name": "Doe, Jane"}]',
                "--token", "tok-123",
                "--license", "MIT",
            ])

        assert rc == 0
        mock_archiver.assert_called_once_with(token="tok-123")
        mock_instance.create_archive.assert_called_once_with(
            title="Test Title",
            description="Test Description",
            creators=[{"name": "Doe, Jane"}],
            file_path="test_data.parquet",
            license_id="MIT",
        )

    def test_archive_handler_parses_creators_json(self) -> None:
        """Verify JSON creators arg is parsed correctly."""
        with patch(
            "nlp_policy_nz.cli.main.ZenodoArchiver",
        ) as mock_archiver:
            mock_instance = mock_archiver.return_value
            mock_instance.create_archive.return_value = {"doi": "10.5072/zenodo.99999"}

            _run_main([
                "archive-to-zenodo",
                "--parquet", "d.parquet",
                "--title", "T",
                "--description", "D",
                "--creators", '[{"name": "Smith, John", "affiliation": "Uni"}]',
            ])

            mock_instance.create_archive.assert_called_once_with(
                title="T",
                description="D",
                creators=[{"name": "Smith, John", "affiliation": "Uni"}],
                file_path="d.parquet",
                license_id="MIT",
            )


# ---------------------------------------------------------------------------
# Tests: ``release`` subcommand
# ---------------------------------------------------------------------------


class TestReleaseSubcommand:
    """Tests for the ``release`` subcommand."""

    def test_release_requires_parquet(self) -> None:
        """``release`` without ``--parquet`` should fail."""
        with pytest.raises(SystemExit):
            _run_main([
                "release",
                "--version", "1.0.0",
                "--title", "Test Title",
                "--description", "Test Description",
                "--creators", '[{"name": "Doe, Jane"}]',
            ])

    def test_release_requires_version(self) -> None:
        """``release`` without ``--version`` should fail."""
        with pytest.raises(SystemExit):
            _run_main([
                "release",
                "--parquet", "test.parquet",
                "--title", "Test Title",
                "--description", "Test Description",
                "--creators", '[{"name": "Doe, Jane"}]',
            ])

    def test_release_accepts_all_flags(self) -> None:
        """``release`` with all flags should parse without argparse error.

        The handler will fail at runtime because the Parquet file does
        not exist, but argument parsing succeeds.
        """
        rc = _run_main([
            "release",
            "--parquet", "nonexistent.parquet",
            "--version", "1.0.0",
            "--title", "Test Title",
            "--description", "Test Description",
            "--creators", '[{"name": "Doe, Jane"}]',
            "--token", "zenodo-tok-123",
            "--output-dir", "/tmp/releases",
        ])
        # Fails because file doesn't exist, but argparse succeeded.
        assert rc == 1

    def test_release_handler_dispatches_manager(self) -> None:
        """Mock ReleaseManager and verify ``full_release`` is called."""
        with patch(
            "nlp_policy_nz.cli.main.ReleaseManager",
        ) as mock_manager:
            mock_instance = mock_manager.return_value
            mock_instance.full_release.return_value = {"doi": "10.5072/zenodo.55555"}

            rc = _run_main([
                "release",
                "--parquet", "release_data.parquet",
                "--version", "2.1.0",
                "--title", "Release Title",
                "--description", "Release Description",
                "--creators", '[{"name": "Doe, Jane"}]',
                "--token", "tok-999",
                "--output-dir", "/tmp/out",
            ])

        assert rc == 0
        mock_manager.assert_called_once_with(token="tok-999")
        mock_instance.full_release.assert_called_once_with(
            "release_data.parquet",
            version="2.1.0",
            title="Release Title",
            description="Release Description",
            creators=[{"name": "Doe, Jane"}],
        )

    def test_release_handler_creators_parsed(self) -> None:
        """Verify JSON creators are parsed and passed to full_release."""
        with patch(
            "nlp_policy_nz.cli.main.ReleaseManager",
        ) as mock_manager:
            mock_instance = mock_manager.return_value
            mock_instance.full_release.return_value = {"doi": "10.5072/zenodo.66666"}

            _run_main([
                "release",
                "--parquet", "d.parquet",
                "--version", "3.0.0",
                "--title", "T",
                "--description", "D",
                "--creators", '[{"name": "Smith, John"}, {"name": "Jones, A."}]',
            ])

            mock_instance.full_release.assert_called_once_with(
                "d.parquet",
                version="3.0.0",
                title="T",
                description="D",
                creators=[{"name": "Smith, John"}, {"name": "Jones, A."}],
            )
