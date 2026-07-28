"""Optional Haystack-style governance orchestration helpers."""

from __future__ import annotations

from nlp_policy_nz.orchestration.haystack.decision import (
    ALLOWED_CONTEXTS,
    BANNED_CONTEXTS,
    FAITHFULNESS_EVALUATOR_AUTHORITATIVE,
    GENERATIVE_DEFAULT_ALLOWED,
    TRACK_ID,
    assert_haystack_not_default_runtime,
    haystack_available,
)
from nlp_policy_nz.orchestration.haystack.evaluation import (
    emit_scorecard,
    exact_match_score,
    sas_proxy_score,
)
from nlp_policy_nz.orchestration.haystack.pipelines import (
    GENERATIVE_COMPONENTS_FORBIDDEN,
    build_indexing_pipeline,
    build_restricted_query_pipeline,
    extractive_qa,
    run_indexing_pipeline,
)
from nlp_policy_nz.orchestration.haystack.types import ExtractedSpanAnswer, GovernanceDocument

__all__ = [
    "ALLOWED_CONTEXTS",
    "BANNED_CONTEXTS",
    "FAITHFULNESS_EVALUATOR_AUTHORITATIVE",
    "GENERATIVE_COMPONENTS_FORBIDDEN",
    "GENERATIVE_DEFAULT_ALLOWED",
    "TRACK_ID",
    "ExtractedSpanAnswer",
    "GovernanceDocument",
    "assert_haystack_not_default_runtime",
    "build_indexing_pipeline",
    "build_restricted_query_pipeline",
    "emit_scorecard",
    "exact_match_score",
    "extractive_qa",
    "haystack_available",
    "run_indexing_pipeline",
    "sas_proxy_score",
]
