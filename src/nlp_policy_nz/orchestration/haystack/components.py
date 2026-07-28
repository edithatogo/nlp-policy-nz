"""Pure-Python Haystack-compatible governance components."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime
from typing import Any

from nlp_policy_nz.orchestration.haystack.types import GovernanceDocument
from nlp_policy_nz.storage.interfaces import VectorBackend

_RESTRICTED_ACCESS = frozenset({"restricted", "maori", "sovereign"})
_SECTION_PATTERN = re.compile(
    r"(?im)^(?:section\s+\d+|\d+\.)\s*",
)
_BLANK_LINE_PATTERN = re.compile(r"\n\s*\n+")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class RightsGateComponent:
    """Fail-closed rights gate for governance documents."""

    def run(self, *, documents: list[GovernanceDocument]) -> dict[str, Any]:
        """Pass through cleared or public documents; block restricted items."""
        allowed: list[GovernanceDocument] = []
        for document in documents:
            access_class = str(document.meta.get("access_class") or "").strip().lower()
            # Normalise common Māori macron variants for fail-closed matching.
            access_class = access_class.replace("ā", "a").replace("Ā", "a")
            if not access_class:
                return {
                    "documents": [],
                    "error": f"missing access_class for document {document.id}",
                }
            if access_class in _RESTRICTED_ACCESS and document.meta.get("rights_cleared") is not True:
                return {
                    "documents": [],
                    "error": f"rights not cleared for document {document.id}",
                }
            allowed.append(document)
        return {"documents": allowed}


class LegalStructureSplitter:
    """Split documents on legal structure markers while preserving clause boundaries."""

    def __init__(
        self,
        *,
        nlp: object | None = None,
        year: int | None = None,
        number: int | None = None,
    ) -> None:
        """Initialize optional spaCy-backed chunking parameters."""
        self._nlp = nlp
        self._year = year
        self._number = number

    def _split_content(self, document: GovernanceDocument) -> list[str]:
        if self._nlp is not None and self._year is not None and self._number is not None:
            from nlp_policy_nz.syntactic.chunking import chunk_legislation_document

            chunks = chunk_legislation_document(
                document.content,
                self._nlp,
                self._year,
                self._number,
            )
            return [chunk["text"] for chunk in chunks]

        parts = _BLANK_LINE_PATTERN.split(document.content.strip())
        if len(parts) == 1:
            parts = [part.strip() for part in _SECTION_PATTERN.split(document.content) if part.strip()]
        return [part.strip() for part in parts if part.strip()]

    def run(self, *, documents: list[GovernanceDocument]) -> dict[str, Any]:
        """Split each document into clause-level governance documents."""
        output: list[GovernanceDocument] = []
        for document in documents:
            for clause_index, clause_text in enumerate(self._split_content(document)):
                meta = dict(document.meta)
                meta["clause_index"] = clause_index
                meta["parent_id"] = document.id
                output.append(
                    GovernanceDocument(
                        id=f"{document.id}::clause-{clause_index}",
                        content=clause_text,
                        meta=meta,
                    )
                )
        return {"documents": output}


class SpaCyEnricher:
    """Enrich document metadata with spaCy entities when a pipeline is provided."""

    def __init__(
        self,
        *,
        nlp: Callable[[str], object] | None = None,
        model_id: str = "noop",
    ) -> None:
        """Initialize with an optional spaCy-like callable."""
        self._nlp = nlp
        self._model_id = model_id

    def run(self, *, documents: list[GovernanceDocument]) -> dict[str, Any]:
        """Attach entity metadata to each document."""
        enriched: list[GovernanceDocument] = []
        for document in documents:
            meta = dict(document.meta)
            meta["pipeline_component"] = "SpaCyEnricher"
            if self._nlp is None:
                meta["spacy_model"] = "noop"
                meta["ents"] = []
            else:
                doc = self._nlp(document.content)
                meta["spacy_model"] = self._model_id
                ents = getattr(doc, "ents", ())
                meta["ents"] = [
                    {
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                    }
                    for ent in ents
                ]
            enriched.append(replace(document, meta=meta))
        return {"documents": enriched}


class ProvenanceStepRecorder:
    """Record pipeline step metadata compatible with ProvenanceRecorder fields."""

    def __init__(
        self,
        *,
        steps: list[dict[str, Any]] | None = None,
        callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._steps = steps if steps is not None else []
        self._callback = callback

    def run(
        self,
        *,
        step_name: str,
        started_at: str | None = None,
        ended_at: str | None = None,
        details: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        """Append a provenance step and optionally invoke a callback."""
        payload: dict[str, Any] = {
            "step_name": step_name,
            "started_at": started_at or _utc_now(),
            "ended_at": ended_at or _utc_now(),
        }
        if details:
            payload.update(details)
        self._steps.append(payload)
        if self._callback is not None:
            self._callback(payload)
        return {"steps": list(self._steps)}


class InMemoryDocumentStore:
    """Local offline document store for governance indexing."""

    def __init__(self) -> None:
        """Initialize an empty in-memory store."""
        self.documents: list[GovernanceDocument] = []

    def write(self, documents: list[GovernanceDocument]) -> int:
        """Append documents and return how many were written."""
        self.documents.extend(documents)
        return len(documents)


class DocumentWriter:
    """Write governance documents to an in-memory or custom store."""

    def __init__(self, *, store: InMemoryDocumentStore | None = None) -> None:
        """Initialize with an optional document store."""
        self._store = store or InMemoryDocumentStore()

    def run(self, *, documents: list[GovernanceDocument]) -> dict[str, Any]:
        """Write documents to the configured store."""
        written = self._store.write(documents)
        return {"documents_written": written}


class LanceDBDocumentWriter:
    """Write governance documents through a VectorBackend-compatible adapter."""

    def __init__(
        self,
        *,
        backend: VectorBackend,
        vector_dim: int = 384,
    ) -> None:
        """Initialize with a vector backend and default embedding width."""
        self._backend = backend
        self._vector_dim = vector_dim

    def run(self, *, documents: list[GovernanceDocument]) -> dict[str, Any]:
        """Create or extend a vector index with governance documents."""
        records: list[dict[str, Any]] = []
        for document in documents:
            vector = document.meta.get("vector")
            if vector is None:
                vector = [0.0] * self._vector_dim
            records.append(
                {
                    "doc_id": document.id,
                    "text": document.content,
                    "vector": vector,
                    "meta": document.meta,
                }
            )
        if self._backend.index_exists():
            self._backend.add_records(records)
        else:
            self._backend.create_index(records)
        return {"documents_written": len(records)}
