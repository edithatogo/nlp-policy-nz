"""API layer for nlp-policy-nz.

Exports both the FastAPI inference server and the public pipeline API.
"""
from nlp_policy_nz.api.server import app
from nlp_policy_nz.pipeline_api import process_hansard, process_legislation, search_similar

__all__ = [
    "app",
    "process_hansard",
    "process_legislation",
    "search_similar",
]