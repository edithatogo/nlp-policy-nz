#!/usr/bin/env python3
"""Materialize reviewed pilot source metadata and hashes on GitHub Actions."""

from __future__ import annotations

import argparse
import json
import tempfile
from collections.abc import Callable
from pathlib import Path

if __package__:
    from scripts.cloud_ocr_worker import _download
else:
    from cloud_ocr_worker import _download


def prepare(
    source_path: Path,
    output_path: Path,
    *,
    downloader: Callable[[str, Path], str] = _download,
) -> None:
    """Download each reviewed public source only long enough to calculate its digest."""
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    items = payload.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= 3:
        raise ValueError("pilot source registry must contain between one and three items")
    materialized = []
    with tempfile.TemporaryDirectory(prefix="cloud-ocr-pilot-") as temporary:
        directory = Path(temporary)
        for index, item in enumerate(items):
            if item.get("rights_code") not in {"Apache-2.0", "NZ-Copyright-Act-1994-s27"}:
                raise ValueError("pilot item does not have an approved public-content rights code")
            if item.get("publish_eligibility") != "public_full_text":
                raise ValueError("pilot item must be approved for public full-text processing")
            digest = downloader(str(item["source_url"]), directory / f"source-{index}")
            materialized.append({**item, "source_sha256": digest})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"items": materialized}, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    """Run the GitHub-hosted pilot-manifest preparation command."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.input, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
