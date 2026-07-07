"""Completion and man-page helpers for the CLI."""

# ruff: noqa: SLF001

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

SUPPORTED_SHELLS = ("bash", "zsh", "pwsh")


def _subcommand_names(parser: argparse.ArgumentParser) -> list[str]:
    names: list[str] = []
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):  # type: ignore[attr-defined]
            names.extend(action.choices)
    return sorted(set(names))


def _subcommand_children(parser: argparse.ArgumentParser) -> dict[str, list[str]]:
    children: dict[str, list[str]] = {}
    for action in parser._actions:
        if not isinstance(action, argparse._SubParsersAction):  # type: ignore[attr-defined]
            continue
        for name, subparser in action.choices.items():
            nested = _subcommand_names(subparser)
            if nested:
                children[name] = nested
    return children


def _bash_case_line(parent: str, children: list[str]) -> str:
    options = " ".join(children)
    return f'        {parent}) COMPREPLY=( $(compgen -W "{options}" -- "$cur") ) ;;'


def build_completion_script(parser: argparse.ArgumentParser, shell: str) -> str:
    """Render a simple shell completion script."""
    commands = " ".join(_subcommand_names(parser))
    child_commands = _subcommand_children(parser)
    shell = shell.lower()
    if shell == "bash":
        nested_cases = "\n".join(
            _bash_case_line(parent, children) for parent, children in sorted(child_commands.items())
        )
        return f"""# bash completion for nlp-policy-nz
_nlp_policy_nz_complete() {{
    local cur prev
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
    case "$prev" in
        nlp-policy-nz) COMPREPLY=( $(compgen -W "{commands}" -- "$cur") ) ;;
{nested_cases}
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


def _capability_lines(capabilities: Iterable[Any]) -> str:
    lines = []
    for capability in capabilities:
        command_path = " ".join(getattr(capability, "command_path", ()))
        capability_id = getattr(capability, "capability_id", "")
        summary = getattr(capability, "summary", "")
        owner_module = getattr(capability, "owner_module", "")
        side_effect = getattr(capability, "side_effect", "")
        output_mode = getattr(capability, "output_mode", "none")
        lines.append(
            f".TP\n.B {command_path}\n{capability_id}\n{summary}\n"
            f"Owner: {owner_module}\nSide effect: {side_effect}\nOutput: {output_mode}\n"
        )
    return "".join(lines)


def build_manpage(
    parser: argparse.ArgumentParser,
    capabilities: Iterable[Any] | None = None,
) -> str:
    """Render a minimal roff man page from an argparse parser."""
    help_text = parser.format_help().strip()
    capabilities_text = _capability_lines(capabilities or ())
    return f""".TH NLP-POLICY-NZ 1
.SH NAME
nlp-policy-nz \\- NLP preprocessing pipeline CLI
.SH SYNOPSIS
.B nlp-policy-nz
[OPTIONS] COMMAND [ARGS...]
.SH DESCRIPTION
{help_text}
.SH CAPABILITIES
{capabilities_text}
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
