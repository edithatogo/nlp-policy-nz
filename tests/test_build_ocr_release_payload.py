"""Tests for the deterministic OCR evidence release packager."""

from __future__ import annotations

import hashlib
import json
import tarfile
from typing import TYPE_CHECKING

from scripts.build_ocr_release_payload import ARCHIVE_PREFIX, build_payload

if TYPE_CHECKING:
    from pathlib import Path


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_build_payload_hashes_all_source_files_and_excludes_hub_cache(tmp_path: Path) -> None:
    source = tmp_path / "source"
    (source / "reports").mkdir(parents=True)
    (source / "reports" / "run.json").write_text('{"status":"complete"}\n', encoding="utf-8")
    (source / "README.md").write_text("pilot evidence\n", encoding="utf-8")
    (source / ".cache" / "huggingface").mkdir(parents=True)
    (source / ".cache" / "huggingface" / "local.json").write_text("local\n", encoding="utf-8")

    archive = tmp_path / "payload.tar.gz"
    manifest_path = tmp_path / "manifest.json"
    metadata_path = tmp_path / "metadata.json"
    manifest = build_payload(source, archive, manifest_path, metadata_path, version="v-test")

    assert [entry["path"] for entry in manifest["files"]] == ["README.md", "reports/run.json"]
    assert manifest["archive"]["sha256"] == _digest(archive)
    assert manifest["artifact_version"] == "v-test"
    assert json.loads(metadata_path.read_text(encoding="utf-8"))["upload_type"] == "dataset"
    with tarfile.open(archive, "r:gz") as packaged:
        assert packaged.getnames() == [f"{ARCHIVE_PREFIX}/README.md", f"{ARCHIVE_PREFIX}/reports/run.json"]


def test_build_payload_is_byte_stable(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "evidence.json").write_text("{}\n", encoding="utf-8")
    first = tmp_path / "first.tar.gz"
    second = tmp_path / "second.tar.gz"
    build_payload(source, first, tmp_path / "first.json", tmp_path / "first-metadata.json")
    build_payload(source, second, tmp_path / "second.json", tmp_path / "second-metadata.json")
    assert first.read_bytes() == second.read_bytes()
