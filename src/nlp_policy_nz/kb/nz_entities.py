"""Curated seed knowledge base for New Zealand legal and parliamentary entities."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Literal

EntityType = Literal["mp", "party", "electorate", "ministry", "court"]


@dataclass(frozen=True)
class EntityContext:
    """Optional context used to disambiguate entity candidates."""

    party: str | None = None
    electorate: str | None = None
    date: str | None = None

    def to_dict(self) -> dict[str, str]:
        """Return non-empty context values for serialisation."""
        return {
            key: value
            for key, value in {
                "party": self.party,
                "electorate": self.electorate,
                "date": self.date,
            }.items()
            if value
        }


@dataclass(frozen=True)
class EntityRecord:
    """One local KB entity linked to Wikidata."""

    entity_id: str
    name: str
    entity_type: EntityType
    qid: str
    aliases: tuple[str, ...] = ()
    party: str | None = None
    electorate: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    attributes: dict[str, object] = field(default_factory=dict)

    def names(self) -> tuple[str, ...]:
        """Return canonical and alias names for matching."""
        return (self.name, *self.aliases)


def load_nz_entities(path: Path | str) -> tuple[EntityRecord, ...]:
    """Load entity records from a Track 12 JSON KB snapshot."""
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    return tuple(
        EntityRecord(
            entity_id=str(record["entity_id"]),
            name=str(record["name"]),
            entity_type=record["entity_type"],
            qid=str(record["qid"]),
            aliases=tuple(str(alias) for alias in record.get("aliases", ())),
            party=_optional_str(record.get("party")),
            electorate=_optional_str(record.get("electorate")),
            start_date=_optional_str(record.get("start_date")),
            end_date=_optional_str(record.get("end_date")),
            attributes=dict(record.get("attributes", {})),
        )
        for record in records
    )


@lru_cache(maxsize=1)
def default_nz_entities() -> tuple[EntityRecord, ...]:
    """Return the bundled NZ entity KB, falling back to a compact seed set."""
    kb_path = Path(__file__).resolve().parents[3] / "data" / "kb" / "nz_entities.json"
    if kb_path.exists():
        return load_nz_entities(kb_path)
    return seed_nz_entities()


def seed_nz_entities() -> tuple[EntityRecord, ...]:
    """Return a representative seed KB for Track 12 resolver integration."""
    return (
        EntityRecord(
            entity_id="mp:jacinda-ardern",
            name="Jacinda Ardern",
            entity_type="mp",
            qid="Q139616",
            aliases=("Ardern", "Rt Hon Jacinda Ardern"),
            party="Labour",
            electorate="Mount Albert",
            start_date="2008-11-08",
            end_date="2023-04-15",
        ),
        EntityRecord(
            entity_id="mp:christopher-luxon",
            name="Christopher Luxon",
            entity_type="mp",
            qid="Q85763849",
            aliases=("Chris Luxon", "Luxon"),
            party="National",
            electorate="Botany",
            start_date="2020-10-17",
        ),
        EntityRecord(
            entity_id="party:labour",
            name="New Zealand Labour Party",
            entity_type="party",
            qid="Q276025",
            aliases=("Labour", "Labour Party"),
        ),
        EntityRecord(
            entity_id="party:national",
            name="New Zealand National Party",
            entity_type="party",
            qid="Q1133105",
            aliases=("National", "National Party"),
        ),
        EntityRecord(
            entity_id="electorate:mount-albert",
            name="Mount Albert",
            entity_type="electorate",
            qid="Q6920665",
            aliases=("Mt Albert",),
        ),
        EntityRecord(
            entity_id="electorate:botany",
            name="Botany",
            entity_type="electorate",
            qid="Q4948642",
            aliases=("Botany electorate",),
        ),
        EntityRecord(
            entity_id="ministry:justice",
            name="Ministry of Justice",
            entity_type="ministry",
            qid="Q6865305",
            aliases=("New Zealand Ministry of Justice",),
        ),
        EntityRecord(
            entity_id="court:supreme-court",
            name="Supreme Court of New Zealand",
            entity_type="court",
            qid="Q7644816",
            aliases=("Supreme Court",),
        ),
        EntityRecord(
            entity_id="court:court-of-appeal",
            name="Court of Appeal of New Zealand",
            entity_type="court",
            qid="Q5179246",
            aliases=("Court of Appeal",),
        ),
    )


def _optional_str(value: object) -> str | None:
    """Convert optional JSON scalar values to strings."""
    return str(value) if value is not None else None
