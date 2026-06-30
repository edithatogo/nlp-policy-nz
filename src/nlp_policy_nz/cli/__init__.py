"""CLI Module.

Command-line interface for interacting with the NLP pipeline, including
batch processing, interactive queries, and pipeline configuration commands.
"""

from __future__ import annotations

from nlp_policy_nz.cli.main import main

__all__: list[str] = [
    "main",
]
