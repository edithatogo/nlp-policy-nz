"""Runnable, fail-closed assurance harness for rights-aware archive exports."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from nlp_policy_nz.archive.schema import (  # noqa: E402
    AccessClass,
    ArchiveAssertion,
    ArchiveBundle,
    ArchiveDocument,
    ArchiveEmbedding,
    ArchiveLine,
    ArchivePage,
    ArchiveRegion,
    ArchiveSource,
    ArchiveSpan,
    ArchiveSpeech,
    ArchiveTable,
    ArchiveToken,
    CoordinateBox,
)
from nlp_policy_nz.archive.serializers import (  # noqa: E402
    write_json,
    write_jsonl,
    write_jsonld,
    write_markdown,
    write_parquet,
    write_rdf,
)

CANARY = "RESTRICTED_ARCHIVE_ASSURANCE_CANARY"
VECTOR_CANARIES = (0.314159, 0.271828)
SERIALIZERS: tuple[tuple[str, Callable[[ArchiveBundle, Path], Path], str], ...] = (
    ("json", write_json, "archive.json"),
    ("jsonl", write_jsonl, "archive.jsonl"),
    ("jsonld", write_jsonld, "archive.jsonld"),
    ("markdown", write_markdown, "archive.md"),
    ("parquet", write_parquet, "archive.parquet"),
    ("rdf", write_rdf, "archive.ttl"),
)


class AssuranceError(RuntimeError):
    """Raised when an assurance lane cannot prove its contract."""


def mixed_bundle(width: int = 4) -> ArchiveBundle:
    """Build a deterministic graph with both direct and inherited restrictions."""
    sources: list[ArchiveSource] = []
    documents: list[ArchiveDocument] = []
    pages: list[ArchivePage] = []
    regions: list[ArchiveRegion] = []
    spans: list[ArchiveSpan] = []
    lines: list[ArchiveLine] = []
    tokens: list[ArchiveToken] = []
    speeches: list[ArchiveSpeech] = []
    tables: list[ArchiveTable] = []
    embeddings: list[ArchiveEmbedding] = []
    assertions: list[ArchiveAssertion] = []

    for index in range(width):
        restricted = index % 2 == 0
        access = AccessClass.RESTRICTED if restricted else AccessClass.PUBLIC
        suffix = str(index)
        source_id = f"source-{suffix}"
        document_id = f"document-{suffix}"
        page_id = f"page-{suffix}"
        region_id = f"region-{suffix}"
        span_id = f"span-{suffix}"
        line_id = f"line-{suffix}"
        token_id = f"token-{suffix}"
        speech_id = f"speech-{suffix}"
        table_id = f"table-{suffix}"
        assertion_id = f"assertion-{suffix}"
        embedding_id = f"embedding-{suffix}"
        text = CANARY if restricted else f"PUBLIC-{suffix}"

        sources.append(
            ArchiveSource(
                source_id=source_id,
                uri=f"https://example.test/{source_id}",
                sha256=(f"{index + 1:064x}"),
                access_class=access,
                rights_code="restricted-rights" if restricted else "open",
            )
        )
        documents.append(ArchiveDocument(document_id=document_id, source_id=source_id, title=text))
        box = CoordinateBox(x0=0, y0=0, x1=100, y1=200, space="original")
        normalized = CoordinateBox(x0=0, y0=0, x1=1, y1=1, space="normalized")
        pages.append(
            ArchivePage(
                page_id=page_id,
                document_id=document_id,
                page_number=1,
                original_bbox=box,
                normalized_bbox=normalized,
            )
        )
        regions.append(ArchiveRegion(region_id=region_id, page_id=page_id, kind="paragraph"))
        spans.append(
            ArchiveSpan(
                span_id=span_id,
                page_id=page_id,
                start=0,
                end=5,
                text=text,
                access_class=access if index % 3 == 0 else AccessClass.PUBLIC,
            )
        )
        lines.append(
            ArchiveLine(
                line_id=line_id,
                region_id=region_id,
                span_id=span_id,
                text=text,
                access_class=AccessClass.PUBLIC,
            )
        )
        tokens.append(
            ArchiveToken(
                token_id=token_id,
                line_id=line_id,
                text=text,
                confidence=0.9,
                alternatives=(text,),
                access_class=AccessClass.RESTRICTED if restricted else AccessClass.PUBLIC,
            )
        )
        speeches.append(
            ArchiveSpeech(
                speech_id=speech_id,
                page_id=page_id,
                text=text,
                span_ids=(span_id,),
                access_class=AccessClass.PUBLIC,
            )
        )
        tables.append(
            ArchiveTable(
                table_id=table_id,
                page_id=page_id,
                span_ids=(span_id,),
                cell_count=1,
                access_class=AccessClass.PUBLIC,
            )
        )
        embeddings.append(
            ArchiveEmbedding(
                embedding_id=embedding_id,
                target_id=speech_id,
                model_id="assurance-model",
                vector_dim=2,
                values=VECTOR_CANARIES if restricted else (0.11, 0.22),
                access_class=AccessClass.PUBLIC,
            )
        )
        assertions.append(
            ArchiveAssertion(
                assertion_id=assertion_id,
                subject_id=speech_id,
                predicate="mentions",
                object_text=text,
                span_ids=(span_id,),
                access_class=AccessClass.RESTRICTED if restricted else AccessClass.PUBLIC,
            )
        )

    return ArchiveBundle(
        schema_version="1.0.0",
        sources=tuple(sources),
        documents=tuple(documents),
        pages=tuple(pages),
        regions=tuple(regions),
        spans=tuple(spans),
        lines=tuple(lines),
        tokens=tuple(tokens),
        speeches=tuple(speeches),
        tables=tuple(tables),
        embeddings=tuple(embeddings),
        assertions=tuple(assertions),
    )


def check_serializer_canaries(bundle: ArchiveBundle, output_dir: Path) -> dict[str, str]:
    """Run every public serializer and reject text or vector canary leakage."""
    projected = bundle.public_projection()
    restricted_embeddings = [
        item for item in projected.embeddings if item.values == VECTOR_CANARIES
    ]
    if restricted_embeddings:
        raise AssuranceError("public projection retained restricted embedding values")
    results: dict[str, str] = {}
    for name, writer, filename in SERIALIZERS:
        destination = writer(bundle, output_dir / filename)
        payload = destination.read_bytes()
        decoded = payload.decode("utf-8", errors="ignore")
        if CANARY in decoded or any(str(value) in decoded for value in VECTOR_CANARIES):
            raise AssuranceError(f"{name} serializer leaked a restricted canary")
        if not payload:
            raise AssuranceError(f"{name} serializer produced an empty archive")
        results[name] = "passed"
    return results


def check_compatibility(bundle: ArchiveBundle, output_dir: Path) -> dict[str, str]:
    """Verify stable public round-trips and an explicit private compatibility path."""
    public_path = write_json(bundle, output_dir / "compatibility.public.json")
    public = ArchiveBundle.model_validate_json(public_path.read_text(encoding="utf-8"))
    if public == bundle:
        raise AssuranceError("public compatibility export unexpectedly retained restrictions")
    private_path = write_json(bundle, output_dir / "compatibility.private.json", public=False)
    private = ArchiveBundle.model_validate_json(private_path.read_text(encoding="utf-8"))
    if private != bundle or CANARY not in private_path.read_text(encoding="utf-8"):
        raise AssuranceError("private compatibility export changed or lost restricted data")
    return {"public_round_trip": "passed", "private_round_trip": "passed"}


def check_performance() -> dict[str, float]:
    """Check deterministic scaling and a generous wall-clock ceiling."""
    timings: dict[int, float] = {}
    for width in (32, 64):
        bundle = mixed_bundle(width)
        started = time.perf_counter()
        for _ in range(3):
            bundle.public_projection()
        elapsed = time.perf_counter() - started
        timings[width] = elapsed
    ratio = timings[64] / max(timings[32], 1e-9)
    if timings[64] > 5.0 or ratio > 8.0:
        raise AssuranceError(f"projection performance exceeded bounds: {timings!r}")
    return {"width_32_seconds": timings[32], "width_64_seconds": timings[64], "scale_ratio": ratio}


def check_mutation(repo_root: Path) -> dict[str, str]:
    """Run a fixed-seed archive mutation sample and fail on survivors/errors."""
    command = [
        shutil.which("mutatest") or "mutatest",
        "--src",
        "src/nlp_policy_nz/archive",
        "--testcmds",
        "pytest",
        "--mode",
        "sd",
        "--nlocations",
        "12",
        "--rseed",
        "133",
        "--exception",
        "1",
        "--nocov",
    ]
    environment = os.environ.copy()
    environment["PYTEST_ADDOPTS"] = (
        "tests/test_archive_schema.py tests/test_archive_assurance.py -q"
    )
    completed = subprocess.run(
        command,
        cwd=repo_root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode:
        detail = (completed.stdout + "\n" + completed.stderr).strip()[-2000:]
        raise AssuranceError(f"archive mutation assurance failed:\n{detail}")
    return {"sample": "12 fixed-seed mutants", "status": "passed"}


def run_assurance(repo_root: Path, *, run_mutation: bool = True) -> dict[str, object]:
    """Run all archive assurance lanes and return a JSON-serializable report."""
    with tempfile.TemporaryDirectory(prefix="archive-assurance-") as temporary:
        output_dir = Path(temporary)
        bundle = mixed_bundle()
        report: dict[str, object] = {
            "schema_version": bundle.schema_version,
            "serializer_canaries": check_serializer_canaries(bundle, output_dir),
            "compatibility": check_compatibility(bundle, output_dir),
            "performance": check_performance(),
        }
        if run_mutation:
            report["mutation"] = check_mutation(repo_root)
        else:
            report["mutation"] = {"status": "skipped"}
        return report


def main(argv: list[str] | None = None) -> int:
    """Run the archive assurance CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--skip-mutation", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        report = run_assurance(args.repo_root, run_mutation=not args.skip_mutation)
    except (AssuranceError, OSError, ValueError) as exc:
        sys.stderr.write(f"archive assurance failed: {exc}\n")
        return 1
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
