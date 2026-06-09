"""Tests for the CLI entry point.

Verifies that the ``main()`` function and ``argparse``-based subcommands
are wired up correctly and respond to ``--help``, ``process``, and
``search`` invocations.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any

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
