"""Canonical NZ legislation source inventory helpers for Track 76."""

from __future__ import annotations

import json
import os
import platform
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parents[3]
TRACK76_DIR = ROOT / "data" / "track76"
FIXTURE_PATH = TRACK76_DIR / "source_inventory_fixtures.json"
DEFAULT_JSON_PATH = TRACK76_DIR / "source_inventory.json"
DEFAULT_MARKDOWN_PATH = TRACK76_DIR / "source_inventory.md"
DEFAULT_PARQUET_PATH = TRACK76_DIR / "source_inventory.parquet"

SourceInventoryStatus = Literal[
    "available",
    "redirected",
    "pdf_only",
    "malformed",
    "access_blocked",
    "unavailable",
]
SourceInventoryGapType = Literal[
    "redirected",
    "pdf_only",
    "malformed",
    "access_blocked",
    "unavailable",
]
SourceInventoryGapStatus = Literal["known", "in_progress", "closed"]


@dataclass(frozen=True, slots=True)
class SourceInventoryRecord:
    """One durable source-location record in the legislation inventory."""

    inventory_id: str
    citation_path: str
    source_url: str
    source_type: str
    document_kind: str
    jurisdiction: str
    title: str
    status: SourceInventoryStatus
    retrieved_at: str
    checksum_sha256: str | None = None
    version: str | None = None
    effective_from: str | None = None
    effective_to: str | None = None
    rights_note: str | None = None
    update_policy: str = ""
    redirect_target: str | None = None
    known_gap_id: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready dictionary."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceInventoryKnownGap:
    """Known inventory gap or retrieval blocker."""

    gap_id: str
    citation_path: str
    source_url: str
    source_type: str
    document_kind: str
    gap_type: SourceInventoryGapType
    status: SourceInventoryGapStatus = "known"
    description: str = ""
    update_policy: str = ""
    record_inventory_id: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready dictionary."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceInventorySummary:
    """Stable summary counts for a source inventory manifest."""

    total_records: int
    available_records: int
    status_counts: dict[str, int]
    document_kind_counts: dict[str, int]
    citation_paths: tuple[str, ...]
    known_gap_count: int
    fixture_bounded: bool
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready dictionary."""
        payload = asdict(self)
        payload["citation_paths"] = list(self.citation_paths)
        return payload


@dataclass(frozen=True, slots=True)
class SourceInventoryLiveProbeReport:
    """Report describing whether the optional live probe ran."""

    platform_name: str
    ci: bool
    include_live_probe: bool
    status: Literal["passed", "skipped"]
    skip_reason: str | None
    probe_mode: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready dictionary."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceInventoryManifest:
    """Deterministic legislation source inventory for rules-as-code planning."""

    schema_version: str
    producer: str
    fixture_path: str
    generated_at: str
    claim_boundary: str
    records: tuple[SourceInventoryRecord, ...]
    known_gaps: tuple[SourceInventoryKnownGap, ...]
    summary: SourceInventorySummary

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready dictionary."""
        payload = asdict(self)
        payload["records"] = [record.to_dict() for record in self.records]
        payload["known_gaps"] = [gap.to_dict() for gap in self.known_gaps]
        payload["summary"] = self.summary.to_dict()
        return payload


def default_source_inventory_manifest() -> SourceInventoryManifest:
    """Build the default inventory manifest from checked-in fixture metadata."""
    payload = _load_fixture_payload()
    records = tuple(_record_from_fixture(item, generated_at=payload["generated_at"]) for item in payload["records"])
    known_gaps = tuple(_gap_from_record(record) for record in records if record.status != "available")
    summary = _build_summary(records, known_gaps, claim_boundary=str(payload["claim_boundary"]))
    manifest = SourceInventoryManifest(
        schema_version=str(payload.get("schema_version", "1.0")),
        producer="nlp-policy-nz",
        fixture_path=str(FIXTURE_PATH.relative_to(ROOT).as_posix()),
        generated_at=str(payload["generated_at"]),
        claim_boundary=str(payload["claim_boundary"]),
        records=records,
        known_gaps=known_gaps,
        summary=summary,
    )
    valid, errors = validate_source_inventory_manifest(manifest)
    if not valid:
        raise ValueError("; ".join(errors))
    return manifest


def detect_source_inventory_live_probe_report(
    *,
    include_live_probe: bool = False,
    platform_name: str | None = None,
    ci: bool | None = None,
) -> SourceInventoryLiveProbeReport:
    """Report whether the optional live inventory probe is eligible to run."""
    detected_platform = platform_name or platform.system()
    detected_ci = _env_flag("CI") if ci is None else ci
    if not include_live_probe:
        return SourceInventoryLiveProbeReport(
            platform_name=detected_platform,
            ci=detected_ci,
            include_live_probe=False,
            status="skipped",
            skip_reason="Live probing is opt-in and disabled by default.",
            probe_mode="fixture-only",
        )
    if detected_platform != "Linux":
        return SourceInventoryLiveProbeReport(
            platform_name=detected_platform,
            ci=detected_ci,
            include_live_probe=True,
            status="skipped",
            skip_reason=f"Live probing is Linux-only; detected {detected_platform}.",
            probe_mode="linux-only",
        )
    if detected_ci:
        return SourceInventoryLiveProbeReport(
            platform_name=detected_platform,
            ci=detected_ci,
            include_live_probe=True,
            status="skipped",
            skip_reason="Live probing is skipped in GitHub Actions.",
            probe_mode="fixture-only",
        )
    return SourceInventoryLiveProbeReport(
        platform_name=detected_platform,
        ci=detected_ci,
        include_live_probe=True,
        status="passed",
        skip_reason=None,
        probe_mode="linux-live",
    )


def validate_source_inventory_manifest(
    manifest: SourceInventoryManifest,
) -> tuple[bool, tuple[str, ...]]:
    """Return whether the manifest is structurally valid and gap-complete."""
    errors: list[str] = []
    if manifest.summary.total_records != len(manifest.records):
        errors.append("summary total_records does not match record count")
    if manifest.summary.known_gap_count != len(manifest.known_gaps):
        errors.append("summary known_gap_count does not match known gap count")

    expected_status_counts: dict[str, int] = {}
    expected_kind_counts: dict[str, int] = {}
    expected_paths = sorted({record.citation_path for record in manifest.records})
    seen_ids: set[str] = set()
    for record in manifest.records:
        if record.inventory_id in seen_ids:
            errors.append(f"duplicate inventory id: {record.inventory_id}")
        seen_ids.add(record.inventory_id)
        expected_status_counts[record.status] = expected_status_counts.get(record.status, 0) + 1
        expected_kind_counts[record.document_kind] = expected_kind_counts.get(record.document_kind, 0) + 1
        if record.status == "available" and record.checksum_sha256 is None:
            errors.append(f"missing checksum for available record: {record.inventory_id}")
        if record.status == "redirected" and record.redirect_target is None:
            errors.append(f"missing redirect target for redirected record: {record.inventory_id}")
        if record.status != "available" and record.known_gap_id is None:
            errors.append(f"missing known gap id for record: {record.inventory_id}")
    if manifest.summary.status_counts != expected_status_counts:
        errors.append("summary status_counts do not match record counts")
    if manifest.summary.document_kind_counts != expected_kind_counts:
        errors.append("summary document_kind_counts do not match record counts")
    if tuple(expected_paths) != manifest.summary.citation_paths:
        errors.append("summary citation_paths do not match record paths")
    if len(manifest.known_gaps) != len({gap.gap_id for gap in manifest.known_gaps}):
        errors.append("duplicate known gap ids")
    for gap in manifest.known_gaps:
        if gap.record_inventory_id not in seen_ids:
            errors.append(f"gap references unknown inventory id: {gap.record_inventory_id}")
    return (not errors, tuple(errors))


def render_source_inventory_json(manifest: SourceInventoryManifest | None = None) -> str:
    """Render the inventory manifest as deterministic JSON."""
    resolved = manifest or default_source_inventory_manifest()
    return json.dumps(resolved.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_source_inventory_markdown(manifest: SourceInventoryManifest | None = None) -> str:
    """Render a concise markdown evidence summary for the inventory."""
    resolved = manifest or default_source_inventory_manifest()
    lines = [
        "# Track 76 Source Inventory",
        "",
        f"- Schema version: {resolved.schema_version}",
        f"- Producer: {resolved.producer}",
        f"- Fixture path: {resolved.fixture_path}",
        f"- Generated at: {resolved.generated_at}",
        f"- Fixture bounded: {resolved.summary.fixture_bounded}",
        "",
        "## Claim boundary",
        "",
        resolved.claim_boundary,
        "",
        "## Status counts",
    ]
    for status, count in sorted(resolved.summary.status_counts.items()):
        lines.append(f"- {status}: {count}")
    lines.extend(["", "## Records", ""])
    for record in resolved.records:
        checksum = record.checksum_sha256 or "missing"
        lines.append(
            f"- {record.inventory_id} | {record.document_kind} | {record.status} | "
            f"{record.citation_path} | {checksum}"
        )
    lines.extend(["", "## Known gaps", ""])
    for gap in resolved.known_gaps:
        lines.append(f"- {gap.gap_id}: {gap.description}")
    lines.extend(["", "## Live probe", ""])
    report = detect_source_inventory_live_probe_report()
    lines.append(f"- status: {report.status}")
    lines.append(f"- skip reason: {report.skip_reason or 'none'}")
    return "\n".join(lines) + "\n"


def build_source_inventory_rows(
    manifest: SourceInventoryManifest | None = None,
) -> list[dict[str, Any]]:
    """Return a flat row set that can be written to Parquet."""
    resolved = manifest or default_source_inventory_manifest()
    rows: list[dict[str, Any]] = []
    for record in resolved.records:
        rows.append(
            {
                **record.to_dict(),
                "source_inventory_schema_version": resolved.schema_version,
                "fixture_path": resolved.fixture_path,
                "generated_at": resolved.generated_at,
            }
        )
    return rows


def write_source_inventory_parquet(
    output_path: str | Path,
    manifest: SourceInventoryManifest | None = None,
) -> Path:
    """Write the source inventory as a deterministic Parquet table."""
    from polars import DataFrame  # imported lazily to keep import-time dependencies light

    path = Path(output_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    table = DataFrame(build_source_inventory_rows(manifest))
    table.write_parquet(path)
    return path


def write_source_inventory_artifacts(
    output_dir: str | Path,
    manifest: SourceInventoryManifest | None = None,
) -> dict[str, Path]:
    """Write the standard Track 76 artifact bundle to disk."""
    resolved = manifest or default_source_inventory_manifest()
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "source_inventory.json"
    markdown_path = output / "source_inventory.md"
    parquet_path = output / "source_inventory.parquet"
    json_path.write_text(render_source_inventory_json(resolved), encoding="utf-8")
    markdown_path.write_text(render_source_inventory_markdown(resolved), encoding="utf-8")
    write_source_inventory_parquet(parquet_path, resolved)
    return {
        "source_inventory.json": json_path,
        "source_inventory.md": markdown_path,
        "source_inventory.parquet": parquet_path,
    }


def _load_fixture_payload() -> dict[str, Any]:
    """Load the checked-in fixture contract from disk."""
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _record_from_fixture(item: dict[str, Any], *, generated_at: str) -> SourceInventoryRecord:
    """Convert one fixture row into a manifest record."""
    source_text = item.get("source_text")
    checksum = _sha256(source_text) if isinstance(source_text, str) and source_text else None
    return SourceInventoryRecord(
        inventory_id=str(item["inventory_id"]),
        citation_path=str(item["citation_path"]),
        source_url=str(item["source_url"]),
        source_type=str(item["source_type"]),
        document_kind=str(item["document_kind"]),
        jurisdiction=str(item["jurisdiction"]),
        title=str(item["title"]),
        status=str(item["status"]),
        retrieved_at=str(item.get("retrieved_at", generated_at)),
        checksum_sha256=checksum,
        version=_optional_str(item.get("version")),
        effective_from=_optional_str(item.get("effective_from")),
        effective_to=_optional_str(item.get("effective_to")),
        rights_note=_optional_str(item.get("rights_note")),
        update_policy=str(item.get("update_policy", "")),
        redirect_target=_optional_str(item.get("redirect_target")),
        known_gap_id=_optional_str(item.get("known_gap_id")),
        notes=str(item.get("notes", "")),
    )


def _gap_from_record(record: SourceInventoryRecord) -> SourceInventoryKnownGap:
    """Create a gap ratchet entry for any non-available record."""
    gap_type = _gap_type_for_status(record.status)
    return SourceInventoryKnownGap(
        gap_id=f"{record.inventory_id}:{gap_type}",
        citation_path=record.citation_path,
        source_url=record.source_url,
        source_type=record.source_type,
        document_kind=record.document_kind,
        gap_type=gap_type,
        status="known",
        description=record.notes or f"{record.document_kind} source is {record.status}.",
        update_policy=record.update_policy,
        record_inventory_id=record.inventory_id,
        notes=record.notes,
    )


def _build_summary(
    records: tuple[SourceInventoryRecord, ...],
    known_gaps: tuple[SourceInventoryKnownGap, ...],
    *,
    claim_boundary: str,
) -> SourceInventorySummary:
    """Summarize counts and status buckets."""
    status_counts: dict[str, int] = {}
    kind_counts: dict[str, int] = {}
    available = 0
    for record in records:
        status_counts[record.status] = status_counts.get(record.status, 0) + 1
        kind_counts[record.document_kind] = kind_counts.get(record.document_kind, 0) + 1
        if record.status == "available":
            available += 1
    citation_paths = tuple(sorted(record.citation_path for record in records))
    return SourceInventorySummary(
        total_records=len(records),
        available_records=available,
        status_counts=status_counts,
        document_kind_counts=kind_counts,
        citation_paths=citation_paths,
        known_gap_count=len(known_gaps),
        fixture_bounded=True,
        claim_boundary=claim_boundary,
    )


def _gap_type_for_status(status: SourceInventoryStatus) -> SourceInventoryGapType:
    """Map a record status to the corresponding known-gap type."""
    if status == "available":
        raise ValueError("available sources do not create gaps")
    return status


def _optional_str(value: object) -> str | None:
    """Convert blank values to None and preserve non-empty strings."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _sha256(text: str) -> str:
    """Return a lowercase SHA-256 digest for fixture source text."""
    return sha256(text.encode("utf-8")).hexdigest()


def _env_flag(name: str) -> bool:
    """Return whether an environment variable is truthy."""
    return os.getenv(name, "").casefold() in {"1", "true", "yes"}


__all__ = [
    "DEFAULT_JSON_PATH",
    "DEFAULT_MARKDOWN_PATH",
    "DEFAULT_PARQUET_PATH",
    "FIXTURE_PATH",
    "SourceInventoryGapStatus",
    "SourceInventoryGapType",
    "SourceInventoryKnownGap",
    "SourceInventoryLiveProbeReport",
    "SourceInventoryManifest",
    "SourceInventoryRecord",
    "SourceInventorySummary",
    "build_source_inventory_rows",
    "default_source_inventory_manifest",
    "detect_source_inventory_live_probe_report",
    "render_source_inventory_json",
    "render_source_inventory_markdown",
    "validate_source_inventory_manifest",
    "write_source_inventory_artifacts",
    "write_source_inventory_parquet",
]
