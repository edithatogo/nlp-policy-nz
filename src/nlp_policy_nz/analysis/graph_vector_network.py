"""Deterministic graph, vector, and network analysis for Track 33."""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import networkx as nx
import numpy as np

from nlp_policy_nz.ontology.mapping_graph import load_mapping_manifest

GRAPH_VECTOR_MANIFEST_FILENAME: Final[str] = "graph_vector_manifest.json"
GRAPH_VECTOR_GRAPH_METRICS_FILENAME: Final[str] = "graph_vector_graph_metrics.json"
GRAPH_VECTOR_VECTOR_METRICS_FILENAME: Final[str] = "graph_vector_vector_metrics.json"
GRAPH_VECTOR_ALIGNMENT_FILENAME: Final[str] = "graph_vector_alignment.csv"
GRAPH_VECTOR_BLOCKERS_FILENAME: Final[str] = "graph_vector_blockers.json"
GRAPH_VECTOR_MERMAID_FILENAME: Final[str] = "graph_vector_network.mmd"
GRAPH_VECTOR_MARKDOWN_FILENAME: Final[str] = "graph_vector_network_analysis.md"

TRACK_ID: Final[str] = "track33_graph_vector_network_analysis_20260625"
DEFAULT_OUTPUT_DIR: Final[Path] = Path("data") / "analysis"
DEFAULT_MARKDOWN_PATH: Final[Path] = Path("docs") / GRAPH_VECTOR_MARKDOWN_FILENAME


@dataclass(frozen=True, slots=True)
class VectorAnalysisRecord:
    """One deterministic vector item used by Track 33 analysis."""

    record_id: str
    label: str
    kind: str
    vector: tuple[float, ...]
    linked_concept_ids: tuple[str, ...] = ()
    source: str = "fixture"


@dataclass(frozen=True, slots=True)
class GraphVectorNetworkBundle:
    """Track 33 analysis bundle ready for artifact export."""

    manifest: dict[str, Any]
    graph_metrics: dict[str, Any]
    vector_metrics: dict[str, Any]
    alignment_rows: tuple[dict[str, Any], ...]
    blockers: tuple[dict[str, Any], ...]
    mermaid: str
    markdown: str


def build_fixture_vector_records() -> tuple[VectorAnalysisRecord, ...]:
    """Return deterministic vector fixtures spanning graph and ontology nodes."""
    records = (
        VectorAnalysisRecord(
            record_id="doc:fixture-court-2023-001",
            label="High Court judgment fixture",
            kind="document",
            vector=(0.20, 0.10, 0.90, 0.00),
            linked_concept_ids=("NZCourtOntology", "NZCourtLevel"),
        ),
        VectorAnalysisRecord(
            record_id="doc:fixture-hansard-2025-001",
            label="Hansard health debate fixture",
            kind="document",
            vector=(0.10, 0.90, 0.20, 0.10),
            linked_concept_ids=("NZHansardOntology", "NZDebateTopic"),
        ),
        VectorAnalysisRecord(
            record_id="doc:fixture-legislation-2024-001",
            label="Example Act fixture",
            kind="document",
            vector=(0.90, 0.10, 0.20, 0.00),
            linked_concept_ids=("NZActOntology", "NZProvision", "Tikanga"),
        ),
        VectorAnalysisRecord(
            record_id="ontology:NZActOntology",
            label="NZ Act ontology",
            kind="ontology",
            vector=(0.86, 0.14, 0.25, 0.00),
        ),
        VectorAnalysisRecord(
            record_id="ontology:NZCourtOntology",
            label="NZ court ontology",
            kind="ontology",
            vector=(0.24, 0.12, 0.86, 0.00),
        ),
        VectorAnalysisRecord(
            record_id="ontology:NZHansardOntology",
            label="NZ Hansard ontology",
            kind="ontology",
            vector=(0.14, 0.86, 0.24, 0.10),
        ),
        VectorAnalysisRecord(
            record_id="ontology:Tikanga",
            label="Tikanga",
            kind="ontology",
            vector=(0.40, 0.30, 0.20, 0.80),
        ),
    )
    return tuple(sorted(records, key=lambda record: record.record_id))


def build_graph_vector_network_analysis(
    *,
    vector_records: tuple[VectorAnalysisRecord, ...] | list[VectorAnalysisRecord] | None = None,
    repo_root_path: Path | str | None = None,
) -> GraphVectorNetworkBundle:
    """Build deterministic Track 33 graph, vector, and alignment analysis."""
    root = Path(repo_root_path) if repo_root_path is not None else _repo_root()
    records = tuple(vector_records) if vector_records is not None else build_fixture_vector_records()
    graph = _build_analysis_graph(root, records)
    graph_metrics = _graph_metrics(graph)
    vector_metrics = _vector_metrics(records)
    alignment_rows = _alignment_rows(graph, records, vector_metrics["nearest_neighbors"])
    blockers = _blockers(root, records)
    manifest = {
        "schema_version": "1.0",
        "track_id": TRACK_ID,
        "producer": "nlp-policy-nz",
        "source_boundary": (
            "Repo-side graph/vector analysis summarizes checked-in ontology mappings, "
            "NZ ontology candidates, Track 32 statistics, and deterministic vector "
            "fixtures. It does not claim full graph/vector corpus coverage."
        ),
        "summary": {
            "graph_node_count": graph_metrics["summary"]["node_count"],
            "graph_edge_count": graph_metrics["summary"]["edge_count"],
            "vector_count": vector_metrics["summary"]["vector_count"],
            "cluster_count": vector_metrics["clusters"]["cluster_count"],
            "alignment_pair_count": len(alignment_rows),
            "blocker_count": len(blockers),
        },
        "tables": {
            "graph_metrics": GRAPH_VECTOR_GRAPH_METRICS_FILENAME,
            "vector_metrics": GRAPH_VECTOR_VECTOR_METRICS_FILENAME,
            "alignment": GRAPH_VECTOR_ALIGNMENT_FILENAME,
            "blockers": GRAPH_VECTOR_BLOCKERS_FILENAME,
            "network": GRAPH_VECTOR_MERMAID_FILENAME,
        },
    }
    mermaid = _render_mermaid(graph)
    markdown = _markdown_summary(manifest, graph_metrics, vector_metrics, alignment_rows, blockers)
    return GraphVectorNetworkBundle(
        manifest=manifest,
        graph_metrics=graph_metrics,
        vector_metrics=vector_metrics,
        alignment_rows=alignment_rows,
        blockers=blockers,
        mermaid=mermaid,
        markdown=markdown,
    )


def write_graph_vector_network_artifacts(
    output_dir: Path | str | None = None,
    *,
    vector_records: tuple[VectorAnalysisRecord, ...] | list[VectorAnalysisRecord] | None = None,
    repo_root_path: Path | str | None = None,
    markdown_path: Path | str | None = None,
) -> dict[str, Path]:
    """Write Track 33 graph/vector/network artifacts and return paths."""
    root = Path(repo_root_path) if repo_root_path is not None else _repo_root()
    target_dir = Path(output_dir) if output_dir is not None else root / DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    if markdown_path is not None:
        target_markdown = Path(markdown_path)
    elif output_dir is None:
        target_markdown = root / DEFAULT_MARKDOWN_PATH
    else:
        target_markdown = target_dir / GRAPH_VECTOR_MARKDOWN_FILENAME
    target_markdown.parent.mkdir(parents=True, exist_ok=True)
    bundle = build_graph_vector_network_analysis(
        vector_records=vector_records,
        repo_root_path=root,
    )
    paths = {
        GRAPH_VECTOR_MANIFEST_FILENAME: target_dir / GRAPH_VECTOR_MANIFEST_FILENAME,
        GRAPH_VECTOR_GRAPH_METRICS_FILENAME: target_dir / GRAPH_VECTOR_GRAPH_METRICS_FILENAME,
        GRAPH_VECTOR_VECTOR_METRICS_FILENAME: target_dir / GRAPH_VECTOR_VECTOR_METRICS_FILENAME,
        GRAPH_VECTOR_ALIGNMENT_FILENAME: target_dir / GRAPH_VECTOR_ALIGNMENT_FILENAME,
        GRAPH_VECTOR_BLOCKERS_FILENAME: target_dir / GRAPH_VECTOR_BLOCKERS_FILENAME,
        GRAPH_VECTOR_MERMAID_FILENAME: target_dir / GRAPH_VECTOR_MERMAID_FILENAME,
        GRAPH_VECTOR_MARKDOWN_FILENAME: target_markdown,
    }
    _write_json(paths[GRAPH_VECTOR_MANIFEST_FILENAME], bundle.manifest)
    _write_json(paths[GRAPH_VECTOR_GRAPH_METRICS_FILENAME], bundle.graph_metrics)
    _write_json(paths[GRAPH_VECTOR_VECTOR_METRICS_FILENAME], bundle.vector_metrics)
    _write_csv(paths[GRAPH_VECTOR_ALIGNMENT_FILENAME], bundle.alignment_rows)
    _write_json(paths[GRAPH_VECTOR_BLOCKERS_FILENAME], list(bundle.blockers))
    paths[GRAPH_VECTOR_MERMAID_FILENAME].write_text(bundle.mermaid, encoding="utf-8")
    paths[GRAPH_VECTOR_MARKDOWN_FILENAME].write_text(bundle.markdown, encoding="utf-8")
    return paths


def _build_analysis_graph(root: Path, records: tuple[VectorAnalysisRecord, ...]) -> nx.Graph:
    graph = nx.Graph()
    mapping_path = root / "data" / "ontologies" / "ontology_mappings.json"
    for mapping in load_mapping_manifest(mapping_path):
        source_standard = f"standard:{mapping.source_standard}"
        target_standard = f"standard:{mapping.target_standard}"
        source_term = f"term:{mapping.source_standard}:{mapping.source_term}"
        target_term = f"term:{mapping.target_standard}:{mapping.target_term}"
        graph.add_node(source_standard, kind="standard", label=mapping.source_standard)
        graph.add_node(target_standard, kind="standard", label=mapping.target_standard)
        graph.add_node(source_term, kind="term", label=mapping.source_term)
        graph.add_node(target_term, kind="term", label=mapping.target_term)
        graph.add_edge(source_standard, source_term, relation="contains")
        graph.add_edge(target_standard, target_term, relation="contains")
        graph.add_edge(source_term, target_term, relation=mapping.mapping_predicate)

    nz_ontology = _read_json(root / "data" / "ontologies" / "nz_ontology_candidates.json")
    for concept in nz_ontology.get("concepts", []):
        concept_id = str(concept["concept_id"])
        concept_node = f"ontology:{concept_id}"
        graph.add_node(
            concept_node,
            kind="ontology",
            label=str(concept.get("label", concept_id)),
            application_area=str(concept.get("application_area", "")),
        )
        for broader in concept.get("broader", []):
            broader_node = f"ontology:{broader}"
            graph.add_edge(concept_node, broader_node, relation="broader")
        for anchor in concept.get("ontology_anchors", []):
            anchor_node = f"term:{anchor.get('standard', '')}:{anchor.get('term', '')}"
            graph.add_node(anchor_node, kind="term", label=str(anchor.get("term", "")))
            graph.add_edge(concept_node, anchor_node, relation=str(anchor.get("predicate", "")))

    for record in records:
        graph.add_node(record.record_id, kind=record.kind, label=record.label)
        for concept_id in record.linked_concept_ids:
            graph.add_edge(record.record_id, f"ontology:{concept_id}", relation="linked_concept")
    return graph


def _graph_metrics(graph: nx.Graph) -> dict[str, Any]:
    components = [sorted(component) for component in nx.connected_components(graph)]
    degree_centrality = nx.degree_centrality(graph)
    betweenness = nx.betweenness_centrality(graph)
    try:
        eigenvector = nx.eigenvector_centrality(graph, max_iter=1000)
    except nx.NetworkXException:
        eigenvector = dict.fromkeys(graph.nodes, 0.0)
    communities = tuple(nx.community.greedy_modularity_communities(graph))
    return {
        "summary": {
            "node_count": graph.number_of_nodes(),
            "edge_count": graph.number_of_edges(),
            "density": round(nx.density(graph), 6),
            "connected_component_count": len(components),
            "largest_component_size": max((len(component) for component in components), default=0),
        },
        "degree_distribution": _degree_distribution(graph),
        "centrality": {
            "degree_top": _top_scores(degree_centrality),
            "betweenness_top": _top_scores(betweenness),
            "eigenvector_top": _top_scores(eigenvector),
        },
        "communities": {
            "community_count": len(communities),
            "communities": [
                {"community_id": index + 1, "nodes": sorted(community)}
                for index, community in enumerate(communities)
            ],
        },
        "network_metrics": {
            "ontology_link_edge_count": sum(
                1 for _, _, data in graph.edges(data=True) if data.get("relation") == "linked_concept"
            ),
            "mapping_edge_count": sum(
                1
                for _, _, data in graph.edges(data=True)
                if str(data.get("relation", "")).startswith(("skos:", "owl:", "source:"))
            ),
        },
    }


def _vector_metrics(records: tuple[VectorAnalysisRecord, ...]) -> dict[str, Any]:
    if not records:
        return {
            "summary": {
                "vector_count": 0,
                "dimension_count": 0,
                "kind_counts": {},
                "mean_norm": 0.0,
            },
            "nearest_neighbors": {},
            "pca_projection": [],
            "clusters": {
                "cluster_count": 0,
                "assignments": [],
                "silhouette_score": 0.0,
            },
        }
    matrix = np.array([record.vector for record in records], dtype=float)
    nearest = _nearest_neighbors(records, matrix)
    projections = _pca_projection(records, matrix)
    assignments = _cluster_assignments(records, matrix)
    return {
        "summary": {
            "vector_count": len(records),
            "dimension_count": int(matrix.shape[1]) if len(records) else 0,
            "kind_counts": dict(sorted(_count_by(records, "kind").items())),
            "mean_norm": round(float(np.linalg.norm(matrix, axis=1).mean()), 6),
        },
        "nearest_neighbors": nearest,
        "pca_projection": projections,
        "clusters": {
            "cluster_count": len({row["cluster_id"] for row in assignments}),
            "assignments": assignments,
            "silhouette_score": _silhouette_score(matrix, [row["cluster_id"] for row in assignments]),
        },
    }


def _nearest_neighbors(
    records: tuple[VectorAnalysisRecord, ...],
    matrix: np.ndarray,
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for index, record in enumerate(records):
        rows = []
        for other_index, other in enumerate(records):
            if index == other_index:
                continue
            cosine = _cosine(matrix[index], matrix[other_index])
            rows.append(
                {
                    "record_id": other.record_id,
                    "cosine_similarity": round(cosine, 6),
                    "euclidean_distance": round(float(np.linalg.norm(matrix[index] - matrix[other_index])), 6),
                }
            )
        result[record.record_id] = sorted(
            rows,
            key=lambda row: (-row["cosine_similarity"], row["record_id"]),
        )
    return result


def _pca_projection(
    records: tuple[VectorAnalysisRecord, ...],
    matrix: np.ndarray,
) -> list[dict[str, Any]]:
    centered = matrix - matrix.mean(axis=0)
    _, singular_values, vh = np.linalg.svd(centered, full_matrices=False)
    components = centered @ vh[:2].T
    total_variance = float((singular_values**2).sum())
    explained = (
        (singular_values[:2] ** 2 / total_variance).tolist() if total_variance else [0.0, 0.0]
    )
    rows = []
    for index, record in enumerate(records):
        rows.append(
            {
                "record_id": record.record_id,
                "pc1": round(float(components[index, 0]), 6),
                "pc2": round(float(components[index, 1]) if components.shape[1] > 1 else 0.0, 6),
                "pc1_explained_variance": round(float(explained[0]), 6),
                "pc2_explained_variance": round(float(explained[1]) if len(explained) > 1 else 0.0, 6),
            }
        )
    return rows


def _cluster_assignments(
    records: tuple[VectorAnalysisRecord, ...],
    matrix: np.ndarray,
) -> list[dict[str, Any]]:
    rows = []
    for index, record in enumerate(records):
        axis = int(np.argmax(matrix[index]))
        rows.append({"record_id": record.record_id, "cluster_id": f"axis_{axis + 1}"})
    return rows


def _alignment_rows(
    graph: nx.Graph,
    records: tuple[VectorAnalysisRecord, ...],
    nearest: dict[str, list[dict[str, Any]]],
) -> tuple[dict[str, Any], ...]:
    vector_by_id = {record.record_id: np.array(record.vector, dtype=float) for record in records}
    rows = []
    for record in records:
        if not record.linked_concept_ids:
            continue
        source_vector = vector_by_id[record.record_id]
        ranked_ids = [row["record_id"] for row in nearest[record.record_id]]
        for concept_id in record.linked_concept_ids:
            concept_record_id = f"ontology:{concept_id}"
            concept_vector = vector_by_id.get(concept_record_id)
            cosine = _cosine(source_vector, concept_vector) if concept_vector is not None else 0.0
            nearest_rank = ranked_ids.index(concept_record_id) + 1 if concept_record_id in ranked_ids else None
            rows.append(
                {
                    "source_id": record.record_id,
                    "linked_concept_id": concept_id,
                    "graph_distance": _graph_distance(graph, record.record_id, concept_record_id),
                    "cosine_similarity": round(cosine, 6),
                    "nearest_rank": nearest_rank or "",
                    "aligned_in_top3": bool(nearest_rank and nearest_rank <= 3),
                }
            )
    return tuple(sorted(rows, key=lambda row: (row["source_id"], row["linked_concept_id"])))


def _blockers(root: Path, records: tuple[VectorAnalysisRecord, ...]) -> tuple[dict[str, Any], ...]:
    blockers = [
        {
            "blocker_id": "full-graph-inputs",
            "blocker_type": "full_graph_unavailable",
            "description": (
                "No canonical full citation, co-vote, co-speech, or Wikidata graph export is checked in."
            ),
            "resolution": "Supply full graph exports or generated NetworkX node-link artifacts.",
        },
        {
            "blocker_id": "full-vector-index",
            "blocker_type": "full_vector_index_unavailable",
            "description": "No canonical full LanceDB vector index is checked in for repo-side CI.",
            "resolution": "Supply a reproducible LanceDB or PipelineRecord vector export.",
        },
    ]
    if not any(record.kind == "document" and record.vector for record in records):
        blockers.append(
            {
                "blocker_id": "document-vectors-missing",
                "blocker_type": "document_vectors_unavailable",
                "description": "No document-level vector records were supplied.",
                "resolution": "Run embedding generation and pass vector records into the writer.",
            }
        )
    if not (root / "data" / "statistics" / "corpus_statistics_manifest.json").is_file():
        blockers.append(
            {
                "blocker_id": "track32-statistics-missing",
                "blocker_type": "track32_dependency_missing",
                "description": "Track 32 checked-in statistics are unavailable.",
                "resolution": "Regenerate Track 32 corpus statistics before Track 33 publication.",
            }
        )
    return tuple(blockers)


def _degree_distribution(graph: nx.Graph) -> list[dict[str, int]]:
    counts: dict[int, int] = {}
    for _, degree in graph.degree():
        counts[degree] = counts.get(degree, 0) + 1
    return [{"degree": degree, "node_count": counts[degree]} for degree in sorted(counts)]


def _top_scores(scores: dict[Any, float], limit: int = 10) -> list[dict[str, Any]]:
    return [
        {"node": str(node), "score": round(float(score), 6)}
        for node, score in sorted(scores.items(), key=lambda item: (-item[1], str(item[0])))[:limit]
    ]


def _count_by(records: tuple[VectorAnalysisRecord, ...], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        value = str(getattr(record, field))
        counts[value] = counts.get(value, 0) + 1
    return counts


def _silhouette_score(matrix: np.ndarray, labels: list[str]) -> float:
    scores = []
    for index, label in enumerate(labels):
        same = [i for i, other in enumerate(labels) if other == label and i != index]
        other_labels = sorted({other for other in labels if other != label})
        if not same or not other_labels:
            continue
        a_distance = float(np.mean([np.linalg.norm(matrix[index] - matrix[i]) for i in same]))
        b_distance = min(
            float(
                np.mean(
                    [
                        np.linalg.norm(matrix[index] - matrix[i])
                        for i, other in enumerate(labels)
                        if other == other_label
                    ]
                )
            )
            for other_label in other_labels
        )
        denominator = max(a_distance, b_distance)
        if denominator:
            scores.append((b_distance - a_distance) / denominator)
    return round(float(np.mean(scores)), 6) if scores else 0.0


def _graph_distance(graph: nx.Graph, source: str, target: str) -> int | str:
    if source not in graph or target not in graph:
        return ""
    try:
        return int(nx.shortest_path_length(graph, source, target))
    except nx.NetworkXNoPath:
        return ""


def _cosine(left: np.ndarray | None, right: np.ndarray | None) -> float:
    if left is None or right is None:
        return 0.0
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if math.isclose(denominator, 0.0):
        return 0.0
    return float(np.dot(left, right) / denominator)


def _render_mermaid(graph: nx.Graph, limit: int = 30) -> str:
    lines = ["graph LR"]
    for index, (source, target, data) in enumerate(sorted(graph.edges(data=True))):
        if index >= limit:
            break
        source_id = _node_id(str(source))
        target_id = _node_id(str(target))
        relation = str(data.get("relation", "related")).replace(":", "_")
        lines.append(f'  {source_id}["{source}"] -- "{relation}" --> {target_id}["{target}"]')
    return "\n".join(lines) + "\n"


def _markdown_summary(
    manifest: dict[str, Any],
    graph_metrics: dict[str, Any],
    vector_metrics: dict[str, Any],
    alignment_rows: tuple[dict[str, Any], ...],
    blockers: tuple[dict[str, Any], ...],
) -> str:
    summary = manifest["summary"]
    lines = [
        "# Graph, Vector, and Network Analysis",
        "",
        "Track 33 provides fixture-bounded graph, vector, network, and alignment",
        "analysis over checked-in ontology artifacts and deterministic vectors.",
        "",
        "## Summary",
        "",
        f"- Graph nodes: {summary['graph_node_count']}",
        f"- Graph edges: {summary['graph_edge_count']}",
        f"- Vectors: {summary['vector_count']}",
        f"- Clusters: {summary['cluster_count']}",
        f"- Alignment pairs: {summary['alignment_pair_count']}",
        f"- Known blockers: {summary['blocker_count']}",
        "",
        "## Network metrics",
        "",
        f"- Connected components: {graph_metrics['summary']['connected_component_count']}",
        f"- Communities: {graph_metrics['communities']['community_count']}",
        f"- Ontology link edges: {graph_metrics['network_metrics']['ontology_link_edge_count']}",
        "",
        "## Vector metrics",
        "",
        f"- Dimensions: {vector_metrics['summary']['dimension_count']}",
        f"- Mean vector norm: {vector_metrics['summary']['mean_norm']}",
        f"- Silhouette score: {vector_metrics['clusters']['silhouette_score']}",
        "",
        "## Alignment",
        "",
        f"- Top-3 aligned graph/vector pairs: {sum(1 for row in alignment_rows if row['aligned_in_top3'])}",
        "",
        "## Blockers",
        "",
    ]
    lines.extend(f"- `{blocker['blocker_id']}`: {blocker['description']}" for blocker in blockers)
    return "\n".join(lines) + "\n"


def _node_id(value: str) -> str:
    return "n_" + "".join(character.lower() if character.isalnum() else "_" for character in value)


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


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


__all__ = [
    "GRAPH_VECTOR_ALIGNMENT_FILENAME",
    "GRAPH_VECTOR_BLOCKERS_FILENAME",
    "GRAPH_VECTOR_GRAPH_METRICS_FILENAME",
    "GRAPH_VECTOR_MANIFEST_FILENAME",
    "GRAPH_VECTOR_MARKDOWN_FILENAME",
    "GRAPH_VECTOR_MERMAID_FILENAME",
    "GRAPH_VECTOR_VECTOR_METRICS_FILENAME",
    "GraphVectorNetworkBundle",
    "VectorAnalysisRecord",
    "build_fixture_vector_records",
    "build_graph_vector_network_analysis",
    "write_graph_vector_network_artifacts",
]
