"""FOAF profile generation for parliamentary actors."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import FOAF, RDF

from nlp_policy_nz.linked_data.rdf import SCHEMA, bind_common_namespaces, write_graph

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class MPProfile:
    """Knowledge-base profile for a member of parliament."""

    identifier: str
    name: str
    party: str | None = None
    role: str | None = None
    electorate: str | None = None
    wikidata_qid: str | None = None


def _clean_base_uri(base_uri: str) -> str:
    """Normalize a base URI for joining path fragments."""
    return base_uri.rstrip("/") + "/"


def _slug(value: str) -> str:
    """Return a stable URI-safe slug for a label."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unknown"


def _uri(base_uri: str, fragment: str) -> URIRef:
    """Build a URIRef from a base URI and relative fragment."""
    return URIRef(_clean_base_uri(base_uri) + fragment.lstrip("/"))


def generate_foaf_graph(
    profiles: list[MPProfile],
    *,
    base_uri: str = "https://data.parliament.nz/",
) -> Graph:
    """Generate a FOAF graph for supplied MP profiles."""
    graph = bind_common_namespaces(Graph())
    for profile in profiles:
        person = _uri(base_uri, profile.identifier)
        graph.add((person, RDF.type, FOAF.Person))
        graph.add((person, FOAF.name, Literal(profile.name)))

        if profile.role:
            graph.add((person, SCHEMA.jobTitle, Literal(profile.role)))
        if profile.electorate:
            graph.add((person, SCHEMA.electoralDistrict, Literal(profile.electorate)))
        if profile.wikidata_qid:
            graph.add((
                person,
                SCHEMA.sameAs,
                URIRef(f"https://www.wikidata.org/entity/{profile.wikidata_qid}"),
            ))
        if profile.party:
            party = _uri(base_uri, f"party/{_slug(profile.party)}")
            graph.add((party, RDF.type, FOAF.Organization))
            graph.add((party, FOAF.name, Literal(profile.party)))
            graph.add((person, SCHEMA.affiliation, party))
            graph.add((party, FOAF.member, person))

    return graph


def export_foaf_profiles(
    profiles: list[MPProfile],
    output_path: str | Path,
    *,
    base_uri: str = "https://data.parliament.nz/",
) -> Path:
    """Write FOAF profiles as Turtle RDF."""
    graph = generate_foaf_graph(profiles, base_uri=base_uri)
    return write_graph(graph, output_path)
