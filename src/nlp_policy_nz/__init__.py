"""
nlp_policy_nz - SOTA shared core NLP pipeline for New Zealand legislation and Hansard corpora.

This package provides a modular NLP preprocessing pipeline for Aotearoa New Zealand's
legislative and parliamentary corpora, featuring Māori Language validation, syntactic
parsing, semantic analysis, efficient storage backends, and integrations for loading
datasets from external sources (Hugging Face Hub, Zenodo, etc.).
"""

__version__ = "0.1.0"

from nlp_policy_nz.api import process_legislation, process_hansard, search_similar

__all__: list[str] = [
    "process_legislation",
    "process_hansard",
    "search_similar",
]
