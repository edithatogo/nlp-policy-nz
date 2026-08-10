"""Offline candidate projection for the Track 105 optional spike.

This module deliberately performs no inference. It turns supplied, already
reviewed fields into a canonical ``PipelineRecord`` while marking the result
as a non-authoritative candidate through its provenance fields.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from nlp_policy_nz.storage import PipelineRecord


def build_candidate_record(
    *,
    doc_id: str,
    corpus_source: str,
    raw_text: str,
    extracted: Mapping[str, Any] | None = None,
) -> PipelineRecord:
    """Build a deterministic candidate record from supplied values.

    ``extracted`` is treated as untrusted input: only known list-shaped fields
    are copied, and label provenance is always ``"candidate"``. No model,
    network, publication, or promotion path is invoked.
    """
    if not doc_id or not corpus_source:
        raise ValueError("doc_id and corpus_source are required")
    if not isinstance(raw_text, str):
        raise TypeError("raw_text must be a string")

    values = extracted or {}

    def list_of_strings(name: str) -> list[str]:
        value = values.get(name, [])
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            raise TypeError(f"{name} must be a sequence of strings")
        if not all(isinstance(item, str) for item in value):
            raise TypeError(f"{name} must be a sequence of strings")
        return list(value)

    return PipelineRecord(
        doc_id=doc_id,
        corpus_source=corpus_source,
        raw_text=raw_text,
        cleaned_tokens=list_of_strings("cleaned_tokens"),
        nz_act_citations=list_of_strings("nz_act_citations"),
        te_reo_terms=list_of_strings("te_reo_terms"),
        legal_effect=values.get("legal_effect"),
        argument_label_source="candidate",
        stance=values.get("stance"),
        stance_label_source="candidate",
    )


__all__ = ["build_candidate_record"]
