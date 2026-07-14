"""Engine-neutral contracts for cloud-run layout-aware OCR.

Heavy OCR engines are deliberately optional. This module owns the stable
interchange format, quality metrics, cache identity, and routing policy so
Docling, PP-StructureV3, Surya, and olmOCR adapters can be replaced without
changing downstream extraction code.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from difflib import SequenceMatcher
from enum import StrEnum
from hashlib import sha256
from typing import Final, Protocol, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator

Digest: TypeAlias = str
CacheKey: TypeAlias = str
_DIGEST_PATTERN: Final[str] = r"^sha256:[0-9a-f]{64}$"


class AdapterKind(StrEnum):
    """Supported OCR/layout adapter families."""

    DOCLING = "docling"
    PP_STRUCTURE_V3 = "pp-structure-v3"
    SURYA = "surya"
    OLMOCR = "olmocr"
    SUPPLIED = "supplied-ocr"


class BoundingBox(BaseModel):
    """Normalized page coordinates in the half-open unit square."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    x0: float = Field(ge=0, le=1)
    y0: float = Field(ge=0, le=1)
    x1: float = Field(ge=0, le=1)
    y1: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def _validate_order(self) -> BoundingBox:
        if self.x1 <= self.x0 or self.y1 <= self.y0:
            raise ValueError("bounding box upper coordinates must exceed lower coordinates")
        return self


class OCRToken(BaseModel):
    """One OCR token with confidence and page geometry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    bbox: BoundingBox


class LayoutBlock(BaseModel):
    """A semantic page region in reading order."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    block_id: str = Field(min_length=1)
    block_type: str = Field(min_length=1)
    bbox: BoundingBox
    reading_order: int | None = Field(default=None, ge=0)
    text: str = ""
    tokens: tuple[OCRToken, ...] = ()


class PageInput(BaseModel):
    """Content-addressed page reference supplied to an OCR adapter."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    page_id: str = Field(min_length=1)
    image_uri: str = Field(min_length=1)
    supplied_ocr: str | None = None
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)


class EngineAdapterSpec(BaseModel):
    """Pinned engine/model/container identity for reproducibility."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: AdapterKind
    engine_version: str = Field(min_length=1)
    model_digest: Digest = Field(pattern=_DIGEST_PATTERN)
    container_digest: Digest = Field(pattern=_DIGEST_PATTERN)
    requires_gpu: bool


class OCRObservation(BaseModel):
    """One complete OCR/layout observation for a page."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    engine: str = Field(min_length=1)
    model_digest: Digest = Field(pattern=_DIGEST_PATTERN)
    page_id: str = Field(min_length=1)
    text: str = ""
    tokens: tuple[OCRToken, ...] = ()
    blocks: tuple[LayoutBlock, ...] = ()
    mean_confidence: float = Field(ge=0, le=1)


class AlignmentOperation(StrEnum):
    """Token-level edit operation between OCR alternatives."""

    MATCH = "match"
    SUBSTITUTE = "substitute"
    INSERT = "insert"
    DELETE = "delete"


class TokenAlignment(BaseModel):
    """One retained token alignment operation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    operation: AlignmentOperation
    reference_token: str | None = None
    candidate_token: str | None = None


class ObservationComparison(BaseModel):
    """Retained comparison between two OCR observations."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    page_id: str
    reference_engine: str
    candidate_engine: str
    reference_text: str
    candidate_text: str
    disagreement_rate: float = Field(ge=0, le=1)
    alignments: tuple[TokenAlignment, ...] = ()


class QualityMetrics(BaseModel):
    """Page-level OCR quality metrics and disagreement signals."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    character_error_rate: float = Field(ge=0, le=1)
    word_error_rate: float = Field(ge=0, le=1)
    disagreement_rate: float = Field(ge=0, le=1)
    reference_confidence: float = Field(ge=0, le=1)
    candidate_confidence: float = Field(ge=0, le=1)


class CascadePolicy(BaseModel):
    """Quality thresholds for CPU baseline and GPU escalation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    min_confidence: float = Field(ge=0, le=1)
    max_disagreement_rate: float = Field(ge=0, le=1)
    gpu_engine: str = Field(min_length=1)


class CascadeDecision(BaseModel):
    """Deterministic routing decision for one page."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    page_id: str
    engine: str
    escalate: bool
    requires_gpu: bool
    reason: str


class OCRAdapter(Protocol):
    """Protocol implemented by optional engine adapters."""

    spec: EngineAdapterSpec

    def recognize(self, page: PageInput) -> OCRObservation:
        """Produce one page observation without mutating the source."""


class CallableOCRAdapter:
    """Small adapter bridge used by optional engine integrations and tests."""

    def __init__(
        self,
        spec: EngineAdapterSpec,
        runner: Callable[[PageInput], OCRObservation],
    ) -> None:
        self.spec = spec
        self._runner = runner

    def recognize(self, page: PageInput) -> OCRObservation:
        """Run the injected engine and enforce page/engine identity."""
        observation = self._runner(page)
        if observation.page_id != page.page_id:
            raise ValueError("OCR adapter returned an observation for another page")
        if observation.model_digest != self.spec.model_digest:
            raise ValueError("OCR adapter returned an observation from another model")
        return observation


def normalize_reading_order(blocks: tuple[LayoutBlock, ...]) -> tuple[LayoutBlock, ...]:
    """Sort blocks by explicit order or top-left geometry and assign order."""
    ordered = sorted(
        blocks,
        key=lambda block: (
            block.reading_order is None,
            block.reading_order if block.reading_order is not None else 0,
            block.bbox.y0,
            block.bbox.x0,
            block.block_id,
        ),
    )
    return tuple(
        block.model_copy(update={"reading_order": index}) for index, block in enumerate(ordered)
    )


def compare_observations(
    reference: OCRObservation,
    candidate: OCRObservation,
) -> ObservationComparison:
    """Compare OCR text while retaining both unmodified alternatives."""
    if reference.page_id != candidate.page_id:
        raise ValueError("observations must refer to the same page")
    reference_tokens = reference.text.split()
    candidate_tokens = candidate.text.split()
    disagreement = 1 - SequenceMatcher(None, reference_tokens, candidate_tokens).ratio()
    alignments = _align_tokens(reference_tokens, candidate_tokens)
    return ObservationComparison(
        page_id=reference.page_id,
        reference_engine=reference.engine,
        candidate_engine=candidate.engine,
        reference_text=reference.text,
        candidate_text=candidate.text,
        disagreement_rate=round(disagreement, 6),
        alignments=alignments,
    )


def calculate_quality_metrics(
    reference: OCRObservation,
    candidate: OCRObservation,
) -> QualityMetrics:
    """Calculate bounded CER/WER proxies and preserve confidence signals."""
    comparison = compare_observations(reference, candidate)
    reference_text = reference.text.casefold()
    candidate_text = candidate.text.casefold()
    character_distance = _levenshtein(reference_text, candidate_text)
    word_distance = _levenshtein(reference_text.split(), candidate_text.split())
    return QualityMetrics(
        character_error_rate=_bounded_error(character_distance, len(reference_text)),
        word_error_rate=_bounded_error(word_distance, len(reference_text.split())),
        disagreement_rate=comparison.disagreement_rate,
        reference_confidence=reference.mean_confidence,
        candidate_confidence=candidate.mean_confidence,
    )


def route_page(
    page: PageInput,
    baseline: OCRObservation,
    policy: CascadePolicy,
    *,
    disagreement_rate: float,
) -> CascadeDecision:
    """Escalate low-quality pages to the configured GPU engine."""
    if not 0 <= disagreement_rate <= 1:
        raise ValueError("disagreement_rate must be between 0 and 1")
    low_confidence = baseline.mean_confidence < policy.min_confidence
    disagreement = disagreement_rate > policy.max_disagreement_rate
    escalate = low_confidence or disagreement
    reason = (
        "low_confidence"
        if low_confidence
        else "high_disagreement"
        if disagreement
        else "baseline_pass"
    )
    return CascadeDecision(
        page_id=page.page_id,
        engine=policy.gpu_engine if escalate else baseline.engine,
        escalate=escalate,
        requires_gpu=escalate,
        reason=reason,
    )


def build_cache_key(
    *,
    source_sha256: str,
    page_id: str,
    pipeline_version: str,
    model_digest: Digest,
) -> CacheKey:
    """Build an immutable cache key from source, page, pipeline, and model."""
    if len(source_sha256) != 64 or any(char not in "0123456789abcdef" for char in source_sha256):
        raise ValueError("source_sha256 must be a lowercase 64-character digest")
    payload = json.dumps(
        [source_sha256, page_id, pipeline_version, model_digest],
        ensure_ascii=True,
        separators=(",", ":"),
    )
    return f"sha256:{sha256(payload.encode('utf-8')).hexdigest()}"


def _bounded_error(distance: int, reference_length: int) -> float:
    """Return a normalized edit distance, bounded for empty references."""
    if reference_length == 0:
        return 0.0 if distance == 0 else 1.0
    return min(1.0, distance / reference_length)


def _align_tokens(reference: list[str], candidate: list[str]) -> tuple[TokenAlignment, ...]:
    """Retain deterministic token-level alternatives from SequenceMatcher."""
    matcher = SequenceMatcher(None, reference, candidate)
    alignments: list[TokenAlignment] = []
    for operation, ref_start, ref_end, candidate_start, candidate_end in matcher.get_opcodes():
        ref_values = reference[ref_start:ref_end]
        candidate_values = candidate[candidate_start:candidate_end]
        if operation == "equal":
            alignments.extend(
                TokenAlignment(
                    operation=AlignmentOperation.MATCH,
                    reference_token=value,
                    candidate_token=value,
                )
                for value in ref_values
            )
        elif operation == "replace":
            for index in range(max(len(ref_values), len(candidate_values))):
                alignments.append(
                    TokenAlignment(
                        operation=AlignmentOperation.SUBSTITUTE,
                        reference_token=ref_values[index] if index < len(ref_values) else None,
                        candidate_token=candidate_values[index]
                        if index < len(candidate_values)
                        else None,
                    )
                )
        elif operation == "delete":
            alignments.extend(
                TokenAlignment(operation=AlignmentOperation.DELETE, reference_token=value)
                for value in ref_values
            )
        elif operation == "insert":
            alignments.extend(
                TokenAlignment(operation=AlignmentOperation.INSERT, candidate_token=value)
                for value in candidate_values
            )
    return tuple(alignments)


def _levenshtein(reference: str | list[str], candidate: str | list[str]) -> int:
    """Compute deterministic Levenshtein distance for text or token lists."""
    left = list(reference)
    right = list(candidate)
    previous = list(range(len(right) + 1))
    for left_index, left_value in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_value in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[right_index] + 1,
                    previous[right_index - 1] + (left_value != right_value),
                )
            )
        previous = current
    return previous[-1]


__all__ = [
    "AdapterKind",
    "AlignmentOperation",
    "BoundingBox",
    "CacheKey",
    "CallableOCRAdapter",
    "CascadeDecision",
    "CascadePolicy",
    "EngineAdapterSpec",
    "LayoutBlock",
    "OCRAdapter",
    "OCRObservation",
    "OCRToken",
    "ObservationComparison",
    "PageInput",
    "QualityMetrics",
    "TokenAlignment",
    "build_cache_key",
    "calculate_quality_metrics",
    "compare_observations",
    "normalize_reading_order",
    "route_page",
]
