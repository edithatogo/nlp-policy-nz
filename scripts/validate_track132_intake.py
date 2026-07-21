"""Validate Track 132 intake evidence and emit a fail-closed report."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")
SPLITS = ("train", "dev", "test")


def _read(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _date(value: object, label: str, errors: list[str]) -> date | None:
    if not isinstance(value, str):
        errors.append(f"{label} must be an ISO date")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{label} must be an ISO date")
        return None


def _timestamp(value: object, label: str, errors: list[str]) -> None:
    if not isinstance(value, str):
        errors.append(f"{label} must be an ISO timestamp")
        return None
    try:
        datetime.fromisoformat(value)
    except ValueError:
        errors.append(f"{label} must be an ISO timestamp")


def _nonempty_strings(value: object, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        errors.append(f"{label} must be a non-empty string list")
        return []
    return value


def validate(contract: dict[str, Any], manifest: dict[str, Any], evaluation: dict[str, Any]) -> list[str]:
    """Return deterministic validation errors; absence of evidence is not fabricated."""
    errors: list[str] = []
    thresholds = contract.get("required_metrics")
    if not isinstance(thresholds, dict) or not thresholds:
        errors.append("contract must declare required metric thresholds")
        thresholds = {}
    for name, threshold in thresholds.items():
        if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
            errors.append(f"invalid threshold: {name}")
    records = manifest.get("records")
    if not isinstance(records, list):
        errors.append("manifest records must be a list")
        records = []
    people = manifest.get("people")
    authority = manifest.get("authority_records")
    reviews = manifest.get("review_decisions")
    if not all(isinstance(value, list) for value in (people, authority, reviews)):
        errors.append("people, authority_records, and review_decisions must be lists")
        people, authority, reviews = people if isinstance(people, list) else [], authority if isinstance(authority, list) else [], reviews if isinstance(reviews, list) else []

    person_roles: dict[str, str] = {}
    for item in people:
        if not isinstance(item, dict) or not isinstance(item.get("person_id"), str):
            errors.append("identity record requires person_id")
            continue
        person_id = item["person_id"]
        role = item.get("role")
        if role not in {"annotator", "adjudicator"}:
            errors.append(f"invalid identity role: {person_id}")
        if not isinstance(item.get("identity_evidence_ref"), str) or not item["identity_evidence_ref"]:
            errors.append(f"missing identity evidence: {person_id}")
        if person_id in person_roles and person_roles[person_id] != role:
            errors.append(f"identity has both annotator and adjudicator roles: {person_id}")
        person_roles[person_id] = role

    authority_by_id: dict[str, dict[str, Any]] = {}
    for item in authority:
        if not isinstance(item, dict) or not isinstance(item.get("authority_id"), str):
            errors.append("authority record requires authority_id")
            continue
        authority_id = item["authority_id"]
        start = _date(item.get("valid_from"), f"authority {authority_id} valid_from", errors)
        end = _date(item.get("valid_to"), f"authority {authority_id} valid_to", errors)
        if start and end and start > end:
            errors.append(f"authority validity is inverted: {authority_id}")
        for field in ("subject_id", "source_uri", "evidence_sha256"):
            if not isinstance(item.get(field), str) or not item[field]:
                errors.append(f"authority {authority_id} missing {field}")
        if not SHA256.fullmatch(str(item.get("evidence_sha256", ""))):
            errors.append(f"authority {authority_id} has invalid evidence_sha256")
        authority_by_id[authority_id] = item

    review_by_id: dict[str, dict[str, Any]] = {}
    for item in reviews:
        if not isinstance(item, dict) or not isinstance(item.get("decision_id"), str):
            errors.append("review decision requires decision_id")
            continue
        decision_id = item["decision_id"]
        for field in ("record_id", "adjudicator_id", "signature_ref", "signature_sha256", "signed_at"):
            if not isinstance(item.get(field), str) or not item[field]:
                errors.append(f"review {decision_id} missing {field}")
        _timestamp(item.get("signed_at"), f"review {decision_id} signed_at", errors)
        if not SHA256.fullmatch(str(item.get("signature_sha256", ""))):
            errors.append(f"review {decision_id} has invalid signature_sha256")
        if item.get("decision") not in {"accepted", "rejected", "abstain"}:
            errors.append(f"review {decision_id} has invalid decision")
        review_by_id[decision_id] = item

    seen_ids: set[str] = set()
    split_values: dict[str, dict[str, str]] = {field: {} for field in ("volume_id", "source_id", "source_sha256")}
    record_by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            errors.append("each intake record must be an object")
            continue
        missing = [field for field in contract.get("required_record_fields", []) if field not in record]
        if missing:
            errors.append(f"record {record.get('record_id', '<unknown>')} missing fields: {', '.join(missing)}")
            continue
        record_id = record["record_id"]
        if not isinstance(record_id, str) or not record_id:
            errors.append("record_id must be a non-empty string")
            continue
        if record_id in seen_ids:
            errors.append(f"duplicate record_id: {record_id}")
        seen_ids.add(record_id)
        record_by_id[record_id] = record
        split = record["split"]
        if split not in SPLITS:
            errors.append(f"invalid split: {record_id}")
            continue
        _date(record["event_date"], f"record {record_id} event_date", errors)
        for field, seen_values in split_values.items():
            value = record[field]
            if not isinstance(value, str) or not value:
                errors.append(f"record {record_id} has empty {field}")
            elif field == "source_sha256" and not SHA256.fullmatch(value):
                errors.append(f"record {record_id} has invalid source_sha256")
            previous = seen_values.setdefault(value, split)
            if previous != split:
                errors.append(f"{field} leakage across splits: {value}")
        annotators = _nonempty_strings(record["annotator_ids"], f"record {record_id} annotator_ids", errors)
        adjudicators = _nonempty_strings(record["adjudicator_ids"], f"record {record_id} adjudicator_ids", errors)
        if set(annotators) & set(adjudicators):
            errors.append(f"annotator/adjudicator role overlap: {record_id}")
        for person_id in annotators:
            if person_roles.get(person_id) != "annotator":
                errors.append(f"record {record_id} references unknown annotator identity: {person_id}")
        for person_id in adjudicators:
            if person_roles.get(person_id) != "adjudicator":
                errors.append(f"record {record_id} references unknown adjudicator identity: {person_id}")
        if not isinstance(record["annotation_ref"], str) or not record["annotation_ref"]:
            errors.append(f"missing held-out annotation: {record_id}")
        authority_ids = _nonempty_strings(record["authority_record_ids"], f"record {record_id} authority_record_ids", errors)
        event_date = _date(record["event_date"], f"record {record_id} event_date", errors)
        for authority_id in authority_ids:
            authority_item = authority_by_id.get(authority_id)
            if authority_item is None:
                errors.append(f"record {record_id} references unknown authority: {authority_id}")
                continue
            start = _date(authority_item.get("valid_from"), f"authority {authority_id} valid_from", errors)
            end = _date(authority_item.get("valid_to"), f"authority {authority_id} valid_to", errors)
            if event_date and start and end and not start <= event_date <= end:
                errors.append(f"authority validity does not cover record event_date: {record_id}")
        review_id = record["review_decision_id"]
        review_item = review_by_id.get(review_id)
        if review_item is None:
            errors.append(f"missing signed review decision: {record_id}")
        elif review_item.get("record_id") != record_id or review_item.get("adjudicator_id") not in adjudicators:
            errors.append(f"review is not bound to record adjudicator: {record_id}")

    for review_id, review in review_by_id.items():
        if review.get("record_id") not in record_by_id:
            errors.append(f"review references unknown record: {review_id}")
    metrics = evaluation.get("metrics")
    if not isinstance(metrics, dict):
        errors.append("evaluation metrics must be an object")
        metrics = {}
    for name, threshold in thresholds.items():
        value = metrics.get(name)
        if value is None:
            continue
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            errors.append(f"invalid measured metric: {name}")
        elif value < threshold:
            errors.append(f"metric below threshold: {name}")
    return sorted(set(errors))


def report(contract: dict[str, Any], manifest: dict[str, Any], evaluation: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    """Build a deterministic report, never treating metadata as measured evidence."""
    records = manifest.get("records", []) if isinstance(manifest.get("records", []), list) else []
    counts = {split: sum(item.get("split") == split for item in records if isinstance(item, dict)) for split in SPLITS}
    metrics = evaluation.get("metrics", {}) if isinstance(evaluation.get("metrics", {}), dict) else {}
    thresholds = contract.get("required_metrics", {})
    reasons = list(errors)
    if counts["test"] == 0:
        reasons.append("no held-out test records are present")
    required_evidence = all(
        isinstance(item, dict)
        and item.get("annotation_ref")
        and item.get("annotator_ids")
        and item.get("adjudicator_ids")
        and item.get("authority_record_ids")
        and item.get("review_decision_id")
        for item in records
        if isinstance(item, dict) and item.get("split") == "test"
    ) and counts["test"] > 0
    if not required_evidence:
        reasons.append("annotations, identities, authority records, and signed review decisions are incomplete")
    missing = sorted(set(thresholds) - set(metrics))
    if missing:
        reasons.append("missing measured metrics: " + ", ".join(missing))
    reasons = sorted(set(reasons))
    ready = not reasons and counts["test"] > 0
    return {
        "contract_valid": not errors,
        "manifest_valid": not errors,
        "evidence_complete": required_evidence,
        "record_counts": counts,
        "measured_metrics": dict(sorted(metrics.items())),
        "promotion_ready": ready,
        "decision": "promote" if ready else "no-promotion",
        "reasons": reasons,
    }


def main() -> int:
    """Validate intake files and write a report; invalid input returns status 1."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=Path("data/track132/intake_contract.json"))
    parser.add_argument("--manifest", type=Path, default=Path("data/track132/intake_manifest.json"))
    parser.add_argument("--evaluation", type=Path, default=Path("data/track132/evaluation_inputs.json"))
    parser.add_argument("--output", type=Path, default=Path("data/track132/intake_report.json"))
    args = parser.parse_args()
    try:
        contract = _read(args.contract)
        manifest = _read(args.manifest)
        evaluation = _read(args.evaluation)
        errors = validate(contract, manifest, evaluation)
        payload = report(contract, manifest, evaluation, errors)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        exit_code = 1 if errors else 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        sys.stderr.write(f"track132 intake error: {exc}\n")
        return 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
