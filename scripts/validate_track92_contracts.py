"""Validate Track 92 candidate concept, feedback, and jurisdiction contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

CONCEPT_SCHEMA = "foio-concept-pack-v1"
FEEDBACK_SCHEMA = "foio-concept-feedback-v1"
MANIFEST_SCHEMA = "track92-jurisdiction-source-manifest-v1"
GATES = {"rights", "legal_review", "profile_owner_approval", "independent_conformance"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _required_strings(value: dict[str, Any], keys: tuple[str, ...], prefix: str) -> list[str]:
    return [f"{prefix}.{key} is required" for key in keys if not isinstance(value.get(key), str) or not value[key]]


def validate_concept_contract(value: dict[str, Any]) -> list[str]:
    """Return violations in the candidate concept-pack contract."""
    errors = _required_strings(
        value,
        ("schema_version", "status", "promotion"),
        "concept",
    )
    if value.get("schema_version") != CONCEPT_SCHEMA:
        errors.append(f"concept.schema_version must be {CONCEPT_SCHEMA}")
    if value.get("status") != "candidate" or value.get("promotion") != "no-promotion":
        errors.append("concept must remain candidate and no-promotion")
    for key in ("required_artifact_fields", "promotion_requirements", "prohibited"):
        if not isinstance(value.get(key), list) or not value[key] or not all(isinstance(item, str) and item for item in value[key]):
            errors.append(f"concept.{key} must be a non-empty string list")
    statuses = value.get("allowed_review_statuses")
    if not isinstance(statuses, list) or set(statuses) != {"candidate", "under-review", "accepted", "rejected"}:
        errors.append("concept.allowed_review_statuses must declare the complete review vocabulary")
    if set(value.get("promotion_requirements", [])) != GATES:
        errors.append("concept.promotion_requirements must declare every promotion gate")
    return errors


def validate_feedback_contract(value: dict[str, Any]) -> list[str]:
    """Return violations in the candidate feedback contract."""
    errors = _required_strings(value, ("schema_version",), "feedback")
    if value.get("schema_version") != FEEDBACK_SCHEMA:
        errors.append(f"feedback.schema_version must be {FEEDBACK_SCHEMA}")
    if value.get("candidate_only") is not True:
        errors.append("feedback.candidate_only must be true")
    fields = value.get("required_fields")
    if not isinstance(fields, list) or not fields or not all(isinstance(item, str) and item for item in fields):
        errors.append("feedback.required_fields must be a non-empty string list")
    dispositions = value.get("dispositions")
    expected = {"needs-evidence", "needs-revision", "accepted", "rejected", "deferred"}
    if not isinstance(dispositions, list) or set(dispositions) != expected:
        errors.append("feedback.dispositions must declare the complete disposition vocabulary")
    if set(value.get("promotion_requires", [])) != GATES:
        errors.append("feedback.promotion_requires must declare every promotion gate")
    return errors


def validate_jurisdiction_manifest(value: dict[str, Any]) -> list[str]:
    """Return violations in the jurisdiction source manifest."""
    errors = _required_strings(value, ("schema_version", "status", "promotion"), "manifest")
    if value.get("schema_version") != MANIFEST_SCHEMA:
        errors.append(f"manifest.schema_version must be {MANIFEST_SCHEMA}")
    if value.get("candidate_only") is not True or value.get("promotion") != "no-promotion":
        errors.append("manifest must remain candidate-only and no-promotion")
    for key in ("required_source_families", "required_fixture_families", "required_fields"):
        if not isinstance(value.get(key), list) or not value[key] or not all(isinstance(item, str) and item for item in value[key]):
            errors.append(f"manifest.{key} must be a non-empty string list")
    jurisdictions = value.get("jurisdictions")
    if not isinstance(jurisdictions, list):
        errors.append("manifest.jurisdictions must be a list")
    elif not jurisdictions:
        blockers = value.get("blockers")
        if not isinstance(blockers, list) or not blockers or not all(isinstance(item, str) and item for item in blockers):
            errors.append("empty manifest must explain its blockers")
    else:
        required = set(value["required_fields"]) if isinstance(value.get("required_fields"), list) else set()
        expected_families = set(value.get("required_source_families", []))
        observed_families: set[str] = set()
        for index, item in enumerate(jurisdictions):
            if not isinstance(item, dict):
                errors.append(f"manifest.jurisdictions[{index}] must be an object")
                continue
            missing = sorted(field for field in required if not isinstance(item.get(field), str) or not item[field])
            if missing:
                errors.append(f"manifest.jurisdictions[{index}] missing: {', '.join(missing)}")
            family = item.get("source_family")
            if isinstance(family, str):
                observed_families.add(family)
            source_hash = item.get("source_sha256")
            if not isinstance(source_hash, str) or not SHA256.fullmatch(source_hash):
                errors.append(f"manifest.jurisdictions[{index}].source_sha256 must be a 64-character SHA-256")
        missing_families = sorted(expected_families - observed_families)
        if missing_families:
            errors.append(f"manifest is missing source families: {', '.join(missing_families)}")
    return errors


def _load(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"{path}: {exc}"]
    if not isinstance(value, dict):
        return None, [f"{path} must contain a JSON object"]
    return value, []


def validate(root: Path) -> list[str]:
    """Validate every Track 92 contract under ``root``."""
    errors: list[str] = []
    for filename, validator in (
        ("concept_pack_contract.json", validate_concept_contract),
        ("feedback_contract.json", validate_feedback_contract),
        ("jurisdiction_source_manifest.json", validate_jurisdiction_manifest),
    ):
        value, load_errors = _load(root / filename)
        errors.extend(load_errors)
        if value is not None:
            errors.extend(validator(value))
    return errors


def main() -> int:
    """Run contract validation from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("data/track92"))
    args = parser.parse_args()
    errors = validate(args.root)
    sys.stdout.write(
        json.dumps({"passed": not errors, "decision": "no-promotion", "errors": errors}, indent=2, sort_keys=True)
        + "\n"
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
