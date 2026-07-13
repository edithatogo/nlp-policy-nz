from __future__ import annotations

import pytest

from nlp_policy_nz.ocr.benchmark import (
    BenchmarkCase,
    BenchmarkThresholds,
    evaluate_benchmark,
)
from nlp_policy_nz.ocr.ensemble import BoundingBox, LayoutBlock, OCRObservation, OCRToken


def _observation(text: str, *, engine: str) -> OCRObservation:
    token = OCRToken(text=text, confidence=0.95, bbox=BoundingBox(x0=0, y0=0, x1=1, y1=1))
    block = LayoutBlock(
        block_id="paragraph-1",
        block_type="paragraph",
        bbox=BoundingBox(x0=0, y0=0, x1=1, y1=1),
        reading_order=0,
        text=text,
        tokens=(token,),
    )
    return OCRObservation(
        engine=engine,
        model_digest="sha256:" + "a" * 64,
        page_id="page-0001",
        text=text,
        tokens=(token,),
        blocks=(block,),
        mean_confidence=0.95,
    )


def _thresholds() -> BenchmarkThresholds:
    return BenchmarkThresholds(
        max_character_error_rate=0.2,
        max_word_error_rate=0.5,
        max_disagreement_rate=0.5,
        min_layout_accuracy=1,
        min_reading_order_accuracy=1,
        min_table_accuracy=1,
        max_calibration_error=0.2,
        max_cost_per_page_usd=1,
        min_pages_per_second=0.5,
    )


def test_benchmark_passes_all_quality_and_operations_gates() -> None:
    case = BenchmarkCase(
        case_id="golden-1",
        reference=_observation("stable text", engine="reference"),
        candidate=_observation("stable text", engine="docling"),
        expected_block_types=("paragraph",),
        expected_reading_order=("paragraph-1",),
    )

    result = evaluate_benchmark(
        (case,),
        engine="docling",
        elapsed_seconds=1,
        cost_usd=0.1,
        thresholds=_thresholds(),
    )

    assert result.passed is True
    assert result.failures == ()
    assert result.pages_per_second == 1


def test_benchmark_reports_failed_quality_and_cost_gates() -> None:
    case = BenchmarkCase(
        case_id="golden-1",
        reference=_observation("reference text", engine="reference"),
        candidate=_observation("wrong", engine="surya"),
        expected_block_types=("table",),
        expected_reading_order=("missing",),
        expected_table_count=1,
    )
    thresholds = _thresholds().model_copy(update={"max_cost_per_page_usd": 0.01})

    result = evaluate_benchmark(
        (case,),
        engine="surya",
        elapsed_seconds=10,
        cost_usd=1,
        thresholds=thresholds,
    )

    assert result.passed is False
    assert {
        "character_error_rate",
        "layout_accuracy",
        "reading_order_accuracy",
        "cost_per_page_usd",
    }.issubset(result.failures)


def test_benchmark_rejects_empty_or_invalid_runtime_inputs() -> None:
    with pytest.raises(ValueError, match="at least one"):
        evaluate_benchmark(
            (), engine="docling", elapsed_seconds=1, cost_usd=0, thresholds=_thresholds()
        )
    case = BenchmarkCase(
        case_id="golden-1",
        reference=_observation("x", engine="r"),
        candidate=_observation("x", engine="c"),
    )
    with pytest.raises(ValueError, match="positive"):
        evaluate_benchmark(
            (case,), engine="docling", elapsed_seconds=0, cost_usd=0, thresholds=_thresholds()
        )
    with pytest.raises(ValueError, match="negative"):
        evaluate_benchmark(
            (case,), engine="docling", elapsed_seconds=1, cost_usd=-1, thresholds=_thresholds()
        )


def test_benchmark_defaults_unannotated_structure_to_pass() -> None:
    case = BenchmarkCase(
        case_id="golden-1",
        reference=_observation("x", engine="r"),
        candidate=_observation("x", engine="c"),
    )

    result = evaluate_benchmark(
        (case,), engine="c", elapsed_seconds=1, cost_usd=0, thresholds=_thresholds()
    )

    assert result.layout_accuracy == 1
    assert result.reading_order_accuracy == 1
    assert result.table_accuracy == 1


def test_benchmark_orders_unannotated_blocks_after_explicit_orders() -> None:
    token = OCRToken(
        text="text",
        confidence=0.95,
        bbox=BoundingBox(x0=0, y0=0, x1=0.5, y1=0.2),
    )
    blocks = (
        LayoutBlock(
            block_id="lower-unannotated",
            block_type="paragraph",
            bbox=BoundingBox(x0=0, y0=0.8, x1=1, y1=1),
            text="text",
            tokens=(token,),
        ),
        LayoutBlock(
            block_id="upper-explicit",
            block_type="paragraph",
            bbox=BoundingBox(x0=0, y0=0, x1=1, y1=0.2),
            reading_order=0,
            text="text",
            tokens=(token,),
        ),
    )
    observation = _observation("text", engine="candidate").model_copy(update={"blocks": blocks})
    case = BenchmarkCase(
        case_id="mixed-order",
        reference=_observation("text", engine="reference"),
        candidate=observation,
        expected_reading_order=("upper-explicit", "lower-unannotated"),
    )

    result = evaluate_benchmark(
        (case,), engine="candidate", elapsed_seconds=1, cost_usd=0, thresholds=_thresholds()
    )

    assert result.reading_order_accuracy == 1
