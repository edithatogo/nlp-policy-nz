from __future__ import annotations

import json
from pathlib import Path

import pytest

from nlp_policy_nz.ocr.protocol import (
    BenchmarkManifest,
    EngineRegistry,
    build_scaffold,
    load_manifest,
    load_registry,
    validate_immutable_pins,
)

ROOT = Path(__file__).parents[1]


def test_track131_inputs_validate_and_scaffold_is_metadata_only() -> None:
    manifest = load_manifest(ROOT / "data/track131/benchmark_manifest.json")
    registry = load_registry(ROOT / "data/track87/engine_registry.json")
    fixture = json.loads(
        (ROOT / "data/track87/golden_page_fixtures.json").read_text(encoding="utf-8")
    )

    report = build_scaffold(manifest, registry, fixture)

    assert report.status == "not_run"
    assert report.compute_policy == "no_cost_only"
    assert set(report.engine_status.values()) == {"blocked_unpinned"}
    assert "No page images" in report.claim_boundary
    assert len(report.registry_sha256) == 64


def test_benchmark_ready_registry_requires_all_immutable_pins() -> None:
    payload = json.loads((ROOT / "data/track87/engine_registry.json").read_text(encoding="utf-8"))
    payload["status"] = "benchmark_ready"

    with pytest.raises(ValueError, match="immutable engine pins"):
        EngineRegistry.model_validate(payload)


def test_registry_rejects_invalid_digest_even_in_contract_only_mode() -> None:
    payload = json.loads((ROOT / "data/track87/engine_registry.json").read_text(encoding="utf-8"))
    payload["engines"][0]["model_digest"] = "latest"

    with pytest.raises(ValueError, match="String should match pattern"):
        EngineRegistry.model_validate(payload)


def test_scaffold_requires_fixture_case_ids_to_match_manifest() -> None:
    manifest = load_manifest(ROOT / "data/track131/benchmark_manifest.json")
    registry = load_registry(ROOT / "data/track87/engine_registry.json")
    fixture = {"cases": [{"case_id": "wrong"}]}

    with pytest.raises(ValueError, match="case_ids"):
        build_scaffold(manifest, registry, fixture)


def test_validate_immutable_pins_reports_each_missing_identity() -> None:
    payload = json.loads((ROOT / "data/track87/engine_registry.json").read_text(encoding="utf-8"))
    registry = EngineRegistry.model_validate(payload)

    with pytest.raises(ValueError, match="docling: engine_version, model_digest"):
        validate_immutable_pins(registry)


def test_manifest_schema_rejects_paid_compute_policy() -> None:
    payload = json.loads(
        (ROOT / "data/track131/benchmark_manifest.json").read_text(encoding="utf-8")
    )
    payload["compute_policy"] = "paid_compute"

    with pytest.raises(ValueError, match="no_cost_only"):
        BenchmarkManifest.model_validate(payload)
