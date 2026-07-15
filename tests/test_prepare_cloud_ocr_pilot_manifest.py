from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.prepare_cloud_ocr_pilot_manifest import prepare


def test_prepare_materializes_reviewed_public_source_hash(tmp_path: Path) -> None:
    source = tmp_path / "sources.json"
    source.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "item_id": "item-1",
                        "source_url": "https://example.test/public.pdf",
                        "rights_code": "NZ-Copyright-Act-1994-s27",
                        "publish_eligibility": "public_full_text",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "items.json"
    prepare(source, output, downloader=lambda _url, _target: "a" * 64)
    item = json.loads(output.read_text(encoding="utf-8"))["items"][0]
    assert item["source_sha256"] == "a" * 64


def test_prepare_rejects_unreviewed_rights(tmp_path: Path) -> None:
    source = tmp_path / "sources.json"
    source.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "source_url": "https://example.test/unknown.pdf",
                        "rights_code": "unknown",
                        "publish_eligibility": "metadata_only",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="approved public-content rights code"):
        prepare(source, tmp_path / "output.json", downloader=lambda _url, _target: "a" * 64)
