"""DigitalNZ API v3 Probe — metadata search for NZ cultural heritage records.

This module provides an unauthenticated probe into the DigitalNZ API v3
(https://digitalnz.org/developers/api-docs-v3), which serves as the
**Discovery Layer** (Track 21) for the nlp-policy-nz pipeline.

DigitalNZ (digitalnz.org) aggregates metadata from New Zealand's cultural
heritage institutions — libraries, museums, galleries, and archives —
and exposes them through a unified search API. The API is built on the
Supplejack metadata framework and does **not** require authentication for
low-volume use, though rate limits apply (see Notes below).

API Findings (Track 21 — DigitalNZ Discovery Layer)
----------------------------------------------------
Base URL:  https://api.digitalnz.org/v3
Endpoint:  GET /records.json
Auth:      Optional — use ``api_key`` query param or ``Authentication-Token``
           header.  Unauthenticated requests are rate-limited (~60 req/min).
Paginate:  ``page`` (1-based) and ``per_page`` (default 20, max 100).
Field filter:  ``fields`` comma-separated list; only requested fields returned.
Sorting:   ``sort`` (field name) and ``direction`` (asc/desc).
Filters:   ``and[field_name]`` for scoped queries.

Response envelope::

    {
      "search": {
        "page": 1,
        "per_page": 20,
        "result_count": 32300803,
        "request_url": "...",
        "results": [ ... ],
        "facets": {}
      },
      "api_terms_of_use": "https://api.digitalnz.org/terms-of-use"
    }

Key record fields
-----------------
+---------------------------+----------+-----------------------------------+
| Field                     | Type     | Description                       |
+===========================+==========+===================================+
| id                        | int      | DigitalNZ record identifier       |
| title                     | str      | Display title of the item         |
| description               | str|None | Textual description               |
| creator                   | [str]    | Creator(s) / author(s)            |
| date                      | [str]    | ISO date(s) associated            |
| display_date              | str|None | Human-readable date               |
| display_collection        | str|None | Contributing collection name      |
| category                  | [str]    | e.g. Images, Text, Video          |
| rights                    | str|None | Rights statement URL or text      |
| copyright                 | [str]    | Copyright statement(s)            |
| usage                     | [str]    | Usage permissions                 |
| content_partner           | [str]    | Partner institution                |
| landing_url               | str|None | Link to item on partner site      |
| thumbnail_url             | str|None | Thumbnail image URL               |
| dc_identifier             | [str]    | Dublin Core identifier(s)         |
| dnz_type                  | str|None  | DigitalNZ item type               |
| tag                       | [str]    | Tags / keywords                   |
| language                  | [str]    | ISO language codes                |
| source_url                | str|None | API source metadata URL           |
+---------------------------+----------+-----------------------------------+

Rights classification logic
---------------------------
- ``rights`` containing ``creativecommons`` → ``"open"``
- ``rights`` containing ``rightsstatements.org`` with ``InC`` → ``"restricted"``
- ``copyright`` containing ``All rights reserved`` → ``"restricted"``
- ``usage`` contains ``No known copyright`` / ``No known restrictions`` → ``"open"``
- ``rights`` is ``null`` / ``None`` with no other signal → ``"unknown"``
- Fallback → ``"unknown"``

Normalisation to Open NZ Corpus Schema
---------------------------------------
DigitalNZ field → Shared NZ Corpus Core field:

- ``title`` → ``display_title``
- ``description`` → ``description``
- ``creator`` → (mapped as-is, list of strings)
- ``date[0]`` → ``published_date`` (first date, if present)
- ``rights`` → ``rights_note``
- ``landing_url`` → ``source_url``
- ``dc_identifier[0]`` → ``canonical_uri``
- ``content_partner`` → stored under ``provenance.source_name``
- ``display_collection`` → stored under ``provenance.source_record_id``

Usage
-----
Command-line probe::

    python -m nlp_policy_nz.digitalnz_probe \\
        --query "Māori land" \\
        --fields "title,description,creator,rights" \\
        --max-results 50 \\
        --output results.json

Python API::

    from nlp_policy_nz.digitalnz_probe import DigitalNZProbe

    probe = DigitalNZProbe()
    result = probe.search_all("Māori land", max_results=50)
    print(f"Found {result.total_count} records")
    for rec in result.records:
        print(rec.title)
"""  # noqa: W505

from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

import msgspec
import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL: Final[str] = "https://api.digitalnz.org/v3"
"""Default base URL for the DigitalNZ API v3."""

SEARCH_ENDPOINT: Final[str] = "/records.json"
"""Search endpoint path relative to the base URL."""

DEFAULT_PER_PAGE: Final[int] = 20
"""Default number of results per page."""

MAX_PER_PAGE: Final[int] = 100
"""Maximum allowed results per page by the DigitalNZ API."""

REQUEST_DELAY: Final[float] = 1.0
"""Minimum delay in seconds between consecutive API requests to avoid rate
limiting."""

MAX_RETRIES: Final[int] = 3
"""Maximum number of retries for transient HTTP errors."""

RETRY_BACKOFF: Final[float] = 2.0
"""Multiplicative backoff factor between retries."""

USER_AGENT: Final[str] = "nlp-policy-nz/0.1.0 (DigitalNZ Track 21 Probe)"
"""User-Agent header sent with each API request."""

# --- Rights classification patterns ---
_OPEN_RIGHTS_PATTERNS: Final[list[str]] = [
    "creativecommons",
    "cc0",
    "cc-by",
    "cc-by-sa",
    "cc-by-nc",
    "publicdomain",
    "no known copyright",
    "no known restriction",
]
"""Patterns in rights/copyright/usage indicating open access."""

_RESTRICTED_RIGHTS_PATTERNS: Final[list[str]] = [
    "all rights reserved",
    "inc",
    "rightsstatements.org/vocab/InC/",
]
"""Patterns indicating restricted / in-copyright status."""


# ---------------------------------------------------------------------------
# Structs
# ---------------------------------------------------------------------------


class DigitalNZRecord(msgspec.Struct):
    """A single record from the DigitalNZ API search response.

    Only the most commonly used fields are exposed; other fields are
    accessible via the :attr:`raw` dict.

    Parameters
    ----------
    record_id : int
        DigitalNZ numeric record identifier.
    title : str | None
        Display title of the item.
    description : str | None
        Textual description of the item.
    creator : list[str] | None
        Creator(s) or author(s) of the item.
    date : list[str] | None
        ISO 8601 date strings associated with the item.
    display_date : str | None
        Human-readable display date.
    display_collection : str | None
        Name of the contributing collection.
    display_content_partner : str | None
        Human-readable name of the content partner institution.
    category : list[str] | None
        Category labels (e.g. ``["Images"]``, ``["Text"]``).
    rights : str | None
        Rights statement URL or text.
    rights_url : list[str] | None
        List of rights statement URLs.
    copyright : list[str] | None
        Copyright statement(s).
    usage : list[str] | None
        Usage permission descriptions.
    landing_url : str | None
        URL to the item on the partner's site.
    thumbnail_url : str | None
        URL to a thumbnail image of the item.
    large_thumbnail_url : str | None
        URL to a large thumbnail image.
    source_url : str | None
        URL to the source metadata record in the API.
    content_partner : list[str] | None
        List of content partner institution names.
    dc_identifier : list[str] | None
        Dublin Core identifiers for the item.
    dnz_type : str | None
        DigitalNZ item type classification.
    tag : list[str] | None
        Tags or keywords.
    language : list[str] | None
        ISO language codes.
    provenance : str | None
        Provenance information.
    subject : list[str] | None
        Subject headings.
    publisher : list[str] | None
        Publisher names.
    raw : dict[str, Any] | None
        The complete raw record dict from the API for any fields not
        explicitly captured.

    """

    record_id: int = msgspec.field(name="id")
    title: str | None = None
    description: str | None = None
    creator: list[str] | None = None
    date: list[str] | None = None
    display_date: str | None = None
    display_collection: str | None = None
    display_content_partner: str | None = None
    category: list[str] | None = None
    rights: str | None = None
    rights_url: list[str] | None = None
    copyright: list[str] | None = None
    usage: list[str] | None = None
    landing_url: str | None = None
    thumbnail_url: str | None = None
    large_thumbnail_url: str | None = None
    source_url: str | None = None
    content_partner: list[str] | None = None
    dc_identifier: list[str] | None = None
    dnz_type: str | None = None
    tag: list[str] | None = None
    language: list[str] | None = None
    provenance: str | None = None
    subject: list[str] | None = None
    publisher: list[str] | None = None
    raw: dict[str, Any] | None = None


class SearchResult(msgspec.Struct):
    """Structured result of a DigitalNZ API search query.

    Parameters
    ----------
    query : str
        The original search query string.
    timestamp : str
        ISO 8601 timestamp of when the search was performed.
    total_count : int
        Total number of matching records in the DigitalNZ corpus.
    page : int
        Current page number in the search results.
    per_page : int
        Number of results per page.
    records : list[DigitalNZRecord]
        List of records returned for this search.
    request_url : str | None
        The full request URL sent to the API.

    """

    query: str
    timestamp: str
    total_count: int
    page: int
    per_page: int
    records: list[DigitalNZRecord]
    request_url: str | None = None


class NormalisedRecord(msgspec.Struct):
    """Record normalised to the Open NZ Corpus shared schema.

    Maps DigitalNZ record fields onto the ``shared_nz_corpus_core.schema.json``
    canonical fields.

    Parameters
    ----------
    record_id : int
        DigitalNZ record identifier.
    display_title : str | None
        Normalised title (from DigitalNZ ``title``).
    description : str | None
        Description text (from DigitalNZ ``description``).
    creator : list[str] | None
        Creator list (from DigitalNZ ``creator``).
    published_date : str | None
        First ISO date (from DigitalNZ ``date[0]``).
    rights_note : str
        Classified rights note (normalised from DigitalNZ ``rights`` /
        ``copyright`` / ``usage``).
    source_url : str | None
        Landing URL on the partner site (from DigitalNZ ``landing_url``).
    canonical_uri : str | None
        Dublin Core identifier (from DigitalNZ ``dc_identifier[0]``).
    source_name : str | None
        Content partner name (from DigitalNZ ``display_content_partner``).
    collection : str | None
        Collection name (from DigitalNZ ``display_collection``).
    category : list[str] | None
        Category labels.
    rights_classification : str
        One of ``"open"``, ``"restricted"``, or ``"unknown"``.
    raw_record : DigitalNZRecord
        Reference to the original DigitalNZ record.

    """

    record_id: int
    display_title: str | None = None
    description: str | None = None
    creator: list[str] | None = None
    published_date: str | None = None
    rights_note: str = "unknown"
    source_url: str | None = None
    canonical_uri: str | None = None
    source_name: str | None = None
    collection: str | None = None
    category: list[str] | None = None
    rights_classification: str = "unknown"
    raw_record: DigitalNZRecord | None = None


# ---------------------------------------------------------------------------
# Rights classification
# ---------------------------------------------------------------------------


def classify_rights(record: DigitalNZRecord) -> str:
    """Classify the rights status of a DigitalNZ record.

    Examines the ``rights``, ``copyright``, and ``usage`` fields of a
    record to determine an overall rights classification.

    Parameters
    ----------
    record : DigitalNZRecord
        The record to classify.

    Returns
    -------
    str
        One of ``"open"``, ``"restricted"``, or ``"unknown"``.

    Examples
    --------
    >>> rec = DigitalNZRecord(record_id=1, rights="http://creativecommons.org/licenses/by/4.0/")
    >>> classify_rights(rec)
    'open'

    >>> rec = DigitalNZRecord(record_id=2, copyright=["All rights reserved"])
    >>> classify_rights(rec)
    'restricted'

    """
    rights_lower = (record.rights or "").lower()
    for pattern in _OPEN_RIGHTS_PATTERNS:
        if pattern in rights_lower:
            return "open"
    for pattern in _RESTRICTED_RIGHTS_PATTERNS:
        if pattern in rights_lower:
            return "restricted"
    if record.copyright:
        copyright_text = " ".join(record.copyright).lower()
        for pattern in _RESTRICTED_RIGHTS_PATTERNS:
            if pattern in copyright_text:
                return "restricted"
    if record.usage:
        usage_text = " ".join(record.usage).lower()
        for pattern in _OPEN_RIGHTS_PATTERNS:
            if pattern in usage_text:
                return "open"
    if record.rights_url:
        rights_url_text = " ".join(record.rights_url).lower()
        for pattern in _OPEN_RIGHTS_PATTERNS:
            if pattern in rights_url_text:
                return "open"
        for pattern in _RESTRICTED_RIGHTS_PATTERNS:
            if pattern in rights_url_text:
                return "restricted"
    if record.rights is not None:
        return "restricted"
    return "unknown"


# ---------------------------------------------------------------------------
# Field normalisation
# ---------------------------------------------------------------------------


def normalise_record(record: DigitalNZRecord) -> NormalisedRecord:
    """Normalise a DigitalNZ record to the Open NZ Corpus shared schema.

    Maps the DigitalNZ API fields onto the canonical fields defined in
    ``shared_nz_corpus_core.schema.json``.

    Parameters
    ----------
    record : DigitalNZRecord
        The raw DigitalNZ record to normalise.

    Returns
    -------
    NormalisedRecord
        A record with fields mapped to the canonical schema.

    """
    rights_classification = classify_rights(record)
    rights_parts: list[str] = []
    if record.rights:
        rights_parts.append(record.rights)
    if record.copyright:
        rights_parts.extend(record.copyright)
    if record.usage:
        rights_parts.extend(record.usage)
    rights_note = "; ".join(rights_parts) if rights_parts else rights_classification
    return NormalisedRecord(
        record_id=record.record_id,
        display_title=record.title,
        description=record.description,
        creator=record.creator,
        published_date=record.date[0] if record.date else None,
        rights_note=rights_note,
        source_url=record.landing_url,
        canonical_uri=record.dc_identifier[0] if record.dc_identifier else None,
        source_name=record.display_content_partner or (
            record.content_partner[0] if record.content_partner else None
        ),
        collection=record.display_collection,
        category=record.category,
        rights_classification=rights_classification,
        raw_record=record,
    )




# ---------------------------------------------------------------------------
# Probe class
# ---------------------------------------------------------------------------


class DigitalNZProbe:
    """Probe for querying the DigitalNZ API v3 metadata search service.

    Provides methods for searching, field filtering, pagination, and
    rights classification of New Zealand cultural heritage metadata.

    Parameters
    ----------
    base_url : str
        Base URL for the DigitalNZ API v3.
    api_key : str | None
        Optional API key.  If ``None``, requests are unauthenticated.
    request_delay : float
        Minimum delay in seconds between API requests to avoid rate
        limiting (default: ``1.0``).
    user_agent : str
        User-Agent header value.

    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str | None = None,
        request_delay: float = REQUEST_DELAY,
        user_agent: str = USER_AGENT,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._request_delay = request_delay
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json",
        })
        if api_key:
            self._session.headers["Authentication-Token"] = api_key
        self._last_request_time: float = 0.0

    def _rate_limit(self) -> None:
        """Enforce a minimum delay between consecutive API requests."""
        target_time = self._last_request_time + self._request_delay
        while True:
            remaining = target_time - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(remaining)
        self._last_request_time = time.monotonic()

    def _build_url(self, endpoint: str, params: dict[str, Any]) -> str:
        """Build a full request URL for the API.

        Parameters
        ----------
        endpoint : str
            API endpoint path (e.g. ``/records.json``).
        params : dict[str, Any]
            Query parameters.

        Returns
        -------
        str
            The complete URL string.

        """
        query_string = "&".join(
            f"{k}={requests.utils.quote(str(v), safe='')}"
            for k, v in params.items()
            if v is not None
        )
        return f"{self._base_url}{endpoint}?{query_string}"

    def _request(
        self,
        endpoint: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Perform a rate-limited HTTP GET request with retries.

        Parameters
        ----------
        endpoint : str
            API endpoint path.
        params : dict[str, Any]
            Query parameters.

        Returns
        -------
        dict[str, Any]
            Parsed JSON response body.

        Raises
        ------
        requests.RequestException
            If all retries fail.

        """
        url = self._build_url(endpoint, params)
        last_exc: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                self._rate_limit()
                resp = self._session.get(url, timeout=30)
                if resp.status_code == 429:
                    retry_after = float(
                        resp.headers.get("Retry-After", str(attempt * 2))
                    )
                    logger.warning(
                        "Rate limited (attempt %d/%d). Waiting %.1f s.",
                        attempt, MAX_RETRIES, retry_after,
                    )
                    time.sleep(retry_after)
                    continue
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.HTTPError as exc:
                last_exc = exc
                status = exc.response.status_code if exc.response is not None else 0
                if status in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
                    backoff = RETRY_BACKOFF**attempt
                    logger.warning("HTTP %d (attempt %d/%d). Retrying.", status, attempt, MAX_RETRIES)
                    time.sleep(backoff)
                    continue
                msg = f"DigitalNZ API returned HTTP {status} for {endpoint}: {exc}"
                raise requests.RequestException(msg) from exc
            except requests.exceptions.RequestException as exc:
                last_exc = exc
                if attempt < MAX_RETRIES:
                    backoff = RETRY_BACKOFF**attempt
                    logger.warning("Request failed (attempt %d/%d). Retrying.", attempt, MAX_RETRIES)
                    time.sleep(backoff)
                    continue
                msg = f"DigitalNZ API request failed after {MAX_RETRIES} attempts: {exc}"
                raise requests.RequestException(msg) from exc
        if last_exc is not None:
            raise requests.RequestException(
                f"DigitalNZ API request failed after {MAX_RETRIES} attempts: {last_exc}"
            ) from last_exc
        msg = f"DigitalNZ API request failed after {MAX_RETRIES} attempts (unknown error)."
        raise requests.RequestException(msg)

    def _parse_record(self, raw: dict[str, Any]) -> DigitalNZRecord:
        """Parse a raw API record dict into a :class:`DigitalNZRecord`.

        Parameters
        ----------
        raw : dict[str, Any]
            Raw record dict from the API response.

        Returns
        -------
        DigitalNZRecord
            Parsed record struct.

        """
        known_fields = {
            f.name: getattr(f, "encode_name", None) or f.name
            for f in msgspec.structs.fields(DigitalNZRecord)
        }
        kwargs: dict[str, Any] = {}
        for field_name, api_name in known_fields.items():
            if api_name in raw:
                kwargs[field_name] = raw[api_name]
        if "id" in raw:
            kwargs["record_id"] = raw["id"]
        kwargs["raw"] = dict(raw)
        return DigitalNZRecord(**kwargs)

    def search(
        self,
        query: str,
        fields: list[str] | None = None,
        per_page: int = DEFAULT_PER_PAGE,
        page: int = 1,
    ) -> SearchResult:
        """Execute a single search query against the DigitalNZ API.

        Parameters
        ----------
        query : str
            Free-text search query.
        fields : list[str] | None
            Optional list of field names to include in the response.
        per_page : int
            Number of results per page (default: 20, max: 100).
        page : int
            Page number to retrieve (1-based, default: 1).

        Returns
        -------
        SearchResult
            Structured search result with metadata and records.

        Raises
        ------
        ValueError
            If *per_page* exceeds 100 or *page* is less than 1.

        """
        if per_page < 1 or per_page > MAX_PER_PAGE:
            msg = f"per_page must be between 1 and {MAX_PER_PAGE}, got {per_page}"
            raise ValueError(msg)
        if page < 1:
            msg = f"page must be >= 1, got {page}"
            raise ValueError(msg)
        params: dict[str, Any] = {"text": query, "per_page": per_page, "page": page}
        if fields:
            params["fields"] = ",".join(fields)
        data = self._request(SEARCH_ENDPOINT, params)
        search_data = data.get("search", data)
        raw_results = search_data.get("results", [])
        records = [self._parse_record(raw) for raw in raw_results]
        return SearchResult(
            query=query,
            timestamp=datetime.now(UTC).isoformat(),
            total_count=search_data.get("result_count", 0),
            page=search_data.get("page", page),
            per_page=search_data.get("per_page", per_page),
            records=records,
            request_url=search_data.get("request_url"),
        )

    def search_all(
        self,
        query: str,
        fields: list[str] | None = None,
        max_results: int = DEFAULT_PER_PAGE,
    ) -> SearchResult:
        """Execute a paginated search, fetching up to *max_results* records.

        Parameters
        ----------
        query : str
            Free-text search query.
        fields : list[str] | None
            Optional list of field names to include.
        max_results : int
            Maximum number of results to collect (default: 20).

        Returns
        -------
        SearchResult
            Aggregated search result with all collected records.

        """
        per_page = min(max_results, MAX_PER_PAGE)
        all_records: list[DigitalNZRecord] = []
        total_count = 0
        request_url: str | None = None
        page = 1
        while len(all_records) < max_results:
            result = self.search(
                query=query, fields=fields, per_page=per_page, page=page,
            )
            if not result.records:
                break
            all_records.extend(result.records)
            total_count = result.total_count
            if request_url is None:
                request_url = result.request_url
            page += 1
            if len(result.records) < per_page:
                break
        all_records = all_records[:max_results]
        return SearchResult(
            query=query,
            timestamp=datetime.now(UTC).isoformat(),
            total_count=total_count,
            page=1,
            per_page=len(all_records),
            records=all_records,
            request_url=request_url,
        )

    def get_record(self, record_id: int) -> DigitalNZRecord:
        """Retrieve a single record by its DigitalNZ identifier.

        Parameters
        ----------
        record_id : int
            The DigitalNZ numeric record identifier.

        Returns
        -------
        DigitalNZRecord
            The parsed record.

        """
        endpoint = f"/records/{record_id}.json"
        data = self._request(endpoint, {})
        record_data = data.get("record", data)
        return self._parse_record(record_data)

    def save_fixtures(
        self,
        output_dir: str | Path = "tests/fixtures",
        query: str = "Māori",
        count: int = 3,
    ) -> Path:
        """Save small API response fixtures for testing.

        Parameters
        ----------
        output_dir : str | Path
            Directory to write fixture files to.
        query : str
            Search query for the fixture.
        count : int
            Number of records to include.

        Returns
        -------
        Path
            Path to the fixture directory.

        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        result = self.search(query=query, per_page=count)
        search_fixture = {
            "search": {
                "page": result.page,
                "per_page": result.per_page,
                "result_count": result.total_count,
                "request_url": result.request_url,
                "results": [
                    msgspec.json.decode(msgspec.json.encode(rec))
                    for rec in result.records
                ],
                "facets": {},
            },
            "api_terms_of_use": "https://api.digitalnz.org/terms-of-use",
        }
        search_path = output_path / "digitalnz_search_fixture.json"
        with search_path.open("w", encoding="utf-8") as fh:
            json.dump(search_fixture, fh, indent=2, ensure_ascii=False)
        logger.info("Wrote search fixture to %s", search_path)
        if result.records:
            record = result.records[0]
            record_fixture = {
                "record": msgspec.json.decode(msgspec.json.encode(record)),
            }
            record_path = output_path / "digitalnz_single_record.json"
            with record_path.open("w", encoding="utf-8") as fh:
                json.dump(record_fixture, fh, indent=2, ensure_ascii=False)
            logger.info("Wrote single-record fixture to %s", record_path)
        return output_path.resolve()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _build_cli_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the ``digitalnz-probe`` CLI.

    Returns
    -------
    argparse.ArgumentParser
        Configured argument parser.

    """
    parser = argparse.ArgumentParser(
        prog="digitalnz-probe",
        description="Probe the DigitalNZ API v3 for NZ cultural heritage metadata.",
        epilog=(
            "Examples:\n"
            '  digitalnz-probe --query "Māori land" --output results.json\n'
            '  digitalnz-probe --query "Treaty of Waitangi" '
            '--fields "title,creator,rights" --max-results 10\n'
            "  digitalnz-probe --save-fixtures --query kiwi --output ./tests/fixtures"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        default="New Zealand",
        help="Search query text (default: 'New Zealand').",
    )
    parser.add_argument(
        "--fields", "-f",
        type=str,
        default=None,
        help="Comma-separated list of fields (e.g. 'title,description,creator,rights').",
    )
    parser.add_argument(
        "--max-results", "-n",
        type=int,
        default=20,
        help=f"Maximum number of results (default: 20, max: {MAX_PER_PAGE}).",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Path to write JSON output (default: stdout).",
    )
    parser.add_argument(
        "--save-fixtures",
        action="store_true",
        default=False,
        help="Save fixture responses for testing instead of live query.",
    )
    parser.add_argument(
        "--fixtures-dir",
        type=str,
        default="tests/fixtures",
        help="Directory for fixture output (default: tests/fixtures).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Enable verbose (INFO) logging.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for the DigitalNZ probe.

    Parameters
    ----------
    argv : list[str] | None
        Command-line arguments (default: :data:`sys.argv`).

    Returns
    -------
    int
        Exit code (0 on success, 1 on failure).

    """
    import sys  # noqa: PLC0415

    parser = _build_cli_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)-8s | %(name)s | %(message)s",
            stream=sys.stderr,
        )

    try:
        probe = DigitalNZProbe()

        if args.save_fixtures:
            fixture_path = probe.save_fixtures(
                output_dir=args.fixtures_dir,
                query=args.query,
                count=min(args.max_results, 5),
            )
            logger.info("Fixtures saved to %s", fixture_path)
            if args.output:
                output_path = Path(args.output)
                output_path.write_text(
                    json.dumps({"fixtures_dir": str(fixture_path)}, indent=2),
                    encoding="utf-8",
                )
            return 0

        fields = args.fields.split(",") if args.fields else None
        result = probe.search_all(query=args.query, fields=fields, max_results=args.max_results)
        normalised = [normalise_record(rec) for rec in result.records]

        output = {
            "query": result.query,
            "timestamp": result.timestamp,
            "total_count": result.total_count,
            "returned_count": len(result.records),
            "request_url": result.request_url,
            "records": [msgspec.json.decode(msgspec.json.encode(nrec)) for nrec in normalised],
        }

        output_json = json.dumps(output, indent=2, ensure_ascii=False)

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output_json, encoding="utf-8")
            logger.info("Results written to %s", output_path.resolve())
        else:
            print(output_json)  # noqa: T201

    except Exception as exc:  # noqa: BLE001
        logger.exception("DigitalNZ probe failed: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    import sys  # noqa: PLC0415
    sys.exit(main())
