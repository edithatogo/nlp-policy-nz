"""SIOC export for Hansard debate discourse."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rdflib import Graph, Literal
from rdflib.namespace import FOAF, RDF, XSD

from nlp_policy_nz.linked_data.foaf import _slug, _uri
from nlp_policy_nz.linked_data.rdf import SIOC, bind_common_namespaces, write_graph

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from nlp_policy_nz.storage import PipelineRecord


@dataclass(frozen=True)
class SpeechPost:
    """A Hansard speech represented as a SIOC post."""

    identifier: str
    debate_id: str
    debate_title: str
    speaker_name: str
    speaker_identifier: str
    content: str
    created_at: str | None = None


def generate_sioc_graph(
    speeches: list[SpeechPost],
    *,
    base_uri: str = "https://data.parliament.nz/",
) -> Graph:
    """Generate a SIOC graph for Hansard debate speeches."""
    graph = bind_common_namespaces(Graph())
    site = _uri(base_uri, "parliament")
    graph.add((site, RDF.type, SIOC.Site))
    graph.add((site, SIOC.name, Literal("New Zealand Parliament")))

    for speech in speeches:
        debate = _uri(base_uri, f"debate/{speech.debate_id}")
        thread = _uri(base_uri, f"debate/{speech.debate_id}/thread")
        post = _uri(base_uri, f"speech/{speech.identifier}")
        speaker = _uri(base_uri, speech.speaker_identifier)

        graph.add((debate, RDF.type, SIOC.Forum))
        graph.add((debate, SIOC.name, Literal(speech.debate_title)))
        graph.add((debate, SIOC.has_parent, site))
        graph.add((thread, RDF.type, SIOC.Thread))
        graph.add((thread, SIOC.has_container, debate))
        graph.add((post, RDF.type, SIOC.Post))
        graph.add((post, SIOC.has_container, debate))
        graph.add((post, SIOC.has_reply, thread))
        graph.add((post, SIOC.content, Literal(speech.content)))
        graph.add((post, SIOC.has_creator, speaker))
        graph.add((speaker, RDF.type, FOAF.Person))
        graph.add((speaker, FOAF.name, Literal(speech.speaker_name)))

        if speech.created_at:
            graph.add((post, SIOC.created_at, Literal(speech.created_at, datatype=XSD.date)))

    return graph


def _metadata_value(
    metadata: Mapping[str, str],
    key: str,
    default: str,
) -> str:
    """Read a metadata value, using *default* for missing or empty values."""
    value = metadata.get(key, "")
    return value or default


def _speech_from_record(
    record: PipelineRecord,
    metadata: Mapping[str, str],
) -> SpeechPost:
    """Convert a pipeline record and metadata to a SIOC speech post."""
    speaker_name = _metadata_value(metadata, "speaker_name", "Unknown Speaker")
    speaker_identifier = _metadata_value(
        metadata,
        "speaker_identifier",
        f"speaker/{_slug(speaker_name)}",
    )
    debate_title = _metadata_value(
        metadata,
        "debate_title",
        record.bill_reference or record.report_title or "Hansard Debate",
    )
    debate_id = _metadata_value(metadata, "debate_id", _slug(debate_title))
    return SpeechPost(
        identifier=record.doc_id,
        debate_id=debate_id,
        debate_title=debate_title,
        speaker_name=speaker_name,
        speaker_identifier=speaker_identifier,
        content=record.raw_text,
        created_at=metadata.get("created_at"),
    )


def export_hansard_sioc(
    records: list[PipelineRecord],
    output_path: str | Path,
    *,
    base_uri: str = "https://data.parliament.nz/",
    speech_metadata: Mapping[str, Mapping[str, str]] | None = None,
) -> Path:
    """Write Hansard records as a SIOC Turtle graph."""
    hansard_records = [record for record in records if record.corpus_source == "hansard"]
    if not hansard_records:
        raise ValueError("No Hansard records available for SIOC export.")

    metadata_by_id = speech_metadata or {}
    speeches = [
        _speech_from_record(record, metadata_by_id.get(record.doc_id, {}))
        for record in hansard_records
    ]
    graph = generate_sioc_graph(speeches, base_uri=base_uri)
    return write_graph(graph, output_path)
