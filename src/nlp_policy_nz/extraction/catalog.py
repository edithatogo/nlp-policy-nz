"""SQLite catalog for extraction manifest summaries and source staleness audits."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal
from uuid import uuid4

from nlp_policy_nz.axiom import source_sha256

if TYPE_CHECKING:
    from collections.abc import Mapping

    from nlp_policy_nz.extraction.schemas import ExtractionManifest

StalenessStatus = Literal["current", "stale", "missing"]


@dataclass(frozen=True)
class CatalogRun:
    """One extraction manifest run recorded in the local catalog."""

    run_id: str
    schema_version: str
    producer: str
    total_records: int


@dataclass(frozen=True)
class CatalogStalenessReport:
    """Non-mutating staleness result for one cataloged source identity."""

    citation_path: str
    status: StalenessStatus
    pinned_sha256: str
    current_sha256: str | None = None
    record_count: int = 0


def initialise_extraction_catalog(db_path: str | Path) -> Path:
    """Create the extraction catalog schema if needed and return its path."""
    path = Path(db_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS extraction_runs (
                run_id TEXT PRIMARY KEY,
                schema_version TEXT NOT NULL,
                producer TEXT NOT NULL,
                total_records INTEGER NOT NULL,
                manifest_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS extraction_records (
                run_id TEXT NOT NULL,
                record_id TEXT NOT NULL,
                family TEXT NOT NULL,
                citation_path TEXT NOT NULL,
                source_sha256 TEXT NOT NULL,
                label TEXT NOT NULL,
                PRIMARY KEY (run_id, record_id),
                FOREIGN KEY (run_id) REFERENCES extraction_runs(run_id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_extraction_records_source
                ON extraction_records (citation_path, source_sha256);
            """
        )
    return path


def write_manifest_to_catalog(
    db_path: str | Path,
    manifest: ExtractionManifest,
    *,
    run_id: str | None = None,
) -> str:
    """Persist an extraction manifest summary and record source identities."""
    path = initialise_extraction_catalog(db_path)
    catalog_run_id = run_id or f"run-{uuid4()}"
    manifest_json = manifest.model_dump_json()
    with _connect(path) as connection:
        connection.execute(
            """
            INSERT INTO extraction_runs (
                run_id, schema_version, producer, total_records, manifest_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                catalog_run_id,
                manifest.schema_version,
                manifest.producer,
                manifest.summary.total_records,
                manifest_json,
            ),
        )
        connection.executemany(
            """
            INSERT INTO extraction_records (
                run_id, record_id, family, citation_path, source_sha256, label
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    catalog_run_id,
                    record.record_id,
                    record.family.value,
                    record.source_trace.citation_path,
                    record.source_trace.source_sha256,
                    record.label,
                )
                for record in manifest.records
            ],
        )
    return catalog_run_id


def list_catalog_runs(db_path: str | Path) -> list[CatalogRun]:
    """Return extraction catalog runs in insertion order."""
    path = initialise_extraction_catalog(db_path)
    with _connect(path) as connection:
        rows = connection.execute(
            """
            SELECT run_id, schema_version, producer, total_records
            FROM extraction_runs
            ORDER BY rowid
            """
        ).fetchall()
    return [
        CatalogRun(
            run_id=row["run_id"],
            schema_version=row["schema_version"],
            producer=row["producer"],
            total_records=row["total_records"],
        )
        for row in rows
    ]


def report_catalog_source_staleness(
    db_path: str | Path,
    current_sources: Mapping[str, str],
) -> list[CatalogStalenessReport]:
    """Compare cataloged source hashes against current source text."""
    path = initialise_extraction_catalog(db_path)
    with _connect(path) as connection:
        rows = connection.execute(
            """
            SELECT citation_path, source_sha256, COUNT(*) AS record_count
            FROM extraction_records
            GROUP BY citation_path, source_sha256
            ORDER BY citation_path, source_sha256
            """
        ).fetchall()
    reports: list[CatalogStalenessReport] = []
    for row in rows:
        citation_path = row["citation_path"]
        pinned_sha256 = row["source_sha256"]
        current_text = current_sources.get(citation_path)
        if current_text is None:
            reports.append(
                CatalogStalenessReport(
                    citation_path=citation_path,
                    status="missing",
                    pinned_sha256=pinned_sha256,
                    record_count=row["record_count"],
                )
            )
            continue
        current_sha256 = source_sha256(current_text)
        reports.append(
            CatalogStalenessReport(
                citation_path=citation_path,
                status="current" if current_sha256 == pinned_sha256 else "stale",
                pinned_sha256=pinned_sha256,
                current_sha256=current_sha256,
                record_count=row["record_count"],
            )
        )
    return reports


def _connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
