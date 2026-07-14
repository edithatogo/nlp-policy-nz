from __future__ import annotations

import json
from pathlib import Path
from typing import Self

import pytest

from nlp_policy_nz.archive.schema import ArchiveBundle
from nlp_policy_nz.publication.hf_archive import (
    CONFIG_NAMES,
    PublicationConflictError,
    build_publication_plan,
    materialize_publication,
    probe_huggingface_endpoint,
    publish_hf_archive,
    stage_publication,
    stream_config,
    verify_materialized_publication,
    write_checksums,
    write_dataset_card,
    write_publication_verification,
    write_release_manifest,
)


def _bundle(*, restricted: bool = False) -> ArchiveBundle:
    from tests.test_archive_schema import _bundle as make_bundle

    return make_bundle(restricted=restricted)


def test_publication_plan_has_all_streaming_configs_and_stable_digest() -> None:
    plan = build_publication_plan(
        _bundle(),
        dataset_id="edithatogo/hathi-structured",
        collection_id="edithatogo/hathitrust-nz",
    )

    assert plan.config_names == CONFIG_NAMES
    assert plan.streaming is True
    assert plan.record_counts["documents"] == 1
    assert len(plan.content_sha256) == 64
    assert plan == build_publication_plan(
        _bundle(),
        dataset_id="edithatogo/hathi-structured",
        collection_id="edithatogo/hathitrust-nz",
    )


def test_stream_config_rows_are_viewer_safe_and_partitionable() -> None:
    rows = list(stream_config(_bundle(), "tokens"))

    assert rows == [{"id": "token-1", "kind": "token", "payload": rows[0]["payload"]}]
    assert rows[0]["payload"]["text"] == "Hello"
    assert all(isinstance(row, dict) for row in rows)
    assert next(stream_config(_bundle(), "tokens", public=False))["payload"]["text"] == "Hello"
    with pytest.raises(ValueError, match="unknown publication configuration"):
        list(stream_config(_bundle(), "unknown"))


def test_restricted_bundle_is_projected_without_text_or_vectors() -> None:
    plan = build_publication_plan(
        _bundle(restricted=True), dataset_id="user/dataset", collection_id="user/collection"
    )

    restricted_rows = list(stream_config(_bundle(restricted=True), "tokens"))
    assert plan.restricted_record_count > 0
    assert restricted_rows[0]["payload"]["text"] is None
    assert restricted_rows[0]["payload"]["alternatives"] == []


def test_release_artifacts_and_stage_are_deterministic(tmp_path: Path) -> None:
    plan = build_publication_plan(
        _bundle(),
        dataset_id="user/dataset",
        collection_id="user/collection",
        source_dois=("10.5281/test",),
    )
    manifest = write_release_manifest(plan, tmp_path / "release.json")
    card = write_dataset_card(plan, tmp_path / "README.md")
    state = stage_publication(plan, tmp_path / "state.json")

    assert json.loads(manifest.read_text(encoding="utf-8"))["content_sha256"] == plan.content_sha256
    assert "streaming" in card.read_text(encoding="utf-8")
    assert json.loads(state.read_text(encoding="utf-8"))["status"] == "staged"
    assert stage_publication(plan, tmp_path / "state.json") == state


def test_materialization_partitions_rows_and_supports_dry_run(tmp_path: Path) -> None:
    bundle = _bundle()
    plan = build_publication_plan(
        bundle, dataset_id="user/dataset", collection_id="user/collection"
    )
    output = materialize_publication(bundle, plan, tmp_path / "release", partition_size=1)

    assert (output / "release-manifest.json").is_file()
    assert (output / "checksums.json").is_file()
    assert (output / "zenodo-handoff.json").is_file()
    assert (output / "provenance-attestation.json").is_file()
    assert (output / "completeness-report.json").is_file()
    assert (output / "sbom.json").is_file()
    assert "config_name: inventory" in (output / "README.md").read_text(encoding="utf-8")
    assert len(list((output / "tokens").glob("part-*.jsonl"))) == 1
    assert publish_hf_archive(bundle, plan, tmp_path / "dry").startswith("dry-run://")
    with pytest.raises(ValueError, match="partition_size"):
        materialize_publication(bundle, plan, tmp_path / "invalid", partition_size=0)


def test_stage_rejects_checksum_replacement(tmp_path: Path) -> None:
    first = build_publication_plan(
        _bundle(), dataset_id="user/dataset", collection_id="user/collection"
    )
    second = build_publication_plan(
        _bundle(), dataset_id="user/other", collection_id="user/collection"
    )
    stage_publication(first, tmp_path / "state.json")

    with pytest.raises(PublicationConflictError):
        stage_publication(second, tmp_path / "state.json")


def test_publish_requires_token_after_materialization(tmp_path: Path) -> None:
    plan = build_publication_plan(
        _bundle(), dataset_id="user/dataset", collection_id="user/collection"
    )
    with pytest.raises(ValueError, match="HF token"):
        publish_hf_archive(_bundle(), plan, tmp_path / "publish", dry_run=False)


def test_materialized_release_verification_records_local_and_endpoint_evidence(
    tmp_path: Path,
) -> None:
    bundle = _bundle(restricted=True)
    plan = build_publication_plan(
        bundle, dataset_id="user/dataset", collection_id="user/collection"
    )
    output = materialize_publication(bundle, plan, tmp_path / "release", partition_size=1)

    report = verify_materialized_publication(
        bundle,
        plan,
        output,
        endpoint_url="https://huggingface.co/datasets/user/dataset",
        endpoint_probe=lambda url: url.endswith("user/dataset"),
    )
    evidence = write_publication_verification(report, output / "verification.json")

    assert report.passed is True
    assert report.endpoint_status == "passed"
    assert report.restricted_content_absent is True
    assert json.loads(evidence.read_text(encoding="utf-8"))["passed"] is True


def test_materialized_release_verification_detects_source_projection_drift(tmp_path: Path) -> None:
    bundle = _bundle()
    plan = build_publication_plan(bundle, dataset_id="user/dataset", collection_id="user/collection")
    output = materialize_publication(bundle, plan, tmp_path / "release", partition_size=1)
    partition = next((output / "inventory").glob("part-*.jsonl"))
    row = json.loads(partition.read_text(encoding="utf-8"))
    row["id"] = "drifted"
    partition.write_text(json.dumps(row) + "\n", encoding="utf-8")
    write_checksums(output, output / "checksums.json")

    report = verify_materialized_publication(bundle, plan, output)

    assert report.passed is False
    assert any("source public projection" in failure for failure in report.failures)


def test_public_endpoint_probe_records_each_config_without_network() -> None:
    class Response:
        status = 200

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self, amount: int = -1) -> bytes:
            return json.dumps({"rows": [{"row": {"id": "row-1"}}]}).encode("utf-8")

    report = probe_huggingface_endpoint(
        "user/dataset",
        configs=("inventory", "tokens"),
        opener=lambda request, timeout: Response(),
    )

    assert report.passed is True
    assert report.metadata_status == 200
    assert report.viewer_statuses == {"inventory": 200, "tokens": 200}
    assert report.viewer_row_counts == {"inventory": 1, "tokens": 1}


def test_publish_uploads_materialized_folder(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import huggingface_hub

    calls: list[tuple[str, str]] = []

    class FakeApi:
        def __init__(self, *, token: str) -> None:
            calls.append(("init", token))

        def create_repo(self, **kwargs: object) -> None:
            calls.append(("create", str(kwargs["repo_id"])))

        def upload_folder(self, **kwargs: object) -> None:
            calls.append(("upload", str(kwargs["folder_path"])))

    monkeypatch.setattr(huggingface_hub, "HfApi", FakeApi)
    bundle = _bundle()
    plan = build_publication_plan(
        bundle, dataset_id="user/dataset", collection_id="user/collection"
    )

    assert publish_hf_archive(
        bundle, plan, tmp_path / "publish", token="hf_test", dry_run=False
    ).startswith("https://huggingface.co/datasets/")
    assert calls[0] == ("init", "hf_test")
    assert calls[1] == ("create", "user/dataset")
    assert calls[2][0] == "upload"
