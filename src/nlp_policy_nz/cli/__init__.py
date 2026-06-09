"""CLI Module.

Command-line interface for interacting with the NLP pipeline, including
batch processing, interactive queries, and pipeline configuration commands.
"""

from nlp_policy_nz.cli.main import main

__all__: list[str] = [
    "main",
]
