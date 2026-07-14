"""Completion and man-page helpers for the CLI."""

# ruff: noqa: SLF001

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SUPPORTED_SHELLS = ("bash", "zsh", "pwsh")


def _subcommand_names(parser: argparse.ArgumentParser) -> list[str]:
    names: list[str] = []
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):  # type: ignore[attr-defined]
            names.extend(action.choices)
    return sorted(set(names))


def build_completion_script(parser: argparse.ArgumentParser, shell: str) -> str:
    """Render a simple shell completion script."""
    commands = " ".join(_subcommand_names(parser))
    shell = shell.lower()
    if shell == "bash":
        return f"""# bash completion for nlp-policy-nz
_nlp_policy_nz_complete() {{
    local cur prev
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
    case "$prev" in
        nlp-policy-nz) COMPREPLY=( $(compgen -W "{commands}" -- "$cur") ) ;;
        completion) COMPREPLY=( $(compgen -W "install manpage" -- "$cur") ) ;;
        --source) COMPREPLY=( $(compgen -W "legislation hansard" -- "$cur") ) ;;
    esac
    return 0
}}
complete -F _nlp_policy_nz_complete nlp-policy-nz
"""
    if shell == "zsh":
        return f"""#compdef nlp-policy-nz
_nlp_policy_nz_complete() {{
    local -a commands
    commands=({commands})
    _describe 'command' commands
}}
compdef _nlp_policy_nz_complete nlp-policy-nz
"""
    if shell == "pwsh":
        return f"""Register-ArgumentCompleter -CommandName nlp-policy-nz -ScriptBlock {{
    param($wordToComplete, $commandAst, $cursorPosition)
    @('{commands}'.Split(' ')) | Where-Object {{ $_ -like "$wordToComplete*" }} | ForEach-Object {{
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }}
}}
"""
    msg = f"Unsupported shell: {shell}"
    raise ValueError(msg)


def build_manpage(parser: argparse.ArgumentParser) -> str:
    """Render a minimal roff man page from an argparse parser."""
    help_text = parser.format_help().strip()
    return f""".TH NLP-POLICY-NZ 1
.SH NAME
nlp-policy-nz \\- NLP preprocessing pipeline CLI
.SH SYNOPSIS
.B nlp-policy-nz
[OPTIONS] COMMAND [ARGS...]
.SH DESCRIPTION
{help_text}
"""


def write_text_output(text: str, output: str | Path | None) -> None:
    """Write generated text to a file or stdout."""
    if output is None:
        sys.stdout.write(text)
        return
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


__all__ = [
    "SUPPORTED_SHELLS",
    "build_completion_script",
    "build_manpage",
    "write_text_output",
]
