"""CLI Module.

Command-line interface for interacting with the NLP pipeline, including
batch processing, interactive queries, and pipeline configuration commands.
"""

from __future__ import annotations

__all__: list[str] = [
    "cli_capability_inventory",
    "cli_contract_summary",
    "main",
]


def __getattr__(name: str) -> object:
    """Lazily resolve the CLI entrypoint without importing the whole CLI stack."""
    if name in {"main", "cli_capability_inventory", "cli_contract_summary"}:
        from nlp_policy_nz.cli.main import main

        if name == "main":
            return main
        from nlp_policy_nz.cli.main import cli_capability_inventory, cli_contract_summary

        return {
            "cli_capability_inventory": cli_capability_inventory,
            "cli_contract_summary": cli_contract_summary,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
