"""Canonical versioned schemas for lossless archive materialization."""

from __future__ import annotations

import hashlib
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AccessClass(StrEnum):
    """Publication access class for an archive object."""

    PUBLIC = "public"
    RESTRICTED = "restricted"


class CoordinateBox(BaseModel):
    """Axis-aligned coordinates in original or normalized page space."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    x0: float = Field(ge=0)
    y0: float = Field(ge=0)
    x1: float = Field(gt=0)
    y1: float = Field(gt=0)
    space: str = Field(pattern=r"^(original|normalized)$")

    @model_validator(mode="after")
    def validate_bounds(self) -> CoordinateBox:
        """Require a non-empty rectangle and normalized bounds when applicable."""
        if self.x1 <= self.x0 or self.y1 <= self.y0:
            raise ValueError("coordinate box must have positive area")
        if self.space == "normalized" and (self.x1 > 1 or self.y1 > 1):
            raise ValueError("normalized coordinates must not exceed one")
        return self


class ArchiveSource(BaseModel):
    """Immutable source identity and rights metadata."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_id: str = Field(min_length=1)
    uri: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    access_class: AccessClass
    rights_code: str | None = None


class ArchiveDocument(BaseModel):
    """Document-level catalog identity."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    title: str | None = None


class ArchivePage(BaseModel):
    """Page geometry and document relationship."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    page_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    page_number: int = Field(ge=1)
    original_bbox: CoordinateBox
    normalized_bbox: CoordinateBox


class ArchiveRegion(BaseModel):
    """Layout region such as paragraph, table, header, or marginalia."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    region_id: str = Field(min_length=1)
    page_id: str = Field(min_length=1)
    kind: str = Field(min_length=1)


class ArchiveSpan(BaseModel):
    """Immutable source trace for an assertion or extracted unit."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    span_id: str = Field(min_length=1)
    page_id: str = Field(min_length=1)
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    text: str | None = None
    access_class: AccessClass = AccessClass.PUBLIC

    @model_validator(mode="after")
    def validate_range(self) -> ArchiveSpan:
        """Require a forward character range."""
        if self.end <= self.start:
            raise ValueError("span end must be greater than start")
        return self


class ArchiveLine(BaseModel):
    """OCR line linked to a layout region and immutable span."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    line_id: str = Field(min_length=1)
    region_id: str = Field(min_length=1)
    span_id: str = Field(min_length=1)
    text: str | None = None
    access_class: AccessClass = AccessClass.PUBLIC


class ArchiveToken(BaseModel):
    """OCR token with alternatives and calibrated confidence."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    token_id: str = Field(min_length=1)
    line_id: str = Field(min_length=1)
    text: str | None = None
    confidence: float = Field(ge=0, le=1)
    alternatives: tuple[str, ...] = ()
    access_class: AccessClass = AccessClass.PUBLIC


class ArchiveSpeech(BaseModel):
    """Parliamentary speech or interjection with source traces."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    speech_id: str = Field(min_length=1)
    page_id: str = Field(min_length=1)
    text: str | None = None
    span_ids: tuple[str, ...] = ()
    access_class: AccessClass = AccessClass.PUBLIC


class ArchiveTable(BaseModel):
    """Table region metadata without requiring public cell text."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    table_id: str = Field(min_length=1)
    page_id: str = Field(min_length=1)
    span_ids: tuple[str, ...] = ()
    cell_count: int = Field(ge=0)
    access_class: AccessClass = AccessClass.PUBLIC


class ArchiveEmbedding(BaseModel):
    """Embedding metadata with optional vector values kept rights-aware."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    embedding_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    vector_dim: int = Field(ge=1)
    values: tuple[float, ...] = ()
    access_class: AccessClass = AccessClass.PUBLIC

    @model_validator(mode="after")
    def validate_vector(self) -> ArchiveEmbedding:
        """Ensure supplied vectors agree with their declared dimension."""
        if self.values and len(self.values) != self.vector_dim:
            raise ValueError("embedding values must match vector_dim")
        return self


class ArchiveAssertion(BaseModel):
    """Semantic assertion with review state and source lineage."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    assertion_id: str = Field(min_length=1)
    subject_id: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    object_id: str | None = None
    object_text: str | None = None
    span_ids: tuple[str, ...] = ()
    review_state: str = Field(default="unreviewed", min_length=1)
    access_class: AccessClass = AccessClass.PUBLIC


class ArchiveGraphEdge(BaseModel):
    """Graph projection edge retaining assertion identity."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    edge_id: str = Field(min_length=1)
    subject_id: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    object_id: str = Field(min_length=1)


class ArchiveRun(BaseModel):
    """Reproducible materialization run metadata."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    run_id: str = Field(min_length=1)
    schema_version: str = Field(min_length=1)
    commit_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    source_ids: tuple[str, ...] = ()
    output_ids: tuple[str, ...] = ()


class ArchiveBundle(BaseModel):
    """Complete multi-layer archive object with referential integrity."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    sources: tuple[ArchiveSource, ...] = ()
    documents: tuple[ArchiveDocument, ...] = ()
    pages: tuple[ArchivePage, ...] = ()
    regions: tuple[ArchiveRegion, ...] = ()
    spans: tuple[ArchiveSpan, ...] = ()
    lines: tuple[ArchiveLine, ...] = ()
    tokens: tuple[ArchiveToken, ...] = ()
    speeches: tuple[ArchiveSpeech, ...] = ()
    tables: tuple[ArchiveTable, ...] = ()
    embeddings: tuple[ArchiveEmbedding, ...] = ()
    assertions: tuple[ArchiveAssertion, ...] = ()
    graph_edges: tuple[ArchiveGraphEdge, ...] = ()
    runs: tuple[ArchiveRun, ...] = ()

    @model_validator(mode="after")
    def validate_references(self) -> ArchiveBundle:
        """Reject dangling relationships before any export is permitted."""
        source_ids = _unique_ids(self.sources, "source_id")
        document_ids = _unique_ids(self.documents, "document_id")
        page_ids = _unique_ids(self.pages, "page_id")
        region_ids = _unique_ids(self.regions, "region_id")
        span_ids = _unique_ids(self.spans, "span_id")
        line_ids = _unique_ids(self.lines, "line_id")
        speech_ids = _unique_ids(self.speeches, "speech_id")
        table_ids = _unique_ids(self.tables, "table_id")
        embedding_ids = _unique_ids(self.embeddings, "embedding_id")
        assertion_ids = _unique_ids(self.assertions, "assertion_id")
        all_ids = (
            source_ids
            | document_ids
            | page_ids
            | region_ids
            | span_ids
            | line_ids
            | speech_ids
            | table_ids
            | embedding_ids
            | assertion_ids
        )
        for document in self.documents:
            _require(document.source_id, source_ids, "source")
        for page in self.pages:
            _require(page.document_id, document_ids, "document")
        for region in self.regions:
            _require(region.page_id, page_ids, "page")
        for span in self.spans:
            _require(span.page_id, page_ids, "page")
        for line in self.lines:
            _require(line.region_id, region_ids, "region")
            _require(line.span_id, span_ids, "span")
        for token in self.tokens:
            _require(token.line_id, line_ids, "line")
        for speech in self.speeches:
            _require(speech.page_id, page_ids, "page")
            for span_id in speech.span_ids:
                _require(span_id, span_ids, "span")
        for table in self.tables:
            _require(table.page_id, page_ids, "page")
            for span_id in table.span_ids:
                _require(span_id, span_ids, "span")
        for embedding in self.embeddings:
            _require(embedding.target_id, all_ids, "embedding target")
        for assertion in self.assertions:
            _require(assertion.subject_id, all_ids, "subject")
            if assertion.object_id is not None:
                _require(assertion.object_id, all_ids, "object")
            for span_id in assertion.span_ids:
                _require(span_id, span_ids, "span")
        for edge in self.graph_edges:
            _require(edge.subject_id, all_ids, "edge subject")
            _require(edge.object_id, all_ids, "edge object")
        for run in self.runs:
            for source_id in run.source_ids:
                _require(source_id, source_ids, "run source")
        return self

    def public_projection(self) -> ArchiveBundle:
        """Remove restricted text while preserving safe identifiers and lineage."""
        restricted_sources = {
            source.source_id
            for source in self.sources
            if source.access_class == AccessClass.RESTRICTED
        }
        restricted_documents = {
            document.document_id
            for document in self.documents
            if document.source_id in restricted_sources
        }
        restricted_pages = {
            page.page_id for page in self.pages if page.document_id in restricted_documents
        }
        restricted_regions = {
            region.region_id for region in self.regions if region.page_id in restricted_pages
        }
        restricted_spans = {
            span.span_id
            for span in self.spans
            if span.access_class == AccessClass.RESTRICTED or span.page_id in restricted_pages
        }
        restricted_lines = {
            line.line_id
            for line in self.lines
            if line.access_class == AccessClass.RESTRICTED
            or line.region_id in restricted_regions
            or line.span_id in restricted_spans
        }
        restricted_tokens = {
            token.token_id
            for token in self.tokens
            if token.access_class == AccessClass.RESTRICTED or token.line_id in restricted_lines
        }
        restricted_speeches = {
            speech.speech_id
            for speech in self.speeches
            if speech.access_class == AccessClass.RESTRICTED
            or speech.page_id in restricted_pages
            or any(span_id in restricted_spans for span_id in speech.span_ids)
        }
        restricted_tables = {
            table.table_id
            for table in self.tables
            if table.access_class == AccessClass.RESTRICTED
            or table.page_id in restricted_pages
            or any(span_id in restricted_spans for span_id in table.span_ids)
        }
        restricted_targets = (
            restricted_sources
            | restricted_documents
            | restricted_pages
            | restricted_regions
            | restricted_spans
            | restricted_lines
            | restricted_tokens
            | restricted_speeches
            | restricted_tables
        )
        restricted_embeddings = {
            embedding.embedding_id
            for embedding in self.embeddings
            if embedding.access_class == AccessClass.RESTRICTED
        }
        restricted_assertions = {
            assertion.assertion_id
            for assertion in self.assertions
            if assertion.access_class == AccessClass.RESTRICTED
        }
        while True:
            effective_restricted = (
                restricted_targets | restricted_embeddings | restricted_assertions
            )
            next_embeddings = restricted_embeddings | {
                embedding.embedding_id
                for embedding in self.embeddings
                if embedding.target_id in effective_restricted
            }
            next_assertions = restricted_assertions | {
                assertion.assertion_id
                for assertion in self.assertions
                if assertion.subject_id in effective_restricted
                or (assertion.object_id is not None and assertion.object_id in effective_restricted)
                or any(span_id in restricted_spans for span_id in assertion.span_ids)
            }
            if (
                next_embeddings == restricted_embeddings
                and next_assertions == restricted_assertions
            ):
                break
            restricted_embeddings = next_embeddings
            restricted_assertions = next_assertions
        return self.model_copy(
            update={
                "documents": tuple(
                    document.model_copy(update={"title": None})
                    if document.document_id in restricted_documents
                    else document
                    for document in self.documents
                ),
                "spans": tuple(
                    span.model_copy(update={"text": None, "access_class": AccessClass.RESTRICTED})
                    if span.span_id in restricted_spans
                    else span
                    for span in self.spans
                ),
                "lines": tuple(
                    line.model_copy(update={"text": None, "access_class": AccessClass.RESTRICTED})
                    if line.line_id in restricted_lines
                    else line
                    for line in self.lines
                ),
                "tokens": tuple(
                    token.model_copy(
                        update={
                            "text": None,
                            "alternatives": (),
                            "access_class": AccessClass.RESTRICTED,
                        }
                    )
                    if token.token_id in restricted_tokens
                    else token
                    for token in self.tokens
                ),
                "speeches": tuple(
                    speech.model_copy(update={"text": None, "access_class": AccessClass.RESTRICTED})
                    if speech.speech_id in restricted_speeches
                    else speech
                    for speech in self.speeches
                ),
                "tables": tuple(
                    table.model_copy(update={"access_class": AccessClass.RESTRICTED})
                    if table.table_id in restricted_tables
                    else table
                    for table in self.tables
                ),
                "embeddings": tuple(
                    embedding.model_copy(
                        update={"values": (), "access_class": AccessClass.RESTRICTED}
                    )
                    if embedding.embedding_id in restricted_embeddings
                    else embedding
                    for embedding in self.embeddings
                ),
                "assertions": tuple(
                    assertion.model_copy(
                        update={
                            "object_text": None,
                            "access_class": AccessClass.RESTRICTED,
                        }
                    )
                    if assertion.assertion_id in restricted_assertions
                    else assertion
                    for assertion in self.assertions
                ),
            }
        )

    def records(self) -> tuple[dict[str, Any], ...]:
        """Return stable, typed records for row-oriented serializers."""
        groups = (
            ("source", self.sources, "source_id"),
            ("document", self.documents, "document_id"),
            ("page", self.pages, "page_id"),
            ("region", self.regions, "region_id"),
            ("span", self.spans, "span_id"),
            ("line", self.lines, "line_id"),
            ("token", self.tokens, "token_id"),
            ("speech", self.speeches, "speech_id"),
            ("table", self.tables, "table_id"),
            ("embedding", self.embeddings, "embedding_id"),
            ("assertion", self.assertions, "assertion_id"),
            ("edge", self.graph_edges, "edge_id"),
            ("run", self.runs, "run_id"),
        )
        rows: list[dict[str, Any]] = []
        for kind, items, id_field in groups:
            for item in items:
                payload = item.model_dump(mode="json")
                rows.append({"kind": kind, "id": payload[id_field], "payload": payload})
        return tuple(sorted(rows, key=lambda row: (row["kind"], row["id"])))


def stable_id(namespace: str, *parts: str) -> str:
    """Generate a deterministic identifier from normalized identity parts."""
    if not namespace or any(not part for part in parts):
        raise ValueError("namespace and identity parts must be non-empty")
    digest = hashlib.sha256("\x1f".join((namespace, *parts)).encode("utf-8")).hexdigest()
    return f"{namespace}-{digest[:24]}"


def _unique_ids(items: tuple[BaseModel, ...], field: str) -> set[str]:
    values = {str(getattr(item, field)) for item in items}
    if len(values) != len(items):
        raise ValueError(f"duplicate {field} values")
    return values


def _require(value: str, available: set[str], kind: str) -> None:
    if value not in available:
        raise ValueError(f"unknown {kind} reference: {value}")


__all__ = [
    "AccessClass",
    "ArchiveAssertion",
    "ArchiveBundle",
    "ArchiveDocument",
    "ArchiveEmbedding",
    "ArchiveGraphEdge",
    "ArchiveLine",
    "ArchivePage",
    "ArchiveRegion",
    "ArchiveRun",
    "ArchiveSource",
    "ArchiveSpan",
    "ArchiveSpeech",
    "ArchiveTable",
    "ArchiveToken",
    "CoordinateBox",
    "stable_id",
]
