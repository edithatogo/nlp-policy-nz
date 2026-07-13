from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from nlp_policy_nz.extraction.hathi_ingestion import (
    AccessClass,
    HathiArchiveItem,
    HathiArchiveRegistry,
    PublicationDecision,
    build_work_manifest,
    hathi_capability_registry,
    load_archive_registry,
    render_hathi_json_schema,
    render_work_manifest_json,
    validate_curated_seed_count,
)


def _item(**overrides: object) -> HathiArchiveItem:
    values: dict[str, object] = {
        "collection_id": "hathitrust-nz",
        "dataset_id": "hathitrust-nz-inventory",
        "source_id": "nz_parliamentary_debates_hansard",
        "item_id": "uc1.b2889853",
        "htid": "uc1.b2889853",
        "access_class": AccessClass.PUBLIC_METADATA,
        "source_url": "https://example.test/uc1.b2889853",
        "source_dataset_name": "HathiTrust Collection 71329709",
        "rights_code": "17",
        "digitization_profile": "public",
        "publish_eligibility": PublicationDecision.METADATA_ONLY,
    }
    values.update(overrides)
    return HathiArchiveItem.model_validate(values)


def test_public_full_text_requires_explicit_checksum_and_is_eligible() -> None:
    item = _item(
        dataset_id="hathitrust-nz-research-fulltext",
        access_class=AccessClass.PUBLIC_FULL_TEXT,
        publish_eligibility=PublicationDecision.PUBLIC_FULL_TEXT,
        source_sha256="a" * 64,
    )

    assert item.publication_decision() is PublicationDecision.PUBLIC_FULL_TEXT
    assert item.content_address == "sha256:" + "a" * 64


def test_restricted_profiles_fail_closed_even_with_public_dataset_label() -> None:
    item = _item(
        dataset_id="hathitrust-nz-research-fulltext",
        access_class=AccessClass.PUBLIC_FULL_TEXT,
        digitization_profile="ic-world",
        publish_eligibility=PublicationDecision.PUBLIC_FULL_TEXT,
        source_sha256="b" * 64,
    )

    assert item.publication_decision() is PublicationDecision.METADATA_ONLY
    assert not item.content_allowed


def test_public_content_without_checksum_is_rejected() -> None:
    with pytest.raises(ValidationError, match="source_sha256"):
        _item(
            access_class=AccessClass.PUBLIC_FULL_TEXT,
            publish_eligibility=PublicationDecision.PUBLIC_FULL_TEXT,
        )


def test_public_full_text_with_non_public_access_is_rejected() -> None:
    with pytest.raises(ValidationError, match="public_full_text access"):
        _item(
            access_class=AccessClass.PUBLIC_METADATA,
            publish_eligibility=PublicationDecision.PUBLIC_FULL_TEXT,
            source_sha256="c" * 64,
        )


def test_htid_must_be_normalized() -> None:
    with pytest.raises(ValidationError, match="normalized"):
        _item(htid="uc1 / invalid")


def test_duplicate_item_ids_are_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate item identity"):
        HathiArchiveRegistry.from_items((_item(), _item()))


def test_registry_rejects_duplicate_dataset_descriptors() -> None:
    descriptor = {
        "dataset_id": "hathitrust-nz-inventory",
        "access_class": AccessClass.PUBLIC_METADATA,
        "hf_repo": "edithatogo/hathitrust-nz-inventory",
    }
    with pytest.raises(ValidationError, match="duplicate dataset id"):
        HathiArchiveRegistry(
            registry_version="1.0",
            collection_id="hathitrust-nz",
            source_collection_id="71329709",
            curated_seed_record_count=510,
            datasets=(descriptor, descriptor),
        )


def test_registry_can_be_projected_from_distinct_items() -> None:
    registry = HathiArchiveRegistry.from_items(
        (_item(), _item(item_id="second", htid="uc1.second"))
    )

    assert registry.dataset_ids == ("hathitrust-nz-inventory",)


def test_work_manifest_is_sorted_sharded_and_content_addressed() -> None:
    first = _item(item_id="b", htid="uc1.b", source_sha256="b" * 64)
    second = _item(item_id="a", htid="uc1.a", source_sha256="a" * 64)

    manifest = build_work_manifest((first, second), pipeline_version="0.1.0", shard_size=1)

    assert [item.item_id for item in manifest.items] == ["a", "b"]
    assert [shard.item_ids for shard in manifest.shards] == [("a",), ("b",)]
    assert manifest.items[0].content_address == "sha256:" + "a" * 64


def test_metadata_content_is_identity_addressed() -> None:
    assert _item().content_address.startswith("identity:")


def test_work_manifest_rejects_invalid_shard_size_and_mixed_collections() -> None:
    item = _item()
    with pytest.raises(ValueError, match="shard_size"):
        build_work_manifest((item,), pipeline_version="0.1.0", shard_size=0)
    with pytest.raises(ValueError, match="collection ids"):
        build_work_manifest(
            (item, _item(item_id="second", htid="uc1.second", collection_id="other")),
            pipeline_version="0.1.0",
        )
    with pytest.raises(ValueError, match="duplicate item identity"):
        build_work_manifest((item, item), pipeline_version="0.1.0")


def test_work_manifest_json_is_deterministic() -> None:
    manifest = build_work_manifest((_item(),), pipeline_version="0.1.0")

    rendered = render_work_manifest_json(manifest)

    assert rendered.endswith("\n")
    assert '"pipeline_version": "0.1.0"' in rendered


def test_registry_loader_preserves_curated_seed_and_dataset_rows(tmp_path) -> None:
    path = tmp_path / "archive_registry.json"
    path.write_text(
        json.dumps(
            {
                "registry_version": "1.0",
                "collection": {
                    "collection_id": "hathitrust-nz",
                    "source_collection_id": "71329709",
                    "curated_seed_record_count": 510,
                },
                "datasets": [
                    {
                        "dataset_id": "hathitrust-nz-inventory",
                        "access_class": "public_metadata",
                        "hf_repo": "edithatogo/hathitrust-nz-inventory",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    registry = load_archive_registry(path)

    assert registry.curated_seed_record_count == 510
    assert registry.collection_id == "hathitrust-nz"
    assert registry.dataset_ids == ("hathitrust-nz-inventory",)


def test_registry_loader_normalizes_existing_hathi_access_labels(tmp_path) -> None:
    path = tmp_path / "archive_registry.json"
    path.write_text(
        json.dumps(
            {
                "collection": {
                    "collection_id": "hathitrust-nz",
                    "source_collection_id": "71329709",
                    "curated_seed_record_count": 510,
                },
                "datasets": [
                    {
                        "dataset_id": "hathitrust-nz-research-fulltext",
                        "access_class": "public_full_text_where_confirmed",
                        "hf_repo": "edithatogo/hathitrust-nz-research-fulltext",
                    },
                    {
                        "dataset_id": "hathitrust-nz-research-metadata",
                        "access_class": "metadata_only_until_static_host_bundle_is_eligible",
                        "hf_repo": "edithatogo/hathitrust-nz-research-metadata",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    registry = load_archive_registry(path)

    assert registry.datasets[0].access_class is AccessClass.PUBLIC_FULL_TEXT
    assert registry.datasets[1].access_class is AccessClass.RESTRICTED_METADATA


def test_registry_loader_requires_collection_and_dataset_lists(tmp_path) -> None:
    missing_collection = tmp_path / "missing-collection.json"
    missing_collection.write_text(json.dumps({"datasets": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="collection"):
        load_archive_registry(missing_collection)

    missing_datasets = tmp_path / "missing-datasets.json"
    missing_datasets.write_text(json.dumps({"collection": {}}), encoding="utf-8")
    with pytest.raises(ValueError, match="datasets"):
        load_archive_registry(missing_datasets)


def test_curated_seed_count_drift_fails_closed() -> None:
    registry = HathiArchiveRegistry(
        registry_version="1.0",
        collection_id="hathitrust-nz",
        source_collection_id="71329709",
        curated_seed_record_count=510,
    )

    assert validate_curated_seed_count(registry, 510) is None
    with pytest.raises(ValueError, match="curated seed count drift"):
        validate_curated_seed_count(registry, 509)


def test_json_schema_is_versioned_and_contains_rights_fields() -> None:
    schema = render_hathi_json_schema()

    assert schema["$defs"]["HathiArchiveItem"]["properties"]["access_class"]
    assert "source_sha256" in schema["$defs"]["HathiArchiveItem"]["properties"]


def test_capability_registry_is_read_only_and_surface_compatible() -> None:
    capabilities = hathi_capability_registry()

    assert {item["capability_id"] for item in capabilities} == {
        "hathi.registry.validate",
        "hathi.work.plan",
    }
    assert all(item["side_effect"] == "read_only" for item in capabilities)
    assert all(set(item["surfaces"]) == {"cli", "api", "sdk", "mcp"} for item in capabilities)


def test_capability_registry_returns_defensive_copies() -> None:
    capabilities = hathi_capability_registry()
    capabilities[0]["surfaces"]["cli"] = "implemented"

    assert hathi_capability_registry()[0]["surfaces"]["cli"] == "planned"
