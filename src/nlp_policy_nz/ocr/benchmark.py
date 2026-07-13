"""Deterministic benchmark gates for historical-page OCR candidates."""

from __future__ import annotations

from statistics import mean

from pydantic import BaseModel, ConfigDict, Field

from .ensemble import OCRObservation, calculate_quality_metrics


class BenchmarkCase(BaseModel):
    """One held-out page pair with structural expectations."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    case_id: str = Field(min_length=1)
    reference: OCRObservation
    candidate: OCRObservation
    expected_block_types: tuple[str, ...] = ()
    expected_reading_order: tuple[str, ...] = ()
    expected_table_count: int = Field(default=0, ge=0)


class BenchmarkThresholds(BaseModel):
    """Promotion limits for an OCR engine benchmark."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    max_character_error_rate: float = Field(ge=0, le=1)
    max_word_error_rate: float = Field(ge=0, le=1)
    max_disagreement_rate: float = Field(ge=0, le=1)
    min_layout_accuracy: float = Field(ge=0, le=1)
    min_reading_order_accuracy: float = Field(ge=0, le=1)
    min_table_accuracy: float = Field(ge=0, le=1)
    max_calibration_error: float = Field(ge=0, le=1)
    max_cost_per_page_usd: float = Field(ge=0)
    min_pages_per_second: float = Field(ge=0)


class BenchmarkResult(BaseModel):
    """Aggregate quality, operations, and promotion result."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    engine: str
    page_count: int = Field(ge=1)
    character_error_rate: float = Field(ge=0, le=1)
    word_error_rate: float = Field(ge=0, le=1)
    disagreement_rate: float = Field(ge=0, le=1)
    layout_accuracy: float = Field(ge=0, le=1)
    reading_order_accuracy: float = Field(ge=0, le=1)
    table_accuracy: float = Field(ge=0, le=1)
    calibration_error: float = Field(ge=0, le=1)
    cost_per_page_usd: float = Field(ge=0)
    pages_per_second: float = Field(ge=0)
    passed: bool
    failures: tuple[str, ...] = ()


def evaluate_benchmark(
    cases: tuple[BenchmarkCase, ...],
    *,
    engine: str,
    elapsed_seconds: float,
    cost_usd: float,
    thresholds: BenchmarkThresholds,
) -> BenchmarkResult:
    """Evaluate held-out OCR pages against quality and operational gates."""
    if not cases:
        raise ValueError("benchmark requires at least one case")
    if elapsed_seconds <= 0:
        raise ValueError("elapsed_seconds must be positive")
    if cost_usd < 0:
        raise ValueError("cost_usd must not be negative")
    metric_rows = [calculate_quality_metrics(case.reference, case.candidate) for case in cases]
    layout_scores = [_layout_accuracy(case) for case in cases]
    order_scores = [_reading_order_accuracy(case) for case in cases]
    table_scores = [_table_accuracy(case) for case in cases]
    mean_confidence = mean(row.candidate_confidence for row in metric_rows)
    mean_cer = mean(row.character_error_rate for row in metric_rows)
    calibration_error = abs(mean_confidence - (1 - mean_cer))
    page_count = len(cases)
    values = {
        "character_error_rate": mean_cer,
        "word_error_rate": mean(row.word_error_rate for row in metric_rows),
        "disagreement_rate": mean(row.disagreement_rate for row in metric_rows),
        "layout_accuracy": mean(layout_scores),
        "reading_order_accuracy": mean(order_scores),
        "table_accuracy": mean(table_scores),
        "calibration_error": calibration_error,
        "cost_per_page_usd": cost_usd / page_count,
        "pages_per_second": page_count / elapsed_seconds,
    }
    failures = _gate_failures(values, thresholds)
    return BenchmarkResult(
        engine=engine,
        page_count=page_count,
        **values,
        passed=not failures,
        failures=failures,
    )


def _layout_accuracy(case: BenchmarkCase) -> float:
    """Score block-type preservation for one page."""
    if not case.expected_block_types:
        return 1.0
    actual = tuple(block.block_type for block in case.candidate.blocks)
    return _sequence_accuracy(case.expected_block_types, actual)


def _reading_order_accuracy(case: BenchmarkCase) -> float:
    """Score candidate block order against the held-out annotation."""
    if not case.expected_reading_order:
        return 1.0
    actual = tuple(
        block.block_id
        for block in sorted(case.candidate.blocks, key=lambda block: block.reading_order or 0)
    )
    return _sequence_accuracy(case.expected_reading_order, actual)


def _table_accuracy(case: BenchmarkCase) -> float:
    """Score table-region count without requiring table cell ground truth."""
    actual = sum(block.block_type.casefold() == "table" for block in case.candidate.blocks)
    return 1.0 if actual == case.expected_table_count else 0.0


def _sequence_accuracy(expected: tuple[str, ...], actual: tuple[str, ...]) -> float:
    """Return the fraction of expected sequence entries recovered exactly."""
    if not expected:
        return 1.0
    return sum(
        index < len(actual) and value == actual[index] for index, value in enumerate(expected)
    ) / len(expected)


def _gate_failures(values: dict[str, float], thresholds: BenchmarkThresholds) -> tuple[str, ...]:
    """Return stable names for failed promotion gates."""
    limits = {
        "character_error_rate": (
            values["character_error_rate"] <= thresholds.max_character_error_rate
        ),
        "word_error_rate": values["word_error_rate"] <= thresholds.max_word_error_rate,
        "disagreement_rate": values["disagreement_rate"] <= thresholds.max_disagreement_rate,
        "layout_accuracy": values["layout_accuracy"] >= thresholds.min_layout_accuracy,
        "reading_order_accuracy": values["reading_order_accuracy"]
        >= thresholds.min_reading_order_accuracy,
        "table_accuracy": values["table_accuracy"] >= thresholds.min_table_accuracy,
        "calibration_error": values["calibration_error"] <= thresholds.max_calibration_error,
        "cost_per_page_usd": values["cost_per_page_usd"] <= thresholds.max_cost_per_page_usd,
        "pages_per_second": values["pages_per_second"] >= thresholds.min_pages_per_second,
    }
    return tuple(name for name, passed in limits.items() if not passed)


__all__ = [
    "BenchmarkCase",
    "BenchmarkResult",
    "BenchmarkThresholds",
    "evaluate_benchmark",
]
