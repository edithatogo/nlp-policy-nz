from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.ocr.ensemble import AdapterKind


def test_candidate_engine_registry_is_explicitly_unpinned_until_benchmarked() -> None:
    path = Path("data/track87/engine_registry.json")
    registry = json.loads(path.read_text(encoding="utf-8"))

    assert registry["status"] == "adapter_contract_only"
    assert {item["kind"] for item in registry["engines"]} == {
        AdapterKind.DOCLING,
        AdapterKind.PP_STRUCTURE_V3,
        AdapterKind.SURYA,
        AdapterKind.OLMOCR,
    }
    assert all(item["model_digest"] is None for item in registry["engines"])
    assert all(item["container_digest"] is None for item in registry["engines"])


def test_golden_page_fixture_is_stratified_and_metadata_only() -> None:
    fixture = json.loads(Path("data/track87/golden_page_fixtures.json").read_text(encoding="utf-8"))

    assert "page images" in fixture["claim_boundary"]
    assert {case["layout_class"] for case in fixture["cases"]} == {
        "single_column",
        "multi_column",
        "table_and_marginalia",
    }
    assert len({case["year_band"] for case in fixture["cases"]}) == 3
