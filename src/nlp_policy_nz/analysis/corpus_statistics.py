"""Deterministic whole-corpus descriptive statistics for Track 32."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from nlp_policy_nz.storage import PipelineRecord, load_from_parquet

CORPUS_STATISTICS_MANIFEST_FILENAME: Final[str] = "corpus_statistics_manifest.json"
CORPUS_STATISTICS_PER_CORPUS_FILENAME: Final[str] = "corpus_statistics_per_corpus.csv"
CORPUS_STATISTICS_PER_YEAR_FILENAME: Final[str] = "corpus_statistics_per_year.csv"
CORPUS_STATISTICS_ENTITY_TYPES_FILENAME: Final[str] = "corpus_statistics_entity_types.csv"
CORPUS_STATISTICS_ONTOLOGY_FILENAME: Final[str] = "corpus_statistics_ontology_coverage.json"
CORPUS_STATISTICS_BLOCKERS_FILENAME: Final[str] = "corpus_statistics_blockers.json"
CORPUS_STATISTICS_MARKDOWN_FILENAME: Final[str] = "corpus_statistics.md"

TRACK_ID: Final[str] = "track32_corpus_descriptive_statistics_20260625"
DEFAULT_OUTPUT_DIR: Final[Path] = Path("data") / "statistics"
DEFAULT_MARKDOWN_PATH: Final[Path] = Path("docs") / CORPUS_STATISTICS_MARKDOWN_FILENAME
_YEAR_RE: Final[re.Pattern[str]] = re.compile(r"\b(18|19|20)\d{2}\b")
_SENTENCE_RE: Final[re.Pattern[str]] = re.compile(r"[.!?]+")


@dataclass(frozen=True, slots=True)
class CorpusStatisticsBundle:
    """Track 32 statistics bundle ready for JSON, CSV, and Markdown output."""

    manifest: dict[str, Any]
    per_corpus: tuple[dict[str, Any], ...]
    per_year: tuple[dict[str, Any], ...]
    entity_types: tuple[dict[str, Any], ...]
    ontology_coverage: dict[str, Any]
    blockers: tuple[dict[str, Any], ...]
    markdown: str


def load_pipeline_records(paths: tuple[Path | str, ...]) -> tuple[PipelineRecord, ...]:
    """Load PipelineRecord rows from one or more Parquet files."""
    records: list[PipelineRecord] = []
    for path in paths:
        records.extend(load_from_parquet(path))
    return tuple(records)


def build_fixture_records() -> tuple[PipelineRecord, ...]:
    """Return deterministic fixture records when no full corpus is available."""
    return (
        PipelineRecord(
            doc_id="fixture-legislation-2024-001",
            corpus_source="legislation",
            raw_text=(
                "Example Act 2024 section 10. A person must provide information "
                "by 1 July 2024. Tikanga considerations may apply."
            ),
            cleaned_tokens=[
                "Example",
                "Act",
                "2024",
                "section",
                "10",
                "A",
                "person",
                "must",
                "provide",
                "information",
                "by",
                "1",
                "July",
                "2024",
            ],
            nz_act_citations=["Example Act 2024"],
            te_reo_terms=["tikanga"],
            embeddings=[0.1, 0.2, 0.3, 0.4],
            deontic_modality=[
                {"label": "obligation", "trigger": "must", "text": "must provide"},
                {"label": "permission", "trigger": "may", "text": "may apply"},
            ],
            temporal_expressions=[
                {"label": "date", "value": "2024-07-01", "text": "1 July 2024"},
            ],
            resolved_entities=[
                {"label": "Example Ministry", "type": "ORG", "qid": "Q100"},
                {"label": "Aotearoa New Zealand", "type": "GPE", "qid": "Q664"},
            ],
            legal_effect="obligation",
        ),
        PipelineRecord(
            doc_id="fixture-hansard-2025-001",
            corpus_source="hansard",
            raw_text=(
                "In 2025 the House debated health policy. The member may respond "
                "and the vote was agreed."
            ),
            cleaned_tokens=[
                "In",
                "2025",
                "the",
                "House",
                "debated",
                "health",
                "policy",
                "the",
                "member",
                "may",
                "respond",
            ],
            nz_act_citations=[],
            te_reo_terms=[],
            embeddings=None,
            deontic_modality=[{"label": "permission", "trigger": "may", "text": "may respond"}],
            temporal_expressions=[{"label": "year", "value": "2025", "text": "2025"}],
            resolved_entities=[{"label": "House", "entity_type": "ORG"}],
            voting_record={"motion": "Health policy vote", "outcome": "agreed"},
            stance="pro",
        ),
        PipelineRecord(
            doc_id="fixture-court-2023-001",
            corpus_source="court",
            raw_text="The High Court judgment in 2023 considered jurisdiction and remedy.",
            cleaned_tokens=[
                "The",
                "High",
                "Court",
                "judgment",
                "in",
                "2023",
                "considered",
                "jurisdiction",
                "and",
                "remedy",
            ],
            nz_act_citations=[],
            te_reo_terms=[],
            embeddings=[0.5, 0.6, 0.7, 0.8],
            temporal_expressions=[{"label": "year", "value": "2023", "text": "2023"}],
            resolved_entities=[{"label": "High Court", "type": "COURT"}],
        ),
    )


def build_corpus_statistics(
    *,
    records: tuple[PipelineRecord, ...] | list[PipelineRecord] | None = None,
    repo_root_path: Path | str | None = None,
) -> CorpusStatisticsBundle:
    """Build Track 32 descriptive statistics from pipeline rows and repo artifacts."""
    resolved_records = tuple(records) if records is not None else build_fixture_records()
    root = Path(repo_root_path) if repo_root_path is not None else _repo_root()
    ontology_coverage = _ontology_coverage(root)
    blockers = _blockers(resolved_records, root)
    per_corpus = _per_corpus_rows(resolved_records)
    per_year = _per_year_rows(resolved_records)
    entity_types = _entity_type_rows(resolved_records)
    manifest = {
        "schema_version": "1.0",
        "track_id": TRACK_ID,
        "producer": "nlp-policy-nz",
        "source_boundary": (
            "Repo-side statistics summarize supplied PipelineRecord rows or deterministic "
            "fixtures and checked-in ontology artifacts. They do not claim canonical "
            "full-corpus coverage unless full-corpus Parquet inputs are supplied."
        ),
        "summary": _summary(resolved_records, per_corpus, per_year, entity_types, blockers),
        "tables": {
            "per_corpus": CORPUS_STATISTICS_PER_CORPUS_FILENAME,
            "per_year": CORPUS_STATISTICS_PER_YEAR_FILENAME,
            "entity_types": CORPUS_STATISTICS_ENTITY_TYPES_FILENAME,
            "ontology_coverage": CORPUS_STATISTICS_ONTOLOGY_FILENAME,
            "blockers": CORPUS_STATISTICS_BLOCKERS_FILENAME,
        },
    }
    markdown = _markdown_summary(manifest, per_corpus, per_year, ontology_coverage, blockers)
    return CorpusStatisticsBundle(
        manifest=manifest,
        per_corpus=per_corpus,
        per_year=per_year,
        entity_types=entity_types,
        ontology_coverage=ontology_coverage,
        blockers=blockers,
        markdown=markdown,
    )


def write_corpus_statistics_artifacts(
    output_dir: Path | str | None = None,
    *,
    records: tuple[PipelineRecord, ...] | list[PipelineRecord] | None = None,
    repo_root_path: Path | str | None = None,
    markdown_path: Path | str | None = None,
) -> dict[str, Path]:
    """Write Track 32 statistics artifacts and return paths by filename."""
    root = Path(repo_root_path) if repo_root_path is not None else _repo_root()
    target_dir = Path(output_dir) if output_dir is not None else root / DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    if markdown_path is not None:
        target_markdown = Path(markdown_path)
    elif output_dir is None:
        target_markdown = root / DEFAULT_MARKDOWN_PATH
    else:
        target_markdown = target_dir / CORPUS_STATISTICS_MARKDOWN_FILENAME
    target_markdown.parent.mkdir(parents=True, exist_ok=True)
    bundle = build_corpus_statistics(records=records, repo_root_path=root)
    paths = {
        CORPUS_STATISTICS_MANIFEST_FILENAME: target_dir / CORPUS_STATISTICS_MANIFEST_FILENAME,
        CORPUS_STATISTICS_PER_CORPUS_FILENAME: target_dir
        / CORPUS_STATISTICS_PER_CORPUS_FILENAME,
        CORPUS_STATISTICS_PER_YEAR_FILENAME: target_dir / CORPUS_STATISTICS_PER_YEAR_FILENAME,
        CORPUS_STATISTICS_ENTITY_TYPES_FILENAME: target_dir
        / CORPUS_STATISTICS_ENTITY_TYPES_FILENAME,
        CORPUS_STATISTICS_ONTOLOGY_FILENAME: target_dir / CORPUS_STATISTICS_ONTOLOGY_FILENAME,
        CORPUS_STATISTICS_BLOCKERS_FILENAME: target_dir / CORPUS_STATISTICS_BLOCKERS_FILENAME,
        CORPUS_STATISTICS_MARKDOWN_FILENAME: target_markdown,
    }
    _write_json(paths[CORPUS_STATISTICS_MANIFEST_FILENAME], bundle.manifest)
    _write_json(paths[CORPUS_STATISTICS_ONTOLOGY_FILENAME], bundle.ontology_coverage)
    _write_json(paths[CORPUS_STATISTICS_BLOCKERS_FILENAME], list(bundle.blockers))
    _write_csv(paths[CORPUS_STATISTICS_PER_CORPUS_FILENAME], bundle.per_corpus)
    _write_csv(paths[CORPUS_STATISTICS_PER_YEAR_FILENAME], bundle.per_year)
    _write_csv(paths[CORPUS_STATISTICS_ENTITY_TYPES_FILENAME], bundle.entity_types)
    paths[CORPUS_STATISTICS_MARKDOWN_FILENAME].write_text(bundle.markdown, encoding="utf-8")
    return paths


def _per_corpus_rows(records: tuple[PipelineRecord, ...]) -> tuple[dict[str, Any], ...]:
    grouped: dict[str, list[PipelineRecord]] = defaultdict(list)
    for record in records:
        grouped[record.corpus_source].append(record)
    rows = []
    for corpus_source, corpus_records in sorted(grouped.items()):
        rows.append(
            {
                "corpus_source": corpus_source,
                "record_count": len(corpus_records),
                "document_count": len({record.doc_id for record in corpus_records}),
                "token_count": sum(len(record.cleaned_tokens) for record in corpus_records),
                "word_count": sum(len(_words(record.raw_text)) for record in corpus_records),
                "sentence_count": sum(_sentence_count(record.raw_text) for record in corpus_records),
                "citation_count": sum(len(record.nz_act_citations) for record in corpus_records),
                "te_reo_term_count": sum(len(record.te_reo_terms) for record in corpus_records),
                "maori_segment_percent": round(
                    100
                    * sum(1 for record in corpus_records if record.te_reo_terms)
                    / len(corpus_records),
                    2,
                ),
                "deontic_count": sum(len(record.deontic_modality) for record in corpus_records),
                "temporal_expression_count": sum(
                    len(record.temporal_expressions) for record in corpus_records
                ),
                "entity_count": sum(len(record.resolved_entities) for record in corpus_records),
                "voting_record_count": sum(1 for record in corpus_records if record.voting_record),
                "amendment_count": sum(len(record.amendments) for record in corpus_records),
                "argument_count": sum(len(record.arguments) for record in corpus_records),
                "embedding_record_count": sum(1 for record in corpus_records if record.embeddings),
                "average_embedding_dimensions": _average_embedding_dimensions(corpus_records),
            }
        )
    return tuple(rows)


def _per_year_rows(records: tuple[PipelineRecord, ...]) -> tuple[dict[str, Any], ...]:
    grouped: dict[int, list[PipelineRecord]] = defaultdict(list)
    for record in records:
        for year in _record_years(record):
            grouped[year].append(record)
    return tuple(
        {
            "year": year,
            "record_count": len(year_records),
            "corpus_sources": sorted({record.corpus_source for record in year_records}),
            "token_count": sum(len(record.cleaned_tokens) for record in year_records),
            "citation_count": sum(len(record.nz_act_citations) for record in year_records),
            "deontic_count": sum(len(record.deontic_modality) for record in year_records),
            "temporal_expression_count": sum(
                len(record.temporal_expressions) for record in year_records
            ),
        }
        for year, year_records in sorted(grouped.items())
    )


def _entity_type_rows(records: tuple[PipelineRecord, ...]) -> tuple[dict[str, Any], ...]:
    counts: Counter[str] = Counter()
    docs: dict[str, set[str]] = defaultdict(set)
    for record in records:
        for entity in record.resolved_entities:
            entity_type = str(
                entity.get("type") or entity.get("entity_type") or entity.get("label") or "unknown"
            )
            counts[entity_type] += 1
            docs[entity_type].add(record.doc_id)
    return tuple(
        {
            "entity_type": entity_type,
            "entity_count": counts[entity_type],
            "document_count": len(docs[entity_type]),
        }
        for entity_type in sorted(counts)
    )


def _ontology_coverage(root: Path) -> dict[str, Any]:
    ontology_dir = root / "data" / "ontologies"
    coverage = _read_json(ontology_dir / "coverage_manifest.json")
    mapping_summary = _read_json(ontology_dir / "ontology_mapping_summary.json")
    inferred = _read_json(ontology_dir / "inferred_mapping_candidates.json")
    nz_ontology = _read_json(ontology_dir / "nz_ontology_candidates.json")
    candidates = inferred.get("candidates", [])
    return {
        "track25": coverage.get("summary", {}),
        "track29": mapping_summary,
        "track30": {
            "candidate_count": inferred.get("candidate_count", 0),
            "method_counts": _method_counts(candidates),
            "review_status_counts": dict(
                Counter(str(item.get("review_status", "unknown")) for item in candidates)
            ),
        },
        "track31": {
            "concept_count": nz_ontology.get("summary", {}).get("concept_count", 0),
            "controlled_vocabulary_count": nz_ontology.get("summary", {}).get(
                "controlled_vocabulary_count",
                0,
            ),
            "application_area_counts": nz_ontology.get("summary", {}).get(
                "application_area_counts",
                {},
            ),
            "authority_counts": nz_ontology.get("summary", {}).get("authority_counts", {}),
        },
    }


def _blockers(records: tuple[PipelineRecord, ...], root: Path) -> tuple[dict[str, Any], ...]:
    present_corpora = {record.corpus_source for record in records}
    blockers: list[dict[str, Any]] = [
        {
            "blocker_id": "full-corpus-inputs",
            "blocker_type": "full_corpus_unavailable",
            "corpus": "all",
            "description": (
                "No canonical whole-corpus Parquet inventory is checked into this repo; "
                "statistics are bounded to supplied inputs or deterministic fixtures."
            ),
            "resolution": (
                "Supply full PipelineRecord Parquet exports for legislation, Hansard, and case law."
            ),
        },
        {
            "blocker_id": "date-coverage",
            "blocker_type": "date_coverage_incomplete",
            "corpus": "all",
            "description": "Not every PipelineRecord guarantees normalized temporal metadata.",
            "resolution": "Populate temporal_expressions or date metadata across all corpus rows.",
        },
    ]
    for corpus in ("legislation", "hansard", "court", "case_law"):
        if corpus not in present_corpora:
            blockers.append(
                {
                    "blocker_id": f"{corpus}-parquet-missing",
                    "blocker_type": "corpus_unavailable",
                    "corpus": corpus,
                    "description": f"No {corpus} PipelineRecord rows were supplied.",
                    "resolution": f"Run the ingestion pipeline for {corpus} and pass the Parquet export.",
                }
            )
    if (root / "data" / "ontologies" / "track28_blockers.json").is_file():
        blockers.append(
            {
                "blocker_id": "track28-analytics-measurement",
                "blocker_type": "ontology_measurement_dependency",
                "corpus": "ontology",
                "description": "Track 28 identified analytics measurement model work for Track 32.",
                "resolution": "Use this Track 32 manifest as the measurement model seed.",
            }
        )
    return tuple(blockers)


def _summary(
    records: tuple[PipelineRecord, ...],
    per_corpus: tuple[dict[str, Any], ...],
    per_year: tuple[dict[str, Any], ...],
    entity_types: tuple[dict[str, Any], ...],
    blockers: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    return {
        "record_count": len(records),
        "corpus_count": len(per_corpus),
        "year_count": len(per_year),
        "entity_type_count": len(entity_types),
        "token_count": sum(row["token_count"] for row in per_corpus),
        "citation_count": sum(row["citation_count"] for row in per_corpus),
        "deontic_count": sum(row["deontic_count"] for row in per_corpus),
        "temporal_expression_count": sum(row["temporal_expression_count"] for row in per_corpus),
        "entity_count": sum(row["entity_count"] for row in per_corpus),
        "embedding_record_count": sum(row["embedding_record_count"] for row in per_corpus),
        "blocker_count": len(blockers),
    }


def _markdown_summary(
    manifest: dict[str, Any],
    per_corpus: tuple[dict[str, Any], ...],
    per_year: tuple[dict[str, Any], ...],
    ontology_coverage: dict[str, Any],
    blockers: tuple[dict[str, Any], ...],
) -> str:
    summary = manifest["summary"]
    lines = [
        "# Whole-Corpus Descriptive Statistics",
        "",
        "Track 32 provides deterministic descriptive statistics for supplied pipeline records",
        "and checked-in ontology artifacts. The checked-in report is fixture-bounded until",
        "canonical whole-corpus Parquet exports are supplied.",
        "",
        "## Summary",
        "",
        f"- Records: {summary['record_count']}",
        f"- Corpora represented: {summary['corpus_count']}",
        f"- Years represented: {summary['year_count']}",
        f"- Entity types: {summary['entity_type_count']}",
        f"- Known blockers: {summary['blocker_count']}",
        "",
        "## Per-corpus coverage",
        "",
        "| Corpus | Records | Tokens | Citations | Entities | Deontic | Temporal |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in per_corpus:
        lines.append(
            "| {corpus_source} | {record_count} | {token_count} | {citation_count} | "
            "{entity_count} | {deontic_count} | {temporal_expression_count} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Temporal coverage",
            "",
            f"- Years: {', '.join(str(row['year']) for row in per_year) or 'none'}",
            "",
            "## Ontology coverage",
            "",
            f"- Track 25 rows: {ontology_coverage['track25'].get('row_count', 0)}",
            f"- Track 29 mappings: {ontology_coverage['track29'].get('mapping_count', 0)}",
            f"- Track 30 inferred candidates: {ontology_coverage['track30'].get('candidate_count', 0)}",
            f"- Track 31 NZ concepts: {ontology_coverage['track31'].get('concept_count', 0)}",
            "",
            "## Blockers",
            "",
        ]
    )
    lines.extend(f"- `{blocker['blocker_id']}`: {blocker['description']}" for blocker in blockers)
    return "\n".join(lines) + "\n"


def _record_years(record: PipelineRecord) -> tuple[int, ...]:
    values: list[str] = [record.doc_id, record.raw_text]
    values.extend(str(item.get("value", "")) for item in record.temporal_expressions)
    values.extend(str(item.get("text", "")) for item in record.temporal_expressions)
    years = sorted({int(match.group(0)) for value in values for match in _YEAR_RE.finditer(value)})
    return tuple(years)


def _method_counts(candidates: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for candidate in candidates:
        counts.update(str(method) for method in candidate.get("methods", []))
    return dict(sorted(counts.items()))


def _average_embedding_dimensions(records: list[PipelineRecord]) -> float:
    dimensions = [len(record.embeddings) for record in records if record.embeddings]
    if not dimensions:
        return 0.0
    return round(sum(dimensions) / len(dimensions), 2)


def _sentence_count(text: str) -> int:
    return max(1, len(list(_SENTENCE_RE.finditer(text)))) if text.strip() else 0


def _words(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_csv(path: Path, rows: tuple[dict[str, Any], ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        if not rows:
            handle.write("")
            return
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
