"""Governance decision constants and Haystack availability guards."""

from __future__ import annotations

import sys
from importlib.util import find_spec

TRACK_ID = "track99_haystack_governance_orchestration_20260728"

ALLOWED_CONTEXTS: tuple[str, ...] = (
    "typed DAG orchestration for auditability",
    "legal indexing shell with structure preservation",
    "extractive span QA with verifiable offsets",
    "local ExactMatch and SAS-proxy evaluation",
    "onshore and air-gap deployments",
)

BANNED_CONTEXTS: tuple[str, ...] = (
    "required runtime dependency for default CI or CLI paths",
    "replacement for spaCy helpers, LanceDBAdapter, or PipelineRecord",
    "generative cloud defaults on restricted or sovereign data",
    "LLM FaithfulnessEvaluator as promotion or OIA evidence oracle",
)

FAITHFULNESS_EVALUATOR_AUTHORITATIVE = False
GENERATIVE_DEFAULT_ALLOWED = False

_HAYSTACK_MODULE_PREFIXES = ("haystack", "haystack_ai")


def haystack_available() -> bool:
    """Return True when the optional haystack-ai package is installed."""
    return find_spec("haystack") is not None


def assert_haystack_not_default_runtime() -> None:
    """Assert that importing nlp_policy_nz does not eagerly load haystack modules."""
    import nlp_policy_nz  # noqa: F401, PLC0415

    loaded = [
        name
        for name in sys.modules
        if any(name == prefix or name.startswith(f"{prefix}.") for prefix in _HAYSTACK_MODULE_PREFIXES)
    ]
    if loaded:
        msg = f"haystack modules loaded on default import path: {loaded}"
        raise AssertionError(msg)
