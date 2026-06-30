"""Bill and Hansard linkage scaffolding inspired by Axiom bill tracking."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Literal, get_args

BillStatus = Literal[
    "introduced",
    "first_reading",
    "select_committee",
    "second_reading",
    "committee_stage",
    "third_reading",
    "royal_assent",
    "defeated",
    "withdrawn",
    "unknown",
]
BILL_STATUSES: tuple[str, ...] = get_args(BillStatus)

_STATUS_PATTERNS: tuple[tuple[BillStatus, tuple[str, ...]], ...] = (
    ("royal_assent", ("royal assent", "assented")),
    ("third_reading", ("third reading", "read a third time")),
    ("committee_stage", ("committee of the whole", "committee stage")),
    ("second_reading", ("second reading", "read a second time")),
    ("select_committee", ("select committee", "reported back")),
    ("first_reading", ("first reading", "read a first time")),
    ("introduced", ("introduced", "bill introduced")),
    ("defeated", ("defeated", "lost", "negative")),
    ("withdrawn", ("withdrawn", "discharged")),
)


@dataclass(frozen=True)
class BillAction:
    """One normalized bill lifecycle action."""

    bill_id: str
    action_date: str
    raw_status: str
    status: BillStatus
    chamber: str | None = None
    source_url: str | None = None

    def __post_init__(self) -> None:
        """Validate required bill action identity fields."""
        _require_nonempty("bill_id", self.bill_id)
        _require_nonempty("action_date", self.action_date)
        _require_nonempty("raw_status", self.raw_status)
        _validate_bill_status(self.status)

    @classmethod
    def from_raw(
        cls,
        *,
        bill_id: str,
        action_date: str,
        raw_status: str,
        chamber: str | None = None,
        source_url: str | None = None,
    ) -> BillAction:
        """Create a bill action with a normalized status."""
        return cls(
            bill_id=bill_id,
            action_date=action_date,
            raw_status=raw_status,
            status=normalise_bill_status(raw_status),
            chamber=chamber,
            source_url=source_url,
        )

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-compatible representation."""
        return asdict(self)


@dataclass(frozen=True)
class BillVersion:
    """Bill version metadata used for Hansard and amendment linkage."""

    bill_id: str
    version_id: str
    title: str
    introduced_date: str | None = None
    source_url: str | None = None
    checksum_sha256: str | None = None

    def __post_init__(self) -> None:
        """Validate required bill version identity fields."""
        _require_nonempty("bill_id", self.bill_id)
        _require_nonempty("version_id", self.version_id)
        _require_nonempty("title", self.title)
        if self.checksum_sha256 is not None:
            _validate_sha256(self.checksum_sha256)

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-compatible representation."""
        return asdict(self)


@dataclass(frozen=True)
class BillHansardLink:
    """Candidate link between Hansard debate text and a bill/provision."""

    hansard_doc_id: str
    bill_id: str
    bill_title: str
    debate_date: str
    target_provision: str | None = None
    confidence: float = 0.0
    evidence: str | None = None

    def __post_init__(self) -> None:
        """Validate link identity and confidence as a normalized score."""
        _require_nonempty("hansard_doc_id", self.hansard_doc_id)
        _require_nonempty("bill_id", self.bill_id)
        _require_nonempty("bill_title", self.bill_title)
        _require_nonempty("debate_date", self.debate_date)
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, str | float | None]:
        """Return a JSON-compatible representation."""
        return asdict(self)


def normalise_bill_status(raw_status: str) -> BillStatus:
    """Map NZ parliamentary status text into a stable lifecycle vocabulary."""
    lowered = re.sub(r"\s+", " ", raw_status.lower()).strip()
    for status, markers in _STATUS_PATTERNS:
        if any(marker in lowered for marker in markers):
            return status
    return "unknown"


def _require_nonempty(name: str, value: str) -> str:
    """Return a stripped required value or raise a contract error."""
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{name} is required")
    return stripped


def _validate_bill_status(value: str) -> BillStatus:
    """Return a supported normalized bill status or raise a contract error."""
    if value not in BILL_STATUSES:
        allowed = ", ".join(BILL_STATUSES)
        raise ValueError(f"status must be one of: {allowed}")
    return value  # type: ignore[return-value]


def _validate_sha256(value: str) -> str:
    """Return a valid lowercase SHA-256 hex digest or raise a contract error."""
    stripped = value.strip()
    if not re.fullmatch(r"[0-9a-f]{64}", stripped):
        raise ValueError("checksum_sha256 must be a lowercase 64-character SHA-256 hex digest")
    return stripped
