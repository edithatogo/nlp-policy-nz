"""Tests for FOAF/SIOC linked-data export."""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import FOAF, RDF

from nlp_policy_nz.linked_data import (
    MPProfile,
    export_foaf_profiles,
    generate_foaf_graph,
)
from nlp_policy_nz.linked_data.foaf import _clean_base_uri, _slug, _uri

SCHEMA = Namespace("https://schema.org/")


def _case_dir(name: str) -> Path:
    """Return a small workspace-local test directory."""
    path = Path("track16-test-output") / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_generate_foaf_graph_contains_all_mp_profiles() -> None:
    """FOAF generator emits one person per supplied MP profile."""
    profiles = [
        MPProfile(
            identifier="mp/chloe-swarbrick",
            name="Chloe Swarbrick",
            party="Green Party of Aotearoa New Zealand",
            role="MP",
            electorate="Auckland Central",
        ),
        MPProfile(
            identifier="mp/chris-hipkins",
            name="Chris Hipkins",
            party="New Zealand Labour Party",
            role="MP",
            electorate="Remutaka",
        ),
    ]

    graph = generate_foaf_graph(profiles, base_uri="https://example.org/nz/")

    people = set(graph.subjects(RDF.type, FOAF.Person))
    assert len(people) == len(profiles)
    assert (
        URIRef("https://example.org/nz/mp/chloe-swarbrick"),
        FOAF.name,
        Literal("Chloe Swarbrick"),
    ) in graph
    assert (
        URIRef("https://example.org/nz/party/green-party-of-aotearoa-new-zealand"),
        RDF.type,
        FOAF.Organization,
    ) in graph
    assert (
        URIRef("https://example.org/nz/mp/chloe-swarbrick"),
        SCHEMA.electoralDistrict,
        Literal("Auckland Central"),
    ) in graph


def test_export_foaf_profiles_writes_valid_turtle() -> None:
    """FOAF profiles can be written as Turtle and parsed back."""
    tmp_path = _case_dir("foaf")
    output = tmp_path / "mps.ttl"

    result = export_foaf_profiles(
        [
            MPProfile(
                identifier="person-1",
                name="Jane Doe",
                party="Example Party",
                role="Minister",
                electorate="Example",
            )
        ],
        output,
        base_uri="https://example.org/",
    )

    parsed = Graph()
    parsed.parse(result, format="turtle")
    assert result == output.resolve()
    assert (URIRef("https://example.org/person-1"), RDF.type, FOAF.Person) in parsed


def test_clean_base_uri():
    assert _clean_base_uri("https://example.org/nz") == "https://example.org/nz/"
    assert _clean_base_uri("https://example.org/nz/") == "https://example.org/nz/"


def test_slug():
    assert _slug("Green Party of Aotearoa New Zealand") == "green-party-of-aotearoa-new-zealand"
    assert _slug("  Some  Value!!  ") == "some-value"
    assert _slug("!@#$") == "unknown"
    assert _slug("") == "unknown"


def test_uri():
    assert (
        str(_uri("https://example.org/nz/", "mp/jane-doe")) == "https://example.org/nz/mp/jane-doe"
    )
    assert (
        str(_uri("https://example.org/nz", "/mp/jane-doe")) == "https://example.org/nz/mp/jane-doe"
    )


def test_generate_foaf_graph_with_missing_optional_fields_and_wikidata():
    profiles = [
        MPProfile(
            identifier="mp/no-role",
            name="No Role",
            party="Independent",
            role=None,
            electorate=None,
            wikidata_qid="Q123456",
        ),
    ]

    graph = generate_foaf_graph(profiles, base_uri="https://example.org/nz/")

    person = URIRef("https://example.org/nz/mp/no-role")

    # Check that wikidata is present
    assert (
        person,
        SCHEMA.sameAs,
        URIRef("https://www.wikidata.org/entity/Q123456"),
    ) in graph

    # Check that role and electorate are NOT present
    assert not list(graph.objects(person, SCHEMA.jobTitle))
    assert not list(graph.objects(person, SCHEMA.electoralDistrict))


def test_generate_foaf_graph_missing_party():
    profiles = [
        MPProfile(
            identifier="mp/no-party",
            name="No Party",
            party=None,
        ),
    ]

    graph = generate_foaf_graph(profiles, base_uri="https://example.org/nz/")

    person = URIRef("https://example.org/nz/mp/no-party")
    assert not list(graph.objects(person, SCHEMA.affiliation))
