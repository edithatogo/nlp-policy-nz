"""Validate metadata-only OCR inputs and write a deterministic report shell."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nlp_policy_nz.ocr.protocol import build_scaffold, load_manifest, load_registry, write_scaffold


def main() -> int:
    """Validate metadata inputs and write the not-run benchmark scaffold."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", type=Path, default=Path("data/track131/benchmark_manifest.json")
    )
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--fixtures", type=Path)
    parser.add_argument("--output", type=Path, default=Path(".tmp/ocr/benchmark-scaffold.json"))
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    registry = load_registry(args.registry or manifest.registry_path)
    fixture_path = args.fixtures or Path(manifest.fixture_path)
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    write_scaffold(build_scaffold(manifest, registry, fixture), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
