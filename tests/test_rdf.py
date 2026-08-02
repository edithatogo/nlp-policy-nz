from pathlib import Path

import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import FOAF

from nlp_policy_nz.linked_data.rdf import (
    SCHEMA,
    SIOC,
    bind_common_namespaces,
    query_graph,
    rdf_sidecar_path,
    write_graph,
)


def test_bind_common_namespaces() -> None:
    """Test that common namespaces are correctly bound to the graph."""
    graph = Graph()
    bind_common_namespaces(graph)

    namespaces = dict(graph.namespaces())
    assert "foaf" in namespaces
    assert namespaces["foaf"] == URIRef(FOAF)
    assert "sioc" in namespaces
    assert namespaces["sioc"] == URIRef(SIOC)
    assert "schema" in namespaces
    assert namespaces["schema"] == URIRef(SCHEMA)


def test_rdf_sidecar_path() -> None:
    """Test sidecar path generation for string and Path inputs."""
    assert rdf_sidecar_path("data.parquet") == Path("data.ttl")
    assert rdf_sidecar_path(Path("/tmp/data.parquet")) == Path("/tmp/data.ttl")
    assert rdf_sidecar_path("file_with.multiple.dots.parquet") == Path("file_with.multiple.dots.ttl")


def test_write_graph(tmp_path: Path) -> None:
    """Test serializing a graph to disk."""
    graph = Graph()
    graph.add((URIRef("http://example.org/a"), FOAF.name, Literal("Test Name")))

    output_path = tmp_path / "output.ttl"
    result_path = write_graph(graph, output_path)

    assert result_path == output_path.resolve()
    assert result_path.exists()

    # Verify the contents
    content = result_path.read_text()
    assert "Test Name" in content


def test_query_graph(tmp_path: Path) -> None:
    """Test running a SPARQL query against a serialized graph."""
    graph = Graph()
    bind_common_namespaces(graph)
    graph.add((URIRef("http://example.org/person1"), FOAF.name, Literal("Alice")))
    graph.add((URIRef("http://example.org/person2"), FOAF.name, Literal("Bob")))

    rdf_path = tmp_path / "data.ttl"
    write_graph(graph, rdf_path)

    query = """
    SELECT ?person ?name WHERE {
        ?person foaf:name ?name .
    }
    ORDER BY ?name
    """

    results = query_graph(rdf_path, query)

    assert len(results) == 2
    assert results[0]["name"] == "Alice"
    assert results[0]["person"] == "http://example.org/person1"

    assert results[1]["name"] == "Bob"
    assert results[1]["person"] == "http://example.org/person2"
