"""Check citation and Zenodo mirror manifest consistency."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "conductor" / "tracks" / "citation_zenodo_mirroring_20260714" / "mirror-manifest.json"
CITATION_PATH = ROOT / "CITATION.cff"
ZENODO_PATH = ROOT / ".zenodo.json"
HF_AUDIT_PATH = ROOT / "data" / "registry" / "huggingface_audit.json"

_DOI_IN_CFF = re.compile(r'value:\s*"(10\.\d+/zenodo\.\d+)"')


def check() -> list[str]:
    """Return citation/Zenodo mirror contract violations."""
    errors: list[str] = []
    for path in (MANIFEST_PATH, CITATION_PATH, ZENODO_PATH):
        if not path.exists():
            errors.append(f"missing {path}")
    if errors:
        return errors

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    citation = CITATION_PATH.read_text(encoding="utf-8")
    zenodo = json.loads(ZENODO_PATH.read_text(encoding="utf-8"))

    version = str(manifest.get("version", ""))
    if version != "0.1.0":
        errors.append("mirror-manifest version must be 0.1.0 for current release")
    if f"version: {version}" not in citation:
        errors.append("CITATION.cff version must match mirror-manifest version")

    if zenodo.get("title") and "nlp-policy-nz" not in str(zenodo.get("title")):
        errors.append(".zenodo.json title must describe nlp-policy-nz")

    status = str(manifest.get("zenodo_status", ""))
    version_doi = manifest.get("zenodo_version_doi")
    concept_doi = manifest.get("zenodo_concept_doi")

    if status == "pending_human_deposit":
        if version_doi is not None or concept_doi is not None:
            errors.append("pending_human_deposit requires null Zenodo DOI fields")
    elif status == "verified":
        if not version_doi or not concept_doi:
            errors.append("verified status requires zenodo_version_doi and zenodo_concept_doi")
        record_url = str(manifest.get("zenodo_record_url") or "")
        if not record_url:
            errors.append("verified status requires zenodo_record_url")
        elif version_doi:
            record_id = version_doi.rsplit(".", maxsplit=1)[-1]
            if record_id not in record_url:
                errors.append("zenodo_record_url must reference the zenodo_version_doi record id")
        if not manifest.get("tag_commit"):
            errors.append("verified status requires tag_commit")
        cff_dois = _DOI_IN_CFF.findall(citation)
        if version_doi not in cff_dois:
            errors.append("CITATION.cff DOI must match mirror-manifest zenodo_version_doi when verified")
        revisions = manifest.get("huggingface_revisions")
        if not isinstance(revisions, list) or not revisions:
            errors.append("verified status requires pinned huggingface_revisions")
        if not HF_AUDIT_PATH.exists():
            errors.append("verified status requires data/registry/huggingface_audit.json for HF pinning")
        elif isinstance(revisions, list) and revisions:
            audit = json.loads(HF_AUDIT_PATH.read_text(encoding="utf-8"))
            audit_revs = {t["repo_id"]: t["revision"] for t in audit.get("targets", [])}
            manifest_repos = {entry.get("repo_id") for entry in revisions if entry.get("repo_id")}
            for repo_id in audit_revs:
                if repo_id not in manifest_repos:
                    errors.append(f"huggingface_revisions missing audit target {repo_id}")
            for entry in revisions:
                repo_id = entry.get("repo_id")
                revision = entry.get("revision")
                if not repo_id or not revision:
                    errors.append("huggingface_revisions entries require repo_id and revision")
                    continue
                if len(revision) != 40:
                    errors.append(f"huggingface revision for {repo_id} must be a 40-char SHA")
                expected = audit_revs.get(repo_id)
                if expected is None:
                    errors.append(f"huggingface_revisions repo_id not in huggingface_audit.json: {repo_id}")
                elif expected != revision:
                    errors.append(f"huggingface revision for {repo_id} must match huggingface_audit.json")
    else:
        errors.append(f"unknown zenodo_status: {status}")

    return errors


if __name__ == "__main__":
    problems = check()
    if problems:
        raise SystemExit("\n".join(problems))
    sys.stdout.write("citation zenodo mirror: OK\n")
