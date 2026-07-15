"""FOI-O candidate adapter for pinned fyi-archive snapshots.

The adapter deliberately wraps the shared extraction manifest rather than
defining a second ontology.  Its output is a review-bound candidate bundle;
it cannot certify or promote legal findings.
"""

from __future__ import annotations

from typing import Literal

import orjson
from pydantic import BaseModel, ConfigDict, Field

from nlp_policy_nz.extraction.schemas import (
    ExtractionManifest,
    ExtractionRecord,
    extraction_manifest_from_records,
)


class FoioArchiveSnapshot(BaseModel):
    """Immutable identities required to reproduce one archive extraction."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    archive_repository: str = Field(min_length=1)
    archive_revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    archive_record_id: str = Field(min_length=1)
    archive_content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    ontology_version: str = Field(min_length=1)
    schema_version: str = Field(min_length=1)
    extraction_contract_version: str = Field(min_length=1)
    pipeline_version: str = Field(min_length=1)
    source_url: str = Field(default="https://huggingface.co/datasets/edithatogo/fyi-archive-nz")
    retrieved_at: str = Field(default="not-recorded", min_length=1)


class FoioArchiveBundle(BaseModel):
    """Portable candidate output handed to fyi-archive for review."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    producer: str = "nlp-policy-nz"
    review_status: Literal["candidate"] = "candidate"
    snapshot: FoioArchiveSnapshot
    manifest: ExtractionManifest


def build_foio_archive_bundle(
    records: list[ExtractionRecord] | tuple[ExtractionRecord, ...],
    snapshot: FoioArchiveSnapshot,
) -> FoioArchiveBundle:
    """Build a sorted, provenance-enriched candidate bundle.

    Records are required to point at the pinned archive content digest.  The
    check prevents accidental mixing of source revisions in one derived layer.
    """
    enriched: list[ExtractionRecord] = []
    for record in sorted(records, key=lambda item: item.record_id):
        if record.source_trace.source_sha256 != snapshot.archive_content_sha256:
            raise ValueError("source digest does not match pinned archive snapshot")
        attributes = dict(record.attributes)
        attributes["foio_provenance"] = snapshot.model_dump(mode="json")
        enriched.append(record.model_copy(update={"attributes": attributes}))
    return FoioArchiveBundle(
        snapshot=snapshot,
        manifest=extraction_manifest_from_records(enriched),
    )


def render_foio_archive_bundle_json(bundle: FoioArchiveBundle) -> str:
    """Render a stable JSON handoff suitable for a derived manifest."""
    return (
        orjson.dumps(bundle.model_dump(mode="json"), option=orjson.OPT_SORT_KEYS).decode("utf-8")
        + "\n"
    )


def compare_foio_baseline(
    baseline: list[ExtractionRecord] | tuple[ExtractionRecord, ...],
    candidate: list[ExtractionRecord] | tuple[ExtractionRecord, ...],
) -> dict[str, tuple[str, ...]]:
    """Report stable added, removed, relabelled, and shifted record IDs."""
    before = {record.record_id: record for record in baseline}
    after = {record.record_id: record for record in candidate}
    common = before.keys() & after.keys()
    return {
        "added": tuple(sorted(after.keys() - before.keys())),
        "removed": tuple(sorted(before.keys() - after.keys())),
        "relabelled": tuple(
            sorted(
                record_id
                for record_id in common
                if before[record_id].label != after[record_id].label
            )
        ),
        "shifted": tuple(
            sorted(
                record_id
                for record_id in common
                if before[record_id].source_trace.spans != after[record_id].source_trace.spans
            )
        ),
    }
