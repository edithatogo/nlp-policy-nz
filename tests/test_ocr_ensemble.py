from __future__ import annotations

import pytest

from nlp_policy_nz.ocr.ensemble import (
    AdapterKind,
    BoundingBox,
    CallableOCRAdapter,
    CascadePolicy,
    EngineAdapterSpec,
    LayoutBlock,
    OCRObservation,
    OCRToken,
    PageInput,
    build_cache_key,
    calculate_quality_metrics,
    compare_observations,
    normalize_reading_order,
    route_page,
)


def _observation(text: str, *, confidence: float = 0.96) -> OCRObservation:
    token = OCRToken(text=text, confidence=confidence, bbox=BoundingBox(x0=0, y0=0, x1=1, y1=1))
    return OCRObservation(
        engine="fixture",
        model_digest="sha256:" + "a" * 64,
        page_id="page-0001",
        text=text,
        tokens=(token,),
        blocks=(
            LayoutBlock(
                block_id="block-1",
                block_type="paragraph",
                bbox=BoundingBox(x0=0, y0=0, x1=1, y1=1),
                reading_order=0,
                text=text,
                tokens=(token,),
            ),
        ),
        mean_confidence=confidence,
    )


def test_geometry_and_reading_order_are_normalized() -> None:
    blocks = (
        LayoutBlock(
            block_id="b2",
            block_type="paragraph",
            bbox=BoundingBox(x0=0.1, y0=0.5, x1=0.9, y1=0.8),
            reading_order=None,
            text="second",
        ),
        LayoutBlock(
            block_id="b1",
            block_type="header",
            bbox=BoundingBox(x0=0.1, y0=0.1, x1=0.9, y1=0.2),
            reading_order=None,
            text="first",
        ),
    )

    ordered = normalize_reading_order(blocks)

    assert [block.block_id for block in ordered] == ["b1", "b2"]
    assert [block.reading_order for block in ordered] == [0, 1]


def test_invalid_geometry_and_confidence_fail_closed() -> None:
    with pytest.raises(ValueError, match="upper coordinates"):
        BoundingBox(x0=0.8, y0=0, x1=0.2, y1=1)
    with pytest.raises(ValueError, match="less than or equal"):
        OCRToken(text="bad", confidence=1.1, bbox=BoundingBox(x0=0, y0=0, x1=1, y1=1))


def test_comparison_retains_alternatives_and_quality_metrics() -> None:
    supplied = _observation("New Zealand Parliament")
    rerun = _observation("New Zeland Parliament", confidence=0.8)

    comparison = compare_observations(supplied, rerun)
    metrics = calculate_quality_metrics(supplied, rerun)

    assert comparison.reference_engine == "fixture"
    assert comparison.candidate_engine == "fixture"
    assert comparison.disagreement_rate > 0
    assert any(alignment.operation.value == "substitute" for alignment in comparison.alignments)
    assert 0 <= metrics.character_error_rate <= 1
    assert 0 <= metrics.word_error_rate <= 1


def test_comparison_rejects_different_pages_and_retains_insert_delete_ops() -> None:
    with pytest.raises(ValueError, match="same page"):
        compare_observations(
            _observation("one"), _observation("two").model_copy(update={"page_id": "other"})
        )
    comparison = compare_observations(_observation("one two"), _observation("one"))
    assert any(item.operation.value == "delete" for item in comparison.alignments)
    comparison = compare_observations(_observation("one"), _observation("one two"))
    assert any(item.operation.value == "insert" for item in comparison.alignments)


def test_route_escalates_low_confidence_or_high_disagreement() -> None:
    policy = CascadePolicy(min_confidence=0.9, max_disagreement_rate=0.1, gpu_engine="olmocr")
    page = PageInput(page_id="page-0001", image_uri="sha256:" + "b" * 64, supplied_ocr="old text")

    decision = route_page(
        page, _observation("new text", confidence=0.7), policy, disagreement_rate=0.2
    )

    assert decision.escalate is True
    assert decision.engine == "olmocr"
    assert decision.requires_gpu is True
    with pytest.raises(ValueError, match="between 0 and 1"):
        route_page(page, _observation("new text"), policy, disagreement_rate=1.1)


def test_high_quality_page_stays_on_cpu_baseline() -> None:
    policy = CascadePolicy(min_confidence=0.9, max_disagreement_rate=0.1, gpu_engine="olmocr")
    page = PageInput(page_id="page-0001", image_uri="sha256:" + "b" * 64)

    decision = route_page(
        page, _observation("stable", confidence=0.99), policy, disagreement_rate=0.01
    )

    assert decision.escalate is False
    assert decision.engine == "fixture"
    assert decision.requires_gpu is False


def test_cache_key_is_content_and_model_addressed() -> None:
    key = build_cache_key(
        source_sha256="c" * 64,
        page_id="page-0001",
        pipeline_version="0.1.0",
        model_digest="sha256:" + "d" * 64,
    )

    assert key.startswith("sha256:")
    assert (
        build_cache_key(
            source_sha256="c" * 64,
            page_id="page-0001",
            pipeline_version="0.1.0",
            model_digest="sha256:" + "d" * 64,
        )
        == key
    )
    with pytest.raises(ValueError, match="lowercase"):
        build_cache_key(
            source_sha256="not-a-digest",
            page_id="page-0001",
            pipeline_version="0.1.0",
            model_digest="sha256:" + "d" * 64,
        )


def test_adapter_spec_requires_pinned_digest_and_known_kind() -> None:
    spec = EngineAdapterSpec(
        kind=AdapterKind.DOCLING,
        engine_version="2.0.0",
        model_digest="sha256:" + "e" * 64,
        container_digest="sha256:" + "f" * 64,
        requires_gpu=False,
    )

    assert spec.kind is AdapterKind.DOCLING
    with pytest.raises(ValueError, match="String should match pattern"):
        EngineAdapterSpec(
            kind=AdapterKind.DOCLING,
            engine_version="2.0.0",
            model_digest="unpinned",
            container_digest="sha256:" + "f" * 64,
            requires_gpu=False,
        )


def test_callable_adapter_enforces_page_and_model_identity() -> None:
    spec = EngineAdapterSpec(
        kind=AdapterKind.DOCLING,
        engine_version="2.0.0",
        model_digest="sha256:" + "e" * 64,
        container_digest="sha256:" + "f" * 64,
        requires_gpu=False,
    )
    page = PageInput(page_id="page-0001", image_uri="sha256:" + "b" * 64)
    adapter = CallableOCRAdapter(
        spec,
        lambda value: _observation("ok").model_copy(
            update={"page_id": value.page_id, "model_digest": spec.model_digest}
        ),
    )

    assert adapter.recognize(page).page_id == page.page_id
    wrong_page = CallableOCRAdapter(spec, lambda _value: _observation("ok"))
    with pytest.raises(ValueError, match="model"):
        wrong_page.recognize(page)
    wrong_page = CallableOCRAdapter(
        spec,
        lambda _value: _observation("ok").model_copy(
            update={"page_id": "other", "model_digest": spec.model_digest}
        ),
    )
    with pytest.raises(ValueError, match="another page"):
        wrong_page.recognize(page)


def test_empty_reference_metrics_are_bounded() -> None:
    empty = _observation("placeholder").model_copy(
        update={"text": "", "tokens": (), "blocks": (), "mean_confidence": 0}
    )
    metrics = calculate_quality_metrics(empty, _observation("text"))

    assert metrics.character_error_rate == 1
    assert metrics.word_error_rate == 1
