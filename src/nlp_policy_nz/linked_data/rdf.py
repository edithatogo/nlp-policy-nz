"""Shared RDF serialization and query helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rdflib import Graph, Namespace
from rdflib.namespace import FOAF

SIOC = Namespace("http://rdfs.org/sioc/ns#")
SCHEMA = Namespace("https://schema.org/")


def bind_common_namespaces(graph: Graph) -> Graph:
    """Bind common parliamentary linked-data namespaces to *graph*."""
    graph.bind("foaf", FOAF)
    graph.bind("sioc", SIOC)
    graph.bind("schema", SCHEMA)
    return graph


def rdf_sidecar_path(parquet_path: str | Path) -> Path:
    """Return the Turtle sidecar path for a Parquet output."""
    return Path(parquet_path).with_suffix(".ttl")


def write_graph(graph: Graph, output_path: str | Path, *, rdf_format: str = "turtle") -> Path:
    """Serialize *graph* to *output_path* and return the resolved path."""
    target = Path(output_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=str(target), format=rdf_format)
    return target


def query_graph(
    rdf_path: str | Path,
    query: str,
    *,
    rdf_format: str = "turtle",
) -> list[dict[str, str]]:
    """Run a SPARQL SELECT query over an RDF file."""
    graph = bind_common_namespaces(Graph())
    graph.parse(str(Path(rdf_path)), format=rdf_format)
    result = graph.query(
        query,
        initNs={
            "foaf": FOAF,
            "sioc": SIOC,
            "schema": SCHEMA,
        },
    )

    rows: list[dict[str, str]] = []
    for row in result:
        row_map: dict[str, str] = {}
        labels = getattr(result, "vars", [])
        for idx, label in enumerate(labels):
            value: Any = row[idx]
            row_map[str(label)] = str(value)
        rows.append(row_map)
    return rows
