"""Check the OCR artifact registry contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "registry" / "ocr_artifact.json"
HF_AUDIT_PATH = ROOT / "data" / "registry" / "huggingface_audit.json"
PUBLISHED_LIKE_MARKERS = ("published", "deposited", "registered", "accepted")
PAYLOAD_STATUS = "payload_complete_doi_pending"


def check() -> list[str]:
    """Return OCR artifact registry violations."""
    errors: list[str] = []
    if not REGISTRY_PATH.exists():
        errors.append(f"missing {REGISTRY_PATH}")
        return errors

    artifact = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    if artifact.get("schema_version") != "registry-ocr-artifact-v1":
        errors.append("ocr_artifact.json schema_version must be registry-ocr-artifact-v1")

    for path_key in ("manifest_path", "engine_registry_path", "payload_manifest_path", "zenodo_metadata_path"):
        rel_path = artifact.get(path_key)
        if not rel_path:
            errors.append(f"ocr_artifact.json missing {path_key}")
            continue
        if not (ROOT / rel_path).exists():
            errors.append(f"ocr_artifact referenced path missing: {rel_path}")

    manifest_path = artifact.get("manifest_path")
    if manifest_path and (ROOT / manifest_path).exists():
        manifest = json.loads((ROOT / manifest_path).read_text(encoding="utf-8"))
        if artifact.get("benchmark_id") != manifest.get("benchmark_id"):
            errors.append("ocr_artifact benchmark_id does not match track131 manifest")
        if artifact.get("version") != manifest.get("pipeline_version"):
            errors.append("ocr_artifact version does not match track131 manifest pipeline_version")

    hf_evidence = artifact.get("hf_evidence") or {}
    repo_id = hf_evidence.get("repo_id")
    revision = hf_evidence.get("revision")
    if not repo_id or not revision:
        errors.append("ocr_artifact hf_evidence must include repo_id and revision")
    elif HF_AUDIT_PATH.exists():
        audit = json.loads(HF_AUDIT_PATH.read_text(encoding="utf-8"))
        targets = {target["repo_id"]: target for target in audit.get("targets", [])}
        target = targets.get(repo_id)
        if target is None:
            errors.append(f"ocr_artifact hf_evidence repo_id not found in huggingface_audit.json: {repo_id}")
        elif target.get("revision") != revision:
            errors.append("ocr_artifact hf revision does not match huggingface_audit.json OCR target")

    if artifact.get("status") == PAYLOAD_STATUS:
        payload_path = ROOT / str(artifact.get("payload_manifest_path", ""))
        metadata_path = ROOT / str(artifact.get("zenodo_metadata_path", ""))
        if payload_path.exists():
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            if payload.get("artifact_version") != artifact.get("version"):
                errors.append("OCR payload artifact_version must match ocr_artifact version")
            if payload.get("benchmark_id") != artifact.get("benchmark_id"):
                errors.append("OCR payload benchmark_id must match ocr_artifact benchmark_id")
            if payload.get("hf_source") != hf_evidence:
                errors.append("OCR payload hf_source must match ocr_artifact hf_evidence")
            archive = payload.get("archive") or {}
            checksum = archive.get("sha256", "")
            if not isinstance(checksum, str) or len(checksum) != 64:
                errors.append("OCR payload archive must include a SHA-256 checksum")
            if (artifact.get("checksums") or {}).get("sha256") != checksum:
                errors.append("OCR artifact checksum must match the payload archive SHA-256")
            if not payload.get("files"):
                errors.append("OCR payload must list at least one source file")
            if (payload.get("scope") or {}).get("payload_policy") != "metadata_only":
                errors.append("OCR payload must retain the metadata_only scope")
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            if metadata.get("upload_type") != "dataset":
                errors.append("OCR Zenodo metadata upload_type must be dataset")
            if metadata.get("version") != artifact.get("version"):
                errors.append("OCR Zenodo metadata version must match ocr_artifact version")

    status = str(artifact.get("status", ""))
    status_lower = status.lower()
    if "doi_pending" in status_lower:
        if artifact.get("doi") is not None:
            errors.append("ocr_artifact doi must be null while status contains doi_pending")
        if artifact.get("deposit_url") is not None:
            errors.append("ocr_artifact deposit_url must be null while status contains doi_pending")
        blockers = artifact.get("blockers")
        if not isinstance(blockers, list) or not blockers:
            errors.append("ocr_artifact blockers must be non-empty while status contains doi_pending")

    if any(marker in status_lower for marker in PUBLISHED_LIKE_MARKERS) and (
        artifact.get("doi") is None or artifact.get("deposit_url") is None
    ):
        errors.append(
            "ocr_artifact published-like status requires both doi and deposit_url "
            "(doi_pending cannot bypass this gate)"
        )

    return errors


if __name__ == "__main__":
    problems = check()
    if problems:
        raise SystemExit("\n".join(problems))
    sys.stdout.write("ocr artifact registry: OK\n")
