#!/usr/bin/env python3
"""Rights-gated CPU OCR worker for the CloudRunPlan container contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

MAX_SOURCE_BYTES = 50 * 1024 * 1024


def _safe_item_name(value: str) -> str:
    """Return a filesystem-safe, deterministic item name."""
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip(".-")
    if not name:
        raise ValueError("item_id has no filesystem-safe characters")
    return name[:120]


def _download(url: str, target: Path) -> str:
    """Download one public source with a hard size limit and return its SHA-256."""
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("pilot sources must use an absolute HTTPS URL")
    request = urllib.request.Request(  # noqa: S310 - scheme and host validated above
        url, headers={"User-Agent": "nlp-policy-nz-cloud-ocr/1.0"}
    )
    digest = hashlib.sha256()
    size = 0
    with urllib.request.urlopen(  # noqa: S310 - request contains a validated HTTPS URL
        request, timeout=60
    ) as response, target.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_SOURCE_BYTES:
                raise ValueError("source exceeds 50 MiB pilot limit")
            digest.update(chunk)
            output.write(chunk)
    return digest.hexdigest()


def _ocr_source(source: Path, work_dir: Path) -> str:
    """OCR a PDF or image using pinned container tools."""
    pages_dir = work_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    if source.read_bytes()[:5] == b"%PDF-":
        subprocess.run(
            ["pdftoppm", "-png", "-r", "200", str(source), str(pages_dir / "page")],
            check=True,
            capture_output=True,
        )
        pages = sorted(pages_dir.glob("page-*.png"))
    else:
        image = pages_dir / "page-1"
        shutil.copyfile(source, image)
        pages = [image]
    if not pages:
        raise ValueError("source produced no OCR pages")
    text = []
    for page in pages:
        result = subprocess.run(
            ["tesseract", str(page), "stdout", "-l", "eng", "--psm", "1"],
            check=True,
            capture_output=True,
            text=True,
        )
        text.append(result.stdout.strip())
    output = "\n\n".join(part for part in text if part).strip()
    if len(output) < 20:
        raise ValueError("OCR output is unexpectedly empty")
    return output + "\n"


def _load_items(plan_path: Path) -> list[dict[str, Any]]:
    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    plan = payload.get("plan", payload)
    items = plan.get("work_manifest", {}).get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("plan contains no work_manifest items")
    return items


def run(plan_path: Path, results_path: Path, output_dir: Path) -> int:
    """Execute all eligible work items and write metadata-only transitions."""
    output_dir.mkdir(parents=True, exist_ok=True)
    transitions: list[dict[str, str]] = []
    for item in _load_items(plan_path):
        item_id = str(item["item_id"])
        try:
            if not item.get("content_allowed") or item.get("publication_decision") != "public_full_text":
                raise ValueError("rights gate does not allow full-text processing")
            content_address = str(item.get("content_address", ""))
            if not content_address.startswith("sha256:"):
                raise ValueError("public pilot requires a SHA-256 content address")
            with tempfile.TemporaryDirectory(prefix="cloud-ocr-") as temporary:
                work_dir = Path(temporary)
                source = work_dir / "source"
                actual_digest = _download(str(item["source_url"]), source)
                if actual_digest != content_address.removeprefix("sha256:"):
                    raise ValueError("source SHA-256 does not match the reviewed manifest")
                text = _ocr_source(source, work_dir)
            text_path = output_dir / f"{_safe_item_name(item_id)}.txt"
            text_path.write_text(text, encoding="utf-8")
            output_digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            transitions.extend(
                [
                    {"item_id": item_id, "state": "processed", "output_digest": f"sha256:{output_digest}"},
                    {"item_id": item_id, "state": "reviewed"},
                    {"item_id": item_id, "state": "published"},
                ]
            )
        except (KeyError, OSError, subprocess.SubprocessError, ValueError) as error:
            error_code = hashlib.sha256(type(error).__name__.encode("utf-8")).hexdigest()[:12]
            transitions.append({"item_id": item_id, "state": "failed", "error_code": error_code})
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(
        json.dumps({"schema_version": "1.0.0", "engine": "tesseract-cpu", "results": transitions}, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return 0


def main() -> int:
    """Run the container command-line contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("/work/worker"))
    args = parser.parse_args()
    return run(args.plan, args.results, args.output_dir)


if __name__ == "__main__":
    raise SystemExit(main())
