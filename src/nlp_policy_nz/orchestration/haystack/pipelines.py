"""Governance indexing and extractive QA pipelines."""

from __future__ import annotations

import re
from typing import Any

from nlp_policy_nz.orchestration.haystack.components import (
    DocumentWriter,
    InMemoryDocumentStore,
    LegalStructureSplitter,
    ProvenanceStepRecorder,
    RightsGateComponent,
    SpaCyEnricher,
)
from nlp_policy_nz.orchestration.haystack.decision import GENERATIVE_DEFAULT_ALLOWED
from nlp_policy_nz.orchestration.haystack.types import ExtractedSpanAnswer, GovernanceDocument

GENERATIVE_COMPONENTS_FORBIDDEN = True
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_SENTENCE_PATTERN = re.compile(r"[^.!?\n]+[.!?\n]?")


def _tokenize(text: str) -> set[str]:
    return {token.lower() for token in _TOKEN_PATTERN.findall(text)}


def build_indexing_pipeline(
    *,
    writer: DocumentWriter | None = None,
    rights_gate: RightsGateComponent | None = None,
    splitter: LegalStructureSplitter | None = None,
    enricher: SpaCyEnricher | None = None,
    provenance: ProvenanceStepRecorder | None = None,
) -> dict[str, Any]:
    """Wire rights gate, splitter, enricher, and writer components."""
    return {
        "rights_gate": rights_gate or RightsGateComponent(),
        "splitter": splitter or LegalStructureSplitter(),
        "enricher": enricher or SpaCyEnricher(),
        "writer": writer or DocumentWriter(store=InMemoryDocumentStore()),
        "provenance": provenance or ProvenanceStepRecorder(),
    }


def run_indexing_pipeline(
    documents: list[GovernanceDocument],
    *,
    pipeline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the offline indexing pipeline on governance documents."""
    selected = pipeline or build_indexing_pipeline()
    provenance: ProvenanceStepRecorder = selected["provenance"]
    provenance.run(step_name="rights_gate")
    gated = selected["rights_gate"].run(documents=documents)
    if gated.get("error"):
        return {"written_count": 0, "error": gated["error"], "documents": []}

    provenance.run(step_name="legal_structure_split")
    split = selected["splitter"].run(documents=gated["documents"])
    provenance.run(step_name="spacy_enrich")
    enriched = selected["enricher"].run(documents=split["documents"])
    provenance.run(step_name="document_write")
    written = selected["writer"].run(documents=enriched["documents"])
    return {
        "written_count": written["documents_written"],
        "documents": enriched["documents"],
        "steps": provenance.run(step_name="complete")["steps"],
    }


def _best_sentence(content: str, query_tokens: set[str]) -> tuple[str, int, int, float]:
    best = ("", 0, 0, -1.0)
    for match in _SENTENCE_PATTERN.finditer(content):
        sentence = match.group(0).strip()
        if not sentence:
            continue
        overlap = len(query_tokens & _tokenize(sentence))
        if overlap > best[3]:
            best = (sentence, match.start(), match.end(), float(overlap))
    return best


def _best_window(content: str, query_tokens: set[str]) -> tuple[str, int, int, float]:
    words = list(_TOKEN_PATTERN.finditer(content))
    if not words:
        return ("", 0, 0, 0.0)

    best = ("", 0, 0, -1.0)
    for start_idx in range(len(words)):
        window_tokens: set[str] = set()
        for end_idx in range(start_idx, len(words)):
            window_tokens.add(words[end_idx].group(0).lower())
            overlap = len(query_tokens & window_tokens)
            if overlap <= 0:
                continue
            start_char = words[start_idx].start()
            end_char = words[end_idx].end()
            span = content[start_char:end_char]
            length_penalty = len(span)
            score = overlap - (length_penalty / max(len(content), 1))
            if score > best[3]:
                best = (span, start_char, end_char, score)
    return best


def extractive_qa(
    query: str,
    documents: list[GovernanceDocument],
    *,
    model_id: str = "local-extractive-proxy",
    pipeline_version: str = "track99",
) -> ExtractedSpanAnswer:
    """Return the best extractive span answer from governance documents."""
    query_tokens = _tokenize(query)
    if not query_tokens or not documents:
        return ExtractedSpanAnswer(
            answer="",
            document_id="",
            start=0,
            end=0,
            score=0.0,
            model_id=model_id,
            pipeline_version=pipeline_version,
        )

    best_doc = max(
        documents,
        key=lambda document: len(query_tokens & _tokenize(document.content)),
    )
    overlap_count = len(query_tokens & _tokenize(best_doc.content))
    window = _best_window(best_doc.content, query_tokens)
    sentence = _best_sentence(best_doc.content, query_tokens)
    if sentence[3] >= window[3] and sentence[0]:
        answer, start, end, score = sentence
    else:
        answer, start, end, score = window
    if not answer:
        answer = best_doc.content[: max(len(query), 1)]
        start, end, score = 0, len(answer), float(overlap_count)

    return ExtractedSpanAnswer(
        answer=answer,
        document_id=best_doc.id,
        start=start,
        end=end,
        score=float(score),
        model_id=model_id,
        pipeline_version=pipeline_version,
    )


def build_restricted_query_pipeline() -> dict[str, Any]:
    """Build a restricted query pipeline without generative components."""
    return {
        "retriever": "local-overlap",
        "reader": "extractive-span",
        "generative_forbidden": GENERATIVE_COMPONENTS_FORBIDDEN,
        "generative_default_allowed": GENERATIVE_DEFAULT_ALLOWED,
    }
