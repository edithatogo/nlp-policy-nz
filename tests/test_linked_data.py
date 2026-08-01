"""Tests for FOAF/SIOC linked-data export."""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

from nlp_policy_nz.cli.main import main
from nlp_policy_nz.linked_data import (
    SpeechPost,
    export_hansard_sioc,
    generate_sioc_graph,
    query_graph,
    rdf_sidecar_path,
)
from nlp_policy_nz.storage import PipelineRecord, serialize_to_parquet

SIOC = Namespace("http://rdfs.org/sioc/ns#")
SCHEMA = Namespace("https://schema.org/")


def _case_dir(name: str) -> Path:
    """Return a small workspace-local test directory."""
    path = Path("track16-test-output") / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_generate_sioc_graph_models_hansard_structure() -> None:
    """SIOC exporter represents parliament, debate, thread, and speeches."""
    speeches = [
        SpeechPost(
            identifier="speech-1",
            debate_id="debate-1",
            debate_title="Climate Adaptation Bill",
            speaker_name="Jane Doe",
            speaker_identifier="mp/jane-doe",
            content="I support this bill.",
            created_at="2026-06-21",
        )
    ]

    graph = generate_sioc_graph(speeches, base_uri="https://example.org/nz/")

    post = URIRef("https://example.org/nz/speech/speech-1")
    debate = URIRef("https://example.org/nz/debate/debate-1")
    site = URIRef("https://example.org/nz/parliament")
    assert (site, RDF.type, SIOC.Site) in graph
    assert (debate, RDF.type, SIOC.Forum) in graph
    assert (post, RDF.type, SIOC.Post) in graph
    assert (post, SIOC.content, Literal("I support this bill.")) in graph
    assert (post, SIOC.has_container, debate) in graph


def test_export_hansard_sioc_writes_ttl_sidecar() -> None:
    """Hansard pipeline records export to a .ttl sidecar."""
    tmp_path = _case_dir("sioc")
    parquet = tmp_path / "hansard.parquet"
    output = rdf_sidecar_path(parquet)
    records = [
        PipelineRecord(
            doc_id="han-001",
            corpus_source="hansard",
            raw_text="Speech text.",
            cleaned_tokens=["Speech", "text"],
            nz_act_citations=[],
            te_reo_terms=[],
        )
    ]

    result = export_hansard_sioc(records, output, base_uri="https://example.org/nz/")

    parsed = Graph()
    parsed.parse(result, format="turtle")
    assert result == output.resolve()
    assert (URIRef("https://example.org/nz/speech/han-001"), RDF.type, SIOC.Post) in parsed


def test_query_graph_returns_sparql_bindings() -> None:
    """SPARQL helper runs a basic SELECT query over Turtle RDF."""
    tmp_path = _case_dir("query")
    ttl = tmp_path / "graph.ttl"
    ttl.write_text(
        """
        @prefix foaf: <http://xmlns.com/foaf/0.1/> .
        <https://example.org/mp/1> a foaf:Person ; foaf:name "Jane Doe" .
        """,
        encoding="utf-8",
    )

    rows = query_graph(ttl, "SELECT ?name WHERE { ?s foaf:name ?name }")

    assert rows == [{"name": "Jane Doe"}]


def test_cli_export_rdf_and_sparql(capsys) -> None:
    """CLI can export Hansard Parquet to Turtle and query the RDF graph."""
    tmp_path = _case_dir("cli")
    parquet = tmp_path / "hansard.parquet"
    ttl = tmp_path / "hansard.ttl"
    serialize_to_parquet(
        [
            PipelineRecord(
                doc_id="han-001",
                corpus_source="hansard",
                raw_text="Kia ora from Parliament.",
                cleaned_tokens=["Kia", "ora"],
                nz_act_citations=[],
                te_reo_terms=["Kia ora"],
            )
        ],
        parquet,
    )

    rc_export = main(
        [
            "export-rdf",
            "--parquet",
            str(parquet),
            "--output",
            str(ttl),
            "--base-uri",
            "https://example.org/nz/",
        ]
    )
    rc_query = main(
        [
            "sparql",
            "--rdf",
            str(ttl),
            "--query",
            "SELECT ?content WHERE { ?post <http://rdfs.org/sioc/ns#content> ?content }",
        ]
    )

    assert rc_export == 0
    assert rc_query == 0
    assert "Kia ora from Parliament." in capsys.readouterr().out
