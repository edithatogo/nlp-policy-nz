"""Tests for the PolicyGraph relational graph (Task 7.2).

Verifies node/edge creation, query methods, speaker/act ranking, and
JSON serialisation round-trip.
"""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

from nlp_policy_nz.cli.graph import NODE_TYPES, PolicyGraph

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_node_types_constant() -> None:
    """NODE_TYPES is a frozenset of the expected labels."""
    expected = {"act", "section", "speech", "speaker", "bill", "debate"}
    assert frozenset(expected) == NODE_TYPES
    assert isinstance(NODE_TYPES, frozenset)


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------


def test_policy_graph_init_empty() -> None:
    """A freshly created PolicyGraph has no nodes or edges."""
    graph = PolicyGraph()
    assert graph.graph.number_of_nodes() == 0
    assert graph.graph.number_of_edges() == 0


# ---------------------------------------------------------------------------
# Node creation
# ---------------------------------------------------------------------------


def test_add_act_and_speech() -> None:
    """Nodes can be added and their type metadata is stored correctly."""
    graph = PolicyGraph()
    graph.add_act("act-1", "Legislation Act 2019", 2019)
    graph.add_speech("speech-1", "Hon Member", "2024-06-01", "Speech text...")

    assert graph.graph.has_node("act-1")
    assert graph.graph.has_node("speech-1")
    assert graph.graph.nodes["act-1"].get("type") == "act"
    assert graph.graph.nodes["speech-1"].get("type") == "speech"
    assert graph.graph.nodes["speech-1"].get("speaker") == "Hon Member"


# ---------------------------------------------------------------------------
# Edge creation
# ---------------------------------------------------------------------------


def test_add_citation_creates_edge() -> None:
    """A citation edge between speech and act is created."""
    graph = PolicyGraph()
    graph.add_act("act-1", "Legislation Act 2019", 2019)
    graph.add_speech("speech-1", "Hon Member", "2024-06-01", "Text...")
    graph.add_citation("speech-1", "act-1", context="See section 29")

    assert graph.graph.has_edge("speech-1", "act-1")
    edge_data = graph.graph.get_edge_data("speech-1", "act-1")
    assert edge_data is not None
    assert edge_data["relation"] == "cites"
    assert edge_data["context"] == "See section 29"


def test_add_citation_without_context() -> None:
    """Citation edge can be created without an optional context."""
    graph = PolicyGraph()
    graph.add_act("act-1", "Legislation Act 2019", 2019)
    graph.add_speech("speech-1", "Hon Member", "2024-06-01", "Text...")
    graph.add_citation("speech-1", "act-1")

    edge_data = graph.graph.get_edge_data("speech-1", "act-1")
    assert edge_data is not None
    assert edge_data["relation"] == "cites"
    assert "context" not in edge_data


def test_add_section_reference() -> None:
    """Section-reference edges carry the correct relation label."""
    graph = PolicyGraph()
    graph.add_speech("speech-1", "Hon Member", "2024-06-01", "Text...")
    graph._graph.add_node("sect-29", type="section")
    graph.add_section_reference("speech-1", "sect-29")

    assert graph.graph.has_edge("speech-1", "sect-29")
    edge_data = graph.graph.get_edge_data("speech-1", "sect-29")
    assert edge_data is not None
    assert edge_data["relation"] == "references_section"


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------


def test_query_acts_mentioned_in_speech() -> None:
    """Returning acts cited by a given speech."""
    graph = _build_sample_graph()
    acts = graph.query_acts_mentioned_in_speech("speech-1")
    assert acts == ["act-1", "act-2"]

    # Speech with no citations returns empty list
    assert graph.query_acts_mentioned_in_speech("speech-2") == []


def test_query_speeches_mentioning_act() -> None:
    """Returning speeches that cite a given act."""
    graph = _build_sample_graph()
    speeches = graph.query_speeches_mentioning_act("act-1")
    assert speeches == ["speech-1", "speech-3"]

    # Unknown act returns empty list
    assert graph.query_speeches_mentioning_act("act-999") == []


def test_query_acts_mentioned_unknown_speech() -> None:
    """Querying a non-existent speech returns an empty list."""
    graph = PolicyGraph()
    assert graph.query_acts_mentioned_in_speech("does-not-exist") == []


def test_query_speeches_mentioning_unknown_act() -> None:
    """Querying a non-existent act returns an empty list."""
    graph = PolicyGraph()
    assert graph.query_speeches_mentioning_act("does-not-exist") == []


# ---------------------------------------------------------------------------
# Ranking queries
# ---------------------------------------------------------------------------


def test_most_cited_acts() -> None:
    """Acts are ranked by citation count in descending order."""
    graph = _build_sample_graph()
    ranked = graph.query_most_cited_acts(top_n=5)
    assert ranked == [("act-1", 2), ("act-2", 1)]


def test_most_cited_acts_respects_top_n() -> None:
    """The top_n parameter limits results."""
    graph = _build_sample_graph()
    ranked = graph.query_most_cited_acts(top_n=1)
    assert ranked == [("act-1", 2)]


def test_most_active_speakers() -> None:
    """Speakers are ranked by total outgoing citations."""
    graph = _build_sample_graph()
    ranked = graph.query_most_active_speakers(top_n=5)
    assert ranked == [
        ("Hon Alice", 2),
        ("Hon Bob", 1),
    ]


def test_most_active_speakers_respects_top_n() -> None:
    """The top_n parameter limits speaker results."""
    graph = _build_sample_graph()
    ranked = graph.query_most_active_speakers(top_n=1)
    assert ranked == [("Hon Alice", 2)]


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def test_to_dict_roundtrip() -> None:
    """to_dict produces a dict parseable by node_link_graph."""
    graph = _build_sample_graph()
    data = graph.to_dict()
    assert "nodes" in data
    assert "links" in data or "edges" in data

    restored_graph = PolicyGraph()
    restored_graph._graph = nx.node_link_graph(data)
    assert restored_graph.query_acts_mentioned_in_speech("speech-1") == ["act-1", "act-2"]


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    """Saving to JSON and loading back produces an equivalent graph."""
    original = _build_sample_graph()
    file_path = tmp_path / "policy_graph.json"
    original.save(file_path)

    assert file_path.exists()
    with open(file_path, encoding="utf-8") as fh:  # noqa: PTH123
        raw = json.load(fh)
    assert "nodes" in raw
    assert "links" in raw or "edges" in raw

    restored = PolicyGraph.load(file_path)
    assert restored.graph.number_of_nodes() == original.graph.number_of_nodes()
    assert restored.graph.number_of_edges() == original.graph.number_of_edges()
    assert restored.query_acts_mentioned_in_speech("speech-1") == ["act-1", "act-2"]
    assert restored.query_most_cited_acts(top_n=2) == [("act-1", 2), ("act-2", 1)]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_sample_graph() -> PolicyGraph:
    """Build and return a small PolicyGraph with mixed data for testing.

    Structure
    ---------
    - speech-1 (Hon Alice) cites act-1 and act-2.
    - speech-2 (Hon Alice) cites no acts.
    - speech-3 (Hon Bob) cites act-1.
    - act-1 (Legislation Act 2019) cited by 2 speeches.
    - act-2 (Education Act 2020) cited by 1 speech.
    """
    graph = PolicyGraph()
    graph.add_act("act-1", "Legislation Act 2019", 2019)
    graph.add_act("act-2", "Education Act 2020", 2020)
    graph.add_speech("speech-1", "Hon Alice", "2024-06-01", "First speech...")
    graph.add_speech("speech-2", "Hon Alice", "2024-06-02", "Second speech...")
    graph.add_speech("speech-3", "Hon Bob", "2024-06-03", "Third speech...")

    graph.add_citation("speech-1", "act-1", context="Relevant to clause 5")
    graph.add_citation("speech-1", "act-2", context="Referencing education provisions")
    graph.add_citation("speech-3", "act-1", context="See section 12")

    return graph
