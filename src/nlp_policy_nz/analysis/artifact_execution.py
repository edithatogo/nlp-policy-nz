"""Deterministic analysis artifact execution and figure production for Track 35."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

ANALYSIS_ARTIFACT_MANIFEST_FILENAME: Final[str] = "analysis_artifact_manifest.json"
ANALYSIS_ARTIFACT_BLOCKERS_FILENAME: Final[str] = "analysis_artifact_blockers.json"
ANALYSIS_ARTIFACT_VISUAL_CHECKLIST_FILENAME: Final[str] = "visual_inspection_checklist.md"

TRACK_ID: Final[str] = "track35_analysis_artifact_execution_20260625"
DEFAULT_OUTPUT_DIR: Final[Path] = Path("artifacts")


@dataclass(frozen=True, slots=True)
class AnalysisArtifactBundle:
    """Track 35 artifact bundle ready for publication export."""

    manifest: dict[str, Any]
    tables: dict[str, str]
    figures: dict[str, str]
    diagrams: dict[str, str]
    blockers: tuple[dict[str, Any], ...]
    visual_checklist: str


def build_analysis_artifact_bundle(
    *,
    repo_root_path: Path | str | None = None,
) -> AnalysisArtifactBundle:
    """Build deterministic Track 35 tables, figures, diagrams, and blockers."""
    root = Path(repo_root_path) if repo_root_path is not None else _repo_root()
    corpus_rows = _read_csv(root / "data" / "statistics" / "corpus_statistics_per_corpus.csv")
    year_rows = _read_csv(root / "data" / "statistics" / "corpus_statistics_per_year.csv")
    coverage = _read_json(root / "data" / "statistics" / "corpus_statistics_ontology_coverage.json")
    graph_metrics = _read_json(root / "data" / "analysis" / "graph_vector_graph_metrics.json")
    vector_metrics = _read_json(root / "data" / "analysis" / "graph_vector_vector_metrics.json")
    alignment_rows = _read_csv(root / "data" / "analysis" / "graph_vector_alignment.csv")

    tables = {
        "tables/corpus_summary.csv": _csv_text(corpus_rows),
        "tables/corpus_summary.tex": _latex_table(
            caption="Corpus Summary",
            label="tab:corpus-summary",
            headers=("corpus_source", "record_count", "token_count", "entity_count"),
            rows=corpus_rows,
        ),
        "tables/entity_density.csv": _csv_text(_entity_density_rows(corpus_rows)),
        "tables/topic_distribution.csv": _csv_text(_topic_distribution_rows(alignment_rows)),
        "tables/ontology_coverage.csv": _csv_text(_ontology_coverage_rows(coverage)),
    }
    figures = {
        "figures/temporal_trends.svg": _bar_svg(
            title="Temporal Trend Records",
            rows=year_rows,
            label_key="year",
            value_key="record_count",
        ),
        "figures/entity_density.svg": _bar_svg(
            title="Entity Density by Corpus",
            rows=_entity_density_rows(corpus_rows),
            label_key="corpus_source",
            value_key="entities_per_record",
        ),
        "figures/network_overview.svg": _network_svg(graph_metrics),
        "figures/embedding_projection.svg": _embedding_svg(vector_metrics),
    }
    diagrams = {
        "diagrams/pipeline_architecture.mmd": _pipeline_diagram(),
        "diagrams/workflow_data_flow.mmd": _workflow_diagram(),
        "diagrams/track_dependency.mmd": _dependency_diagram(),
    }
    blockers = _blockers(root)
    manifest_artifacts = _artifact_rows(tables, figures, diagrams)
    manifest = {
        "schema_version": "1.0",
        "track_id": TRACK_ID,
        "producer": "nlp-policy-nz",
        "source_boundary": (
            "Repo-side artifact production executes deterministic Track 32-34 "
            "fixture-bounded analyses and emits publication tables, SVG figures, "
            "Mermaid diagrams, blockers, and visual inspection guidance. It does "
            "not claim full-corpus figure production without canonical corpus exports."
        ),
        "summary": {
            "available_count": len(manifest_artifacts),
            "blocked_count": len(blockers),
            "table_count": len(tables),
            "figure_count": len(figures),
            "diagram_count": len(diagrams),
        },
        "artifacts": manifest_artifacts,
        "blockers": ANALYSIS_ARTIFACT_BLOCKERS_FILENAME,
        "visual_inspection_checklist": ANALYSIS_ARTIFACT_VISUAL_CHECKLIST_FILENAME,
    }
    return AnalysisArtifactBundle(
        manifest=manifest,
        tables=tables,
        figures=figures,
        diagrams=diagrams,
        blockers=blockers,
        visual_checklist=_visual_checklist(manifest_artifacts, blockers),
    )


def write_analysis_artifacts(
    output_dir: Path | str | None = None,
    *,
    repo_root_path: Path | str | None = None,
) -> dict[str, Path]:
    """Write Track 35 artifacts and return paths keyed by relative output path."""
    root = Path(repo_root_path) if repo_root_path is not None else _repo_root()
    target_dir = Path(output_dir) if output_dir is not None else root / DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    bundle = build_analysis_artifact_bundle(repo_root_path=root)
    paths: dict[str, Path] = {
        ANALYSIS_ARTIFACT_MANIFEST_FILENAME: target_dir / ANALYSIS_ARTIFACT_MANIFEST_FILENAME,
        ANALYSIS_ARTIFACT_BLOCKERS_FILENAME: target_dir / ANALYSIS_ARTIFACT_BLOCKERS_FILENAME,
        ANALYSIS_ARTIFACT_VISUAL_CHECKLIST_FILENAME: target_dir
        / ANALYSIS_ARTIFACT_VISUAL_CHECKLIST_FILENAME,
    }
    _write_json(paths[ANALYSIS_ARTIFACT_MANIFEST_FILENAME], bundle.manifest)
    _write_json(paths[ANALYSIS_ARTIFACT_BLOCKERS_FILENAME], list(bundle.blockers))
    paths[ANALYSIS_ARTIFACT_VISUAL_CHECKLIST_FILENAME].write_text(
        bundle.visual_checklist,
        encoding="utf-8",
    )
    for mapping in (bundle.tables, bundle.figures, bundle.diagrams):
        for relative_path, text in mapping.items():
            path = target_dir / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            paths[relative_path] = path
    return paths


def _artifact_rows(
    tables: dict[str, str],
    figures: dict[str, str],
    diagrams: dict[str, str],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for artifact_type, mapping in (
        ("table", tables),
        ("figure", figures),
        ("diagram", diagrams),
    ):
        for output_path in sorted(mapping):
            artifact_id = output_path.removeprefix(f"{artifact_type}s/").rsplit(".", 1)[0]
            rows.append(
                {
                    "artifact_id": f"{artifact_type}-{artifact_id.replace('_', '-')}",
                    "artifact_type": artifact_type,
                    "output_path": output_path,
                    "source": _source_for(output_path),
                    "status": "available",
                }
            )
    return rows


def _source_for(output_path: str) -> str:
    if output_path.startswith("tables/"):
        return "data/statistics and data/analysis checked-in tables"
    if output_path.startswith("figures/"):
        return "Track 32 temporal/entity data and Track 33 graph/vector metrics"
    return "Track 31-35 conductor and pipeline architecture context"


def _blockers(root: Path) -> tuple[dict[str, Any], ...]:
    blocker_sources = (
        root / "data" / "statistics" / "corpus_statistics_blockers.json",
        root / "data" / "analysis" / "graph_vector_blockers.json",
    )
    inherited = []
    for source in blocker_sources:
        if source.is_file():
            inherited.extend(_read_json(source))
    return (
        {
            "artifact_id": "full-corpus-embedding-umap",
            "artifact_type": "figure",
            "status": "blocked",
            "reason": (
                "Publication UMAP over the complete corpus requires canonical "
                "full-corpus vector exports; deterministic fixture projection is "
                "available as figures/embedding_projection.svg."
            ),
            "blocker_sources": [str(path.relative_to(root)) for path in blocker_sources],
            "inherited_blocker_count": len(inherited),
        },
        {
            "artifact_id": "citation-graph-production",
            "artifact_type": "figure",
            "status": "blocked",
            "reason": (
                "Full citation graph figures require canonical citation edge exports. "
                "The checked-in network overview remains fixture-bounded."
            ),
            "blocker_sources": ["data/analysis/graph_vector_blockers.json"],
            "inherited_blocker_count": len(inherited),
        },
    )


def _entity_density_rows(corpus_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows = []
    for row in corpus_rows:
        record_count = max(_number(row.get("record_count", 0)), 1.0)
        rows.append(
            {
                "corpus_source": row["corpus_source"],
                "record_count": int(record_count),
                "entity_count": int(_number(row.get("entity_count", 0))),
                "entities_per_record": round(_number(row.get("entity_count", 0)) / record_count, 3),
            }
        )
    return rows


def _topic_distribution_rows(alignment_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for row in alignment_rows:
        concept = row.get("linked_concept_id") or row.get("nearest_neighbor_id") or "unknown"
        counts[concept] = counts.get(concept, 0) + 1
    return [
        {"topic": topic, "artifact_count": count}
        for topic, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def _ontology_coverage_rows(coverage: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for standard, payload in sorted(coverage.get("standards", {}).items()):
        rows.append(
            {
                "standard": standard,
                "status": payload.get("status", "unknown"),
                "implemented_terms": payload.get("implemented_terms", 0),
                "planned_terms": payload.get("planned_terms", 0),
            }
        )
    if rows:
        return rows
    summary = coverage.get("summary", {})
    return [
        {
            "standard": "repo-ontology-coverage",
            "status": summary.get("coverage_status", "partial"),
            "implemented_terms": summary.get("implemented_count", 0),
            "planned_terms": summary.get("planned_count", 0),
        }
    ]


def _bar_svg(
    *,
    title: str,
    rows: list[dict[str, Any]],
    label_key: str,
    value_key: str,
) -> str:
    width = 720
    height = 420
    plot_left = 80
    plot_top = 70
    plot_width = 560
    plot_height = 250
    values = [_number(row.get(value_key, 0)) for row in rows]
    max_value = max(values, default=1.0) or 1.0
    bar_width = max(28, int(plot_width / max(len(rows), 1) * 0.55))
    gap = int(plot_width / max(len(rows), 1))
    parts = [
        _svg_header(width, height),
        f'<text x="{width / 2:.0f}" y="35" text-anchor="middle" class="title">{title}</text>',
        f'<line x1="{plot_left}" y1="{plot_top + plot_height}" x2="{plot_left + plot_width}" y2="{plot_top + plot_height}" class="axis"/>',
        f'<line x1="{plot_left}" y1="{plot_top}" x2="{plot_left}" y2="{plot_top + plot_height}" class="axis"/>',
    ]
    for index, row in enumerate(rows):
        value = _number(row.get(value_key, 0))
        bar_height = 0 if max_value == 0 else int(plot_height * value / max_value)
        x = plot_left + 24 + index * gap
        y = plot_top + plot_height - bar_height
        label = str(row.get(label_key, ""))
        parts.extend(
            [
                f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" class="bar"/>',
                f'<text x="{x + bar_width / 2:.0f}" y="{y - 8}" text-anchor="middle" class="label">{value:g}</text>',
                f'<text x="{x + bar_width / 2:.0f}" y="{plot_top + plot_height + 28}" text-anchor="middle" class="label">{_escape(label)}</text>',
            ]
        )
    parts.append("</svg>\n")
    return "\n".join(parts)


def _network_svg(graph_metrics: dict[str, Any]) -> str:
    summary = graph_metrics.get("summary", {})
    node_count = summary.get("node_count", 0)
    edge_count = summary.get("edge_count", 0)
    density = graph_metrics.get("density", summary.get("density", 0))
    parts = [
        _svg_header(720, 420),
        '<text x="360" y="35" text-anchor="middle" class="title">Network Overview</text>',
        '<circle cx="210" cy="180" r="66" class="node"/>',
        '<circle cx="360" cy="120" r="52" class="node alt"/>',
        '<circle cx="510" cy="220" r="72" class="node"/>',
        '<line x1="260" y1="158" x2="315" y2="135" class="edge"/>',
        '<line x1="405" y1="150" x2="460" y2="195" class="edge"/>',
        '<line x1="270" y1="205" x2="440" y2="225" class="edge"/>',
        f'<text x="210" y="185" text-anchor="middle" class="metric">{node_count} nodes</text>',
        f'<text x="360" y="125" text-anchor="middle" class="metric">{edge_count} edges</text>',
        f'<text x="510" y="225" text-anchor="middle" class="metric">density {float(density):.3f}</text>',
        "</svg>\n",
    ]
    return "\n".join(parts)


def _embedding_svg(vector_metrics: dict[str, Any]) -> str:
    neighbor_map = vector_metrics.get("nearest_neighbors", {})
    neighbors = [
        {"record_id": source_id, "neighbor_id": item.get("record_id", "")}
        for source_id, items in sorted(neighbor_map.items())
        for item in items[:1]
    ]
    points = [
        (
            120 + index * 80,
            120 + (index % 3) * 65,
            f"{item['record_id']} -> {item['neighbor_id']}",
        )
        for index, item in enumerate(neighbors[:6])
    ]
    parts = [
        _svg_header(720, 420),
        '<text x="360" y="35" text-anchor="middle" class="title">Fixture Embedding Projection</text>',
    ]
    for x, y, label in points:
        parts.append(f'<circle cx="{x}" cy="{y}" r="18" class="point"/>')
        parts.append(f'<text x="{x}" y="{y + 42}" text-anchor="middle" class="label">{_escape(label)}</text>')
    parts.append("</svg>\n")
    return "\n".join(parts)


def _svg_header(width: int, height: int) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">\n'
        "<style>"
        ".title{font:700 20px Arial,sans-serif;fill:#1f2937}"
        ".label{font:12px Arial,sans-serif;fill:#374151}"
        ".metric{font:700 14px Arial,sans-serif;fill:#111827}"
        ".axis{stroke:#6b7280;stroke-width:1.5}"
        ".bar{fill:#0072b2}.node{fill:#009e73;opacity:.85}.node.alt{fill:#d55e00}"
        ".edge{stroke:#6b7280;stroke-width:3;opacity:.65}.point{fill:#cc79a7;opacity:.9}"
        "</style>"
    )


def _pipeline_diagram() -> str:
    return """flowchart LR
    A["PipelineRecord fixtures"] --> B["Track 32 statistics"]
    B --> C["Track 33 graph/vector analysis"]
    C --> D["Track 34 publication protocol"]
    D --> E["Track 35 tables, figures, and diagrams"]
"""


def _workflow_diagram() -> str:
    return """flowchart TD
    A["Read checked-in Track 32-34 artifacts"] --> B["Build artifact manifest"]
    B --> C["Write machine-readable tables"]
    B --> D["Render deterministic SVG figures"]
    B --> E["Render Mermaid diagrams"]
    C --> F["Validate checked-in parity"]
    D --> F
    E --> F
"""


def _dependency_diagram() -> str:
    return """flowchart LR
    T32["Track 32 corpus statistics"] --> T35["Track 35 artifact execution"]
    T33["Track 33 graph/vector analysis"] --> T35
    T34["Track 34 publication protocol"] --> T35
    T35 --> T36["Track 36 exploration site"]
"""


def _visual_checklist(
    artifacts: list[dict[str, str]],
    blockers: tuple[dict[str, Any], ...],
) -> str:
    lines = [
        "# Track 35 Visual Inspection Checklist",
        "",
        "- Confirm SVG figures open in a browser or image viewer.",
        "- Confirm Mermaid diagrams render in documentation tooling.",
        "- Confirm CSV and LaTeX tables contain deterministic fixture-bounded values.",
        "- Confirm blocked full-corpus outputs are not described as completed.",
        "",
        "## Available artifacts",
        "",
    ]
    for artifact in artifacts:
        lines.append(f"- [{artifact['artifact_type']}] `{artifact['output_path']}`")
    lines.extend(["", "## Blocked artifacts", ""])
    for blocker in blockers:
        lines.append(f"- `{blocker['artifact_id']}`: {blocker['reason']}")
    return "\n".join(lines) + "\n"


def _latex_table(
    *,
    caption: str,
    label: str,
    headers: tuple[str, ...],
    rows: list[dict[str, str]],
) -> str:
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        "\\begin{tabular}{llll}",
        "\\hline",
        " & ".join(headers).replace("_", "\\_") + " \\\\",
        "\\hline",
    ]
    for row in rows:
        values = [_latex_escape(str(row.get(header, ""))) for header in headers]
        lines.append(" & ".join(values) + " \\\\")
    lines.extend(["\\hline", "\\end{tabular}", "\\end{table}", ""])
    return "\n".join(lines)


def _csv_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    headers = list(rows[0])
    output = [",".join(headers)]
    for row in rows:
        output.append(",".join(_csv_cell(row.get(header, "")) for header in headers))
    return "\n".join(output) + "\n"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> Any:  # noqa: ANN401
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _number(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _csv_cell(value: object) -> str:
    text = str(value)
    if any(char in text for char in ',\n"'):
        return '"' + text.replace('"', '""') + '"'
    return text


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _latex_escape(value: str) -> str:
    return value.replace("\\", "\\textbackslash{}").replace("_", "\\_").replace("&", "\\&")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


__all__ = [
    "ANALYSIS_ARTIFACT_BLOCKERS_FILENAME",
    "ANALYSIS_ARTIFACT_MANIFEST_FILENAME",
    "ANALYSIS_ARTIFACT_VISUAL_CHECKLIST_FILENAME",
    "AnalysisArtifactBundle",
    "build_analysis_artifact_bundle",
    "write_analysis_artifacts",
]
