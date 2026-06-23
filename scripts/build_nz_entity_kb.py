"""Build the Track 12 New Zealand entity KB from Wikidata SPARQL."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "nlp-policy-nz-track12/0.1 (https://github.com/TheAxiomFoundation/axiom-corpus)"


@dataclass(frozen=True)
class KbEntity:
    """Serializable Wikidata-backed entity record."""

    entity_id: str
    name: str
    entity_type: str
    qid: str
    aliases: list[str] = field(default_factory=list)
    party: str | None = None
    electorate: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


def main() -> None:
    """Fetch entities and write a compact JSON KB snapshot."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/kb/nz_entities.json"))
    parser.add_argument("--delay", type=float, default=0.2)
    args = parser.parse_args()

    entities: list[KbEntity] = []
    entities.extend(fetch_mps())
    time.sleep(args.delay)
    entities.extend(fetch_named_entities("party", PARTY_QUERY))
    time.sleep(args.delay)
    entities.extend(fetch_named_entities("electorate", ELECTORATE_QUERY))
    time.sleep(args.delay)
    entities.extend(fetch_named_entities("ministry", MINISTRY_QUERY))
    time.sleep(args.delay)
    entities.extend(fetch_named_entities("court", COURT_QUERY))

    deduped = dedupe_entities(entities)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps([asdict(entity) for entity in deduped], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    counts: dict[str, int] = {}
    for entity in deduped:
        counts[entity.entity_type] = counts.get(entity.entity_type, 0) + 1
    sys.stdout.write(json.dumps({"output": str(args.output), "counts": counts, "total": len(deduped)}, indent=2) + "\n")


def fetch_mps() -> list[KbEntity]:
    """Fetch current and historical New Zealand MPs with party/electorate context."""
    rows = run_sparql(MP_QUERY)
    by_qid: dict[str, dict[str, Any]] = {}
    for row in rows:
        qid = qid_from_uri(row["item"]["value"])
        entry = by_qid.setdefault(
            qid,
            {
                "name": row["itemLabel"]["value"],
                "parties": set(),
                "electorates": set(),
                "start_dates": [],
                "end_dates": [],
            },
        )
        if party := optional_value(row, "partyLabel"):
            entry["parties"].add(party)
        if electorate := optional_value(row, "electorateLabel"):
            entry["electorates"].add(electorate)
        if start_date := optional_date(row, "startDate"):
            entry["start_dates"].append(start_date)
        if end_date := optional_date(row, "endDate"):
            entry["end_dates"].append(end_date)

    entities: list[KbEntity] = []
    for qid, entry in by_qid.items():
        name = entry["name"]
        aliases = alias_candidates(name, allow_surname=True)
        start_dates = sorted(entry["start_dates"])
        end_dates = sorted(entry["end_dates"])
        entities.append(
            KbEntity(
                entity_id=f"mp:{slugify(name)}",
                name=name,
                entity_type="mp",
                qid=qid,
                aliases=aliases,
                party=sorted(entry["parties"])[-1] if entry["parties"] else None,
                electorate=sorted(entry["electorates"])[-1] if entry["electorates"] else None,
                start_date=start_dates[0] if start_dates else None,
                end_date=end_dates[-1] if end_dates else None,
                attributes={
                    "parties": sorted(entry["parties"]),
                    "electorates": sorted(entry["electorates"]),
                    "source": "wikidata",
                },
            )
        )
    return entities


def fetch_named_entities(entity_type: str, query: str) -> list[KbEntity]:
    """Fetch non-MP entity classes."""
    entities: list[KbEntity] = []
    for row in run_sparql(query):
        name = row["itemLabel"]["value"]
        qid = qid_from_uri(row["item"]["value"])
        aliases = alias_candidates(name, allow_surname=False)
        if alias := optional_value(row, "alias"):
            aliases.append(alias)
        entities.append(
            KbEntity(
                entity_id=f"{entity_type}:{slugify(name)}",
                name=name,
                entity_type=entity_type,
                qid=qid,
                aliases=sorted(set(aliases)),
                attributes={"source": "wikidata"},
            )
        )
    return entities


def run_sparql(query: str) -> list[dict[str, Any]]:
    """Run one SPARQL query against Wikidata."""
    payload = urlencode({"query": query, "format": "json"}).encode("utf-8")
    request = Request(  # noqa: S310
        SPARQL_ENDPOINT,
        data=payload,
        headers={
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    with urlopen(request, timeout=90) as response:  # noqa: S310
        data = json.loads(response.read().decode("utf-8"))
    return list(data["results"]["bindings"])


def dedupe_entities(entities: list[KbEntity]) -> list[KbEntity]:
    """Keep one stable record for each entity_id/QID pair."""
    seen_ids: set[str] = set()
    seen_qids: set[tuple[str, str]] = set()
    deduped: list[KbEntity] = []
    for entity in sorted(entities, key=lambda item: (item.entity_type, item.name)):
        key = (entity.entity_type, entity.qid)
        if entity.entity_id in seen_ids or key in seen_qids:
            continue
        seen_ids.add(entity.entity_id)
        seen_qids.add(key)
        deduped.append(entity)
    return deduped


def qid_from_uri(uri: str) -> str:
    """Extract a Wikidata QID from an entity URI."""
    return uri.rsplit("/", maxsplit=1)[-1]


def optional_value(row: dict[str, Any], key: str) -> str | None:
    """Return an optional SPARQL binding value."""
    if key not in row:
        return None
    return str(row[key]["value"])


def optional_date(row: dict[str, Any], key: str) -> str | None:
    """Return a date binding as YYYY-MM-DD."""
    value = optional_value(row, key)
    return value[:10] if value else None


def slugify(value: str) -> str:
    """Create a stable lowercase entity id segment."""
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value.casefold()))


def alias_candidates(name: str, *, allow_surname: bool) -> list[str]:
    """Derive conservative aliases from a Wikidata label."""
    aliases: set[str] = set()
    clean = re.sub(r"\s+", " ", name).strip()
    if clean != name:
        aliases.add(clean)
    for prefix in ("The Honourable ", "Hon ", "Rt Hon ", "Sir ", "Dame ", "Dr "):
        if clean.startswith(prefix):
            aliases.add(clean.removeprefix(prefix))
    parts = clean.split()
    if allow_surname and len(parts) >= 2:
        aliases.add(parts[-1])
    if clean.startswith("New Zealand "):
        short_name = clean.removeprefix("New Zealand ")
        aliases.add(short_name)
        if short_name.endswith(" Party"):
            aliases.add(short_name.removesuffix(" Party"))
    generic = {"party", "zealand", "new zealand", "court", "ministry", "department", "electorate"}
    return sorted(alias for alias in aliases if alias and alias.casefold() not in generic and alias != name)


MP_QUERY = """
SELECT ?item ?itemLabel ?partyLabel ?electorateLabel ?startDate ?endDate WHERE {
  ?item p:P39 ?statement .
  ?statement ps:P39/wdt:P279* wd:Q18145518 .
  OPTIONAL { ?statement pq:P580 ?startDate . }
  OPTIONAL { ?statement pq:P582 ?endDate . }
  OPTIONAL { ?statement pq:P4100 ?party . }
  OPTIONAL { ?statement pq:P768 ?electorate . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

PARTY_QUERY = """
SELECT DISTINCT ?item ?itemLabel ?alias WHERE {
  ?item wdt:P31/wdt:P279* wd:Q7278 .
  ?item wdt:P17 wd:Q664 .
  OPTIONAL { ?item skos:altLabel ?alias FILTER(LANG(?alias) = "en") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

ELECTORATE_QUERY = """
SELECT DISTINCT ?item ?itemLabel ?alias WHERE {
  ?item wdt:P31/wdt:P279* wd:Q192611 .
  ?item wdt:P17 wd:Q664 .
  OPTIONAL { ?item skos:altLabel ?alias FILTER(LANG(?alias) = "en") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

MINISTRY_QUERY = """
SELECT DISTINCT ?item ?itemLabel ?alias WHERE {
  VALUES ?class { wd:Q327333 wd:Q57660343 wd:Q35798 wd:Q2659904 }
  ?item wdt:P31/wdt:P279* ?class .
  ?item wdt:P17 wd:Q664 .
  ?item rdfs:label ?englishLabel .
  FILTER(LANG(?englishLabel) = "en")
  FILTER(CONTAINS(LCASE(STR(?englishLabel)), "ministry") || CONTAINS(LCASE(STR(?englishLabel)), "department"))
  OPTIONAL { ?item skos:altLabel ?alias FILTER(LANG(?alias) = "en") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

COURT_QUERY = """
SELECT DISTINCT ?item ?itemLabel ?alias WHERE {
  ?item wdt:P31/wdt:P279* wd:Q41487 .
  ?item wdt:P17 wd:Q664 .
  OPTIONAL { ?item skos:altLabel ?alias FILTER(LANG(?alias) = "en") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""


if __name__ == "__main__":
    main()
