from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.integrations.data_registry import DataRecord, DataSovereigntyRegistry


def test_registry_register_lookup_list_and_persist(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.json"
    registry = DataSovereigntyRegistry(str(registry_path))

    first = registry.register(
        dataset_id="nz-hansard-v1",
        source="https://example.test/hansard",
        license_id="CC-BY-4.0",
        version="1.0.0",
        doi="10.1234/example",
        deposit_url="https://zenodo.test/record/1",
    )
    second = registry.register(
        dataset_id="nz-hansard-v1",
        source="https://example.test/hansard",
        license_id="CC-BY-4.0",
        version="1.0.1",
    )

    assert first.dataset_id == "nz-hansard-v1"
    assert second.version == "1.0.1"
    assert registry.lookup("nz-hansard-v1") == second
    assert registry.lookup("missing") is None
    assert registry.list_records() == [second]
    assert json.loads(registry_path.read_text(encoding="utf-8"))[0]["version"] == "1.0.1"

    reloaded = DataSovereigntyRegistry(str(registry_path))
    assert reloaded.lookup("nz-hansard-v1") == second


def test_registry_load_handles_missing_and_invalid_files(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    registry = DataSovereigntyRegistry(str(missing))
    assert registry.list_records() == []

    invalid = tmp_path / "invalid.json"
    invalid.write_text("{not-json}", encoding="utf-8")
    registry = DataSovereigntyRegistry(str(invalid))
    assert registry.list_records() == []


def test_data_record_can_be_constructed_explicitly() -> None:
    record = DataRecord(
        dataset_id="demo",
        source="source",
        license="CC0",
        version="1.0.0",
        recorded_at="2026-06-29T00:00:00+00:00",
    )

    assert record.doi is None
    assert record.deposit_url is None
    assert "demo" in repr(record)
