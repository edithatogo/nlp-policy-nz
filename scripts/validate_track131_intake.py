"""Fail-closed validator for the Track 131 OCR benchmark intake contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40,64}$")


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bundle_file(root: Path, declared: object, label: str, errors: list[str]) -> Path | None:
    if not isinstance(declared, str) or not declared:
        errors.append(f"{label}.path: required relative path")
        return None
    root_resolved = root.resolve()
    candidate = (root / declared).resolve()
    if not candidate.is_relative_to(root_resolved):
        errors.append(f"{label}.path: path escapes bundle root")
        return None
    return candidate


def _required(value: object, path: str, errors: list[str]) -> None:
    if not value:
        errors.append(f"{path}: required evidence is missing")


def _file_pin(root: Path, item: dict[str, Any], label: str, errors: list[str]) -> None:
    _required(item.get("path"), f"{label}.path", errors)
    _required(item.get("sha256"), f"{label}.sha256", errors)
    path = _bundle_file(root, item.get("path"), label, errors)
    if path is None or not path.is_file():
        errors.append(f"{label}.path: file does not exist: {item.get('path')!s}")
        return
    expected = item.get("sha256")
    if not isinstance(expected, str) or not SHA256.fullmatch(expected):
        errors.append(f"{label}.sha256: must be a lowercase SHA-256")
    elif _hash_file(path) != expected:
        errors.append(f"{label}: SHA-256 mismatch for {item['path']}")


def validate(manifest: dict[str, Any], root: Path) -> dict[str, Any]:
    """Validate a manifest and return a deterministic machine-readable report."""
    errors: list[str] = []
    if manifest.get("schema_version") != "track131-intake-v1":
        errors.append("schema_version: must be track131-intake-v1")
    for key in ("dataset_id", "rights", "pages", "runtime", "runner"):
        _required(manifest.get(key), key, errors)

    rights = manifest.get("rights")
    if not isinstance(rights, dict):
        errors.append("rights: must be an object")
    else:
        if rights.get("status") != "cleared":
            errors.append("rights.status: only cleared is accepted")
        for key in ("basis", "evidence_path", "evidence_sha256", "reviewer", "reviewed_at"):
            _required(rights.get(key), f"rights.{key}", errors)
        _file_pin(root, {"path": rights.get("evidence_path"), "sha256": rights.get("evidence_sha256")}, "rights.evidence", errors)

    pages = manifest.get("pages")
    page_ids: set[str] = set()
    rights_path = rights.get("evidence_path") if isinstance(rights, dict) else None
    if not isinstance(pages, list) or not pages:
        errors.append("pages: at least one page is required")
        pages = []
    for index, page in enumerate(pages):
        label = f"pages[{index}]"
        if not isinstance(page, dict):
            errors.append(f"{label}: must be an object")
            continue
        page_id = page.get("page_id")
        if not isinstance(page_id, str) or not page_id:
            errors.append(f"{label}.page_id: required")
        elif page_id in page_ids:
            errors.append(f"{label}.page_id: duplicate {page_id}")
        else:
            page_ids.add(page_id)
        for key in ("source_id", "image_path", "image_sha256", "mime_type", "rights_evidence_ref", "gold_annotation_path", "gold_annotation_sha256"):
            _required(page.get(key), f"{label}.{key}", errors)
        if page.get("rights_evidence_ref") != rights_path:
            errors.append(f"{label}.rights_evidence_ref: must identify rights.evidence_path")
        for key in ("sequence", "width", "height"):
            if not isinstance(page.get(key), int) or page[key] < 1:
                errors.append(f"{label}.{key}: must be a positive integer")
        for file_key, hash_key, file_label in (("image_path", "image_sha256", "image"), ("gold_annotation_path", "gold_annotation_sha256", "gold_annotation")):
            _file_pin(root, {"path": page.get(file_key), "sha256": page.get(hash_key)}, f"{label}.{file_label}", errors)

    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict):
        errors.append("runtime: must be an object")
    else:
        engine = runtime.get("engine")
        if not isinstance(engine, dict):
            errors.append("runtime.engine: must be an object")
        else:
            for key in ("name", "version", "source_commit", "license_spdx"):
                _required(engine.get(key), f"runtime.engine.{key}", errors)
            if not isinstance(engine.get("source_commit"), str) or not COMMIT.fullmatch(str(engine.get("source_commit"))):
                errors.append("runtime.engine.source_commit: immutable hexadecimal commit required")
        for kind in ("model", "container"):
            item = runtime.get(kind)
            if not isinstance(item, dict) or not DIGEST.fullmatch(str(item.get("digest", ""))):
                errors.append(f"runtime.{kind}.digest: immutable sha256 digest required")
        sbom = runtime.get("sbom")
        if not isinstance(sbom, dict):
            errors.append("runtime.sbom: required")
        else:
            _file_pin(root, sbom, "runtime.sbom", errors)
        licenses = runtime.get("licenses")
        if not isinstance(licenses, list) or not licenses:
            errors.append("runtime.licenses: at least one pinned licence is required")
        else:
            for index, license_item in enumerate(licenses):
                if not isinstance(license_item, dict):
                    errors.append(f"runtime.licenses[{index}]: must be an object")
                    continue
                for key in ("component", "version", "spdx_id", "source_path", "source_sha256"):
                    _required(license_item.get(key), f"runtime.licenses[{index}].{key}", errors)
                _file_pin(root, {"path": license_item.get("source_path"), "sha256": license_item.get("source_sha256")}, f"runtime.licenses[{index}]", errors)

    runner = manifest.get("runner")
    if not isinstance(runner, dict):
        errors.append("runner: must be an object")
    else:
        for key in ("provider", "workflow_ref", "quota_policy"):
            _required(runner.get(key), f"runner.{key}", errors)
        if runner.get("no_cost") is not True:
            errors.append("runner.no_cost: must be true")
        if runner.get("paid_fallback") is not False:
            errors.append("runner.paid_fallback: must be false")

    return {"contract": "track131-intake-v1", "dataset_id": manifest.get("dataset_id"), "passed": not errors, "error_count": len(errors), "errors": errors, "page_count": len(pages), "checked_page_ids": sorted(page_ids)}


def main() -> int:
    """Parse arguments, persist the report, and return the fail-closed status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report: dict[str, Any]
    try:
        loaded = json.loads(args.manifest.read_text(encoding="utf-8"))
        report = validate(loaded, args.root) if isinstance(loaded, dict) else {"contract": "track131-intake-v1", "passed": False, "error_count": 1, "errors": ["manifest: top-level JSON object required"]}
    except (OSError, json.JSONDecodeError) as exc:
        report = {"contract": "track131-intake-v1", "passed": False, "error_count": 1, "errors": [f"manifest: unreadable or invalid JSON: {exc}"]}
    try:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as exc:
        sys.stderr.write(f"could not write validation report: {exc}\n")
        return 2
    sys.stdout.write(json.dumps(report, sort_keys=True) + "\n")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
