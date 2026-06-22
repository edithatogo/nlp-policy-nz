"""NetworkX relational graph mapping parliamentary mentions to legislation acts.

This module provides the ``PolicyGraph`` class, a NetworkX-based directed
graph that links debate speeches, speakers, bills, legislation acts, and
specific sections cited during parliamentary proceedings.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal, Self, cast

import networkx as nx

from nlp_policy_nz.discourse import ArgumentComponent, ArgumentGraph

ArgumentType = Literal["premise", "conclusion", "none"]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NODE_TYPES: frozenset[str] = frozenset(
    {
        "act",
        "section",
        "speech",
        "speaker",
        "bill",
        "debate",
    }
)
"""Set of recognised node type labels used in ``PolicyGraph``."""

# ---------------------------------------------------------------------------
# PolicyGraph
# ---------------------------------------------------------------------------


class PolicyGraph:
    """Model NZ parliamentary debate citations as a NetworkX graph.

    This graph links debate speeches, speakers, bills, legislation acts, and
    specific sections cited during parliamentary proceedings.

    The graph uses typed nodes (act, section, speech, speaker, bill, debate)
    and directed edges that represent *mentions* or *citations* from a speech
    to a referenced act or section.

    Examples
    --------
    >>> graph = PolicyGraph()
    >>> graph.add_act("act-1", "Legislation Act 2019", 2019)
    >>> graph.add_speech("speech-1", "Hon Member", "2024-06-01", "Some text...")
    >>> graph.add_citation("speech-1", "act-1", "See section 29")
    >>> graph.query_acts_mentioned_in_speech("speech-1")
    ['act-1']

    """

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        """Initialise an empty ``PolicyGraph`` with a NetworkX ``DiGraph``."""
        self._graph: nx.DiGraph = nx.DiGraph()

    # ------------------------------------------------------------------
    # Node accessors
    # ------------------------------------------------------------------

    @property
    def graph(self) -> nx.DiGraph:
        """Return the underlying NetworkX directed graph.

        Returns
        -------
        nx.DiGraph
            The internal graph object, exposed for advanced inspection.

        """
        return self._graph

    # ------------------------------------------------------------------
    # Node mutators
    # ------------------------------------------------------------------

    def add_act(
        self,
        act_id: str,
        title: str,
        year: int,
        **metadata: object,
    ) -> None:
        r"""Add an act node to the graph.

        Parameters
        ----------
        act_id:
            Unique identifier for the act (e.g. ``\"act-123\"``).
        title:
            Full title of the legislation (e.g. ``\"Legislation Act 2019\"``).
        year:
            Year the act was enacted.
        **metadata:
            Additional key-value pairs stored on the node.

        """
        self._graph.add_node(
            act_id,
            type="act",
            title=title,
            year=year,
            **metadata,
        )

    def add_speech(
        self,
        speech_id: str,
        speaker: str,
        date: str,
        text: str,
        **metadata: object,
    ) -> None:
        r"""Add a speech node to the graph.

        Parameters
        ----------
        speech_id:
            Unique identifier for the speech (e.g. ``\"speech-42\"``).
        speaker:
            Name of the speaker (e.g. ``\"Hon Member\"``).
        date:
            Date the speech was delivered (ISO format string).
        text:
            Full transcript text of the speech.
        **metadata:
            Additional key-value pairs stored on the node.

        """
        self._graph.add_node(
            speech_id,
            type="speech",
            speaker=speaker,
            date=date,
            text=text,
            **metadata,
        )

    # ------------------------------------------------------------------
    # Edge mutators
    # ------------------------------------------------------------------

    def add_citation(
        self,
        speech_id: str,
        act_id: str,
        context: str | None = None,
    ) -> None:
        """Add a directed citation edge from a speech to an act.

        The edge represents that the speech *mentions* or *cites* the
        given act.

        Parameters
        ----------
        speech_id:
            Identifier of the source speech node.
        act_id:
            Identifier of the target act node.
        context:
            Optional snippet or context describing why the act was cited.

        """
        attrs: dict[str, Any] = {"relation": "cites"}
        if context is not None:
            attrs["context"] = context
        self._graph.add_edge(speech_id, act_id, **attrs)

    def add_section_reference(
        self,
        speech_id: str,
        section_id: str,
        **metadata: object,
    ) -> None:
        """Add a directed reference edge from a speech to a section.

        Parameters
        ----------
        speech_id:
            Identifier of the source speech node.
        section_id:
            Identifier of the target section node.
        **metadata:
            Additional key-value pairs stored on the edge.

        """
        self._graph.add_edge(
            speech_id,
            section_id,
            relation="references_section",
            **metadata,
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def query_acts_mentioned_in_speech(self, speech_id: str) -> list[str]:
        """Return all act identifiers cited by a given speech.

        Parameters
        ----------
        speech_id:
            Identifier of the speech node.

        Returns
        -------
        list[str]
            Sorted list of act identifiers that the speech cites.

        """
        if speech_id not in self._graph:
            return []
        successors = list(self._graph.successors(speech_id))
        acts: list[str] = [
            node for node in successors if self._graph.nodes[node].get("type") == "act"
        ]
        return sorted(acts)

    def query_speeches_mentioning_act(self, act_id: str) -> list[str]:
        """Return all speech identifiers that cite a given act.

        Parameters
        ----------
        act_id:
            Identifier of the act node.

        Returns
        -------
        list[str]
            Sorted list of speech identifiers that cite the act.

        """
        if act_id not in self._graph:
            return []
        predecessors = list(self._graph.predecessors(act_id))
        speeches: list[str] = [
            node for node in predecessors if self._graph.nodes[node].get("type") == "speech"
        ]
        return sorted(speeches)

    def query_most_cited_acts(
        self,
        top_n: int = 10,
    ) -> list[tuple[str, int]]:
        """Return the *top_n* most-cited acts ranked by citation count.

        Parameters
        ----------
        top_n:
            Number of top results to return (default ``10``).

        Returns
        -------
        list[tuple[str, int]]
            List of ``(act_id, citation_count)`` tuples in descending order.

        """
        counts: dict[str, int] = {}
        for node, data in self._graph.nodes(data=True):
            if data.get("type") == "act":
                count = len(self.query_speeches_mentioning_act(node))
                if count > 0:
                    counts[node] = count
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_counts[:top_n]

    def query_most_active_speakers(
        self,
        top_n: int = 10,
    ) -> list[tuple[str, int]]:
        """Return the *top_n* speakers who have made the most citations.

        Count is based on the number of outgoing citation edges from
        speeches attributed to each speaker.

        Parameters
        ----------
        top_n:
            Number of top results to return (default ``10``).

        Returns
        -------
        list[tuple[str, int]]
            List of ``(speaker_name, citation_count)`` tuples in descending
            order.

        """
        speaker_counts: dict[str, int] = {}
        for node, data in self._graph.nodes(data=True):
            if data.get("type") == "speech":
                speaker = data.get("speaker", "unknown")
                # Count outgoing edges to act-type nodes
                act_count = sum(
                    1
                    for succ in self._graph.successors(node)
                    if self._graph.nodes[succ].get("type") == "act"
                )
                if act_count > 0:
                    speaker_counts[speaker] = speaker_counts.get(speaker, 0) + act_count
        sorted_speakers = sorted(speaker_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_speakers[:top_n]

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Export the graph as a serializable dictionary.

        Returns
        -------
        dict[str, Any]
            A dictionary representation using NetworkX's node-link format.

        """
        return nx.node_link_data(self._graph)

    def save(self, path: str | Path) -> None:
        """Persist the graph to a JSON file.

        Parameters
        ----------
        path:
            Filesystem path for the output JSON file.

        """
        data = self.to_dict()
        Path(path).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> Self:
        """Load a ``PolicyGraph`` from a JSON file.

        The file must have been saved previously with :meth:`save`.

        Parameters
        ----------
        path:
            Filesystem path to the JSON file.

        Returns
        -------
        Self
            A new ``PolicyGraph`` instance with the restored graph.

        """
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        graph = cls()
        graph._graph = nx.node_link_graph(data)
        return graph

def export_argument_graph_jsonld(
    records: list[object],
    *,
    issue: str | None = None,
) -> dict[str, Any]:
    """Export PipelineRecord argument annotations as AIF-style JSON-LD."""
    arguments: list[ArgumentComponent] = []
    seen_component_ids: set[str] = set()
    for record in records:
        record_id = str(getattr(record, "doc_id", "record"))
        for item in getattr(record, "arguments", []) or []:
            component_id = str(item["component_id"])
            if component_id in seen_component_ids:
                component_id = f"{record_id}:{component_id}"
            seen_component_ids.add(component_id)
            arguments.append(
                ArgumentComponent(
                    component_id=component_id,
                    component_type=cast("ArgumentType", item["component_type"]),
                    text=str(item.get("text", "")),
                    start=int(item.get("start", 0)),
                    end=int(item.get("end", 0)),
                    confidence=float(item.get("confidence", 0.0)),
                )
            )
    return ArgumentGraph.from_arguments(arguments, issue=issue).to_aif_jsonld()
