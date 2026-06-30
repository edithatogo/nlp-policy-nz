"""Tests for the DigitalNZ API v3 probe module (Track 21).

Tests use recorded fixture responses (not the live API) to verify:
- Record parsing and field extraction
- Field normalisation to the Open NZ corpus schema
- Rights classification (open, restricted, unknown)
- Pagination handling
- CLI entry point
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import requests

from nlp_policy_nz.digitalnz_probe import (
    DEFAULT_PER_PAGE,
    MAX_PER_PAGE,
    DigitalNZProbe,
    DigitalNZRecord,
    NormalisedRecord,
    SearchResult,
    classify_rights,
    normalise_record,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def search_fixture_data(fixtures_dir: Path) -> dict[str, Any]:
    """Load the search fixture JSON data."""
    path = fixtures_dir / "digitalnz_search_fixture.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture
def record_fixture_data(fixtures_dir: Path) -> dict[str, Any]:
    """Load the single-record fixture JSON data."""
    path = fixtures_dir / "digitalnz_single_record.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture
def sample_records(
    search_fixture_data: dict[str, Any],
) -> list[DigitalNZRecord]:
    """Parse the search fixture into DigitalNZRecord objects."""
    probe = DigitalNZProbe()
    results = search_fixture_data["search"]["results"]
    return [probe._parse_record(raw) for raw in results]


@pytest.fixture
def mock_response(
    monkeypatch: pytest.MonkeyPatch,
    search_fixture_data: dict[str, Any],
) -> dict[str, Any]:
    """Mock requests.Session.get to return fixture data."""

    def _mock_get(
        self: Any,  # noqa: ARG001, ARG002
        url: str,  # noqa: ARG001
        **kwargs: Any,  # noqa: ARG001, ARG002
    ) -> requests.Response:
        resp = requests.Response()
        resp.status_code = 200
        resp._content = json.dumps(search_fixture_data).encode("utf-8")  # noqa: SLF001
        resp.headers["Content-Type"] = "application/json"
        return resp

    monkeypatch.setattr("requests.Session.get", _mock_get)
    return search_fixture_data


# ---------------------------------------------------------------------------
# Struct tests
# ---------------------------------------------------------------------------


class TestDigitalNZRecord:
    """Tests for the DigitalNZRecord msgspec struct."""

    def test_struct_creation_minimal(self) -> None:
        """Verify a DigitalNZRecord can be created with just an ID."""
        rec = DigitalNZRecord(record_id=42)
        assert rec.record_id == 42
        assert rec.title is None
        assert rec.creator is None

    def test_struct_creation_full(
        self,
        sample_records: list[DigitalNZRecord],
    ) -> None:
        """Verify all fields are populated from fixture data."""
        rec = sample_records[0]
        assert rec.record_id == 1234567
        assert rec.title == "Tram going up Maori Hill in Dunedin"
        assert rec.description is not None
        assert rec.creator == ["Not specified"]
        assert rec.date == ["1920-01-01T12:00:00.000Z"]
        assert rec.display_collection == "TAPUHI"
        assert rec.category == ["Images"]

    def test_struct_raw_dict(
        self,
        sample_records: list[DigitalNZRecord],
    ) -> None:
        """Verify unknown fields are captured in the raw dict."""
        rec = sample_records[0]
        assert rec.raw is not None
        assert "provenance" in rec.raw
        assert "subject" in rec.raw


class TestSearchResult:
    """Tests for the SearchResult msgspec struct."""

    def test_search_result_creation(self) -> None:
        """Verify SearchResult can be created."""
        result = SearchResult(
            query="test",
            timestamp="2025-01-01T00:00:00+00:00",
            total_count=100,
            page=1,
            per_page=20,
            records=[],
        )
        assert result.query == "test"
        assert result.total_count == 100
        assert len(result.records) == 0


class TestNormalisedRecord:
    """Tests for the NormalisedRecord msgspec struct."""

    def test_normalised_record_creation(self) -> None:
        """Verify NormalisedRecord can be created."""
        rec = NormalisedRecord(
            record_id=1,
            display_title="Test",
            rights_classification="open",
        )
        assert rec.record_id == 1
        assert rec.display_title == "Test"
        assert rec.rights_classification == "open"


# ---------------------------------------------------------------------------
# Rights classification tests
# ---------------------------------------------------------------------------


class TestClassifyRights:
    """Tests for rights classification logic."""

    def test_open_creative_commons(self) -> None:
        """CC license is classified as open."""
        rec = DigitalNZRecord(
            record_id=1,
            rights="http://creativecommons.org/licenses/by/4.0/",
        )
        assert classify_rights(rec) == "open"

    def test_open_public_domain(self) -> None:
        """Public domain is classified as open."""
        rec = DigitalNZRecord(
            record_id=2,
            rights="http://creativecommons.org/publicdomain/mark/1.0/",
        )
        assert classify_rights(rec) == "open"

    def test_open_via_usage(self) -> None:
        """No known copyright in usage is classified as open."""
        rec = DigitalNZRecord(
            record_id=3,
            rights=None,
            usage=["No known copyright", "Share"],
        )
        assert classify_rights(rec) == "open"

    def test_restricted_all_rights_reserved(self) -> None:
        """All rights reserved is classified as restricted."""
        rec = DigitalNZRecord(
            record_id=4,
            copyright=["All rights reserved"],
        )
        assert classify_rights(rec) == "restricted"

    def test_restricted_inc(self) -> None:
        """InC rights statement is classified as restricted."""
        rec = DigitalNZRecord(
            record_id=5,
            rights="https://rightsstatements.org/vocab/InC/1.0/",
        )
        assert classify_rights(rec) == "restricted"

    def test_restricted_via_rights_url(self) -> None:
        """InC via rights_url is classified as restricted."""
        rec = DigitalNZRecord(
            record_id=6,
            rights=None,
            rights_url=["https://rightsstatements.org/vocab/InC/1.0/"],
        )
        assert classify_rights(rec) == "restricted"

    def test_unknown_no_rights_info(self) -> None:
        """No rights info at all is classified as unknown."""
        rec = DigitalNZRecord(record_id=7)
        assert classify_rights(rec) == "unknown"

    def test_fixture_open_record(
        self,
        sample_records: list[DigitalNZRecord],
    ) -> None:
        """Verify first fixture record is classified as open."""
        assert classify_rights(sample_records[0]) == "open"

    def test_fixture_public_domain_record(
        self,
        sample_records: list[DigitalNZRecord],
    ) -> None:
        """Verify second fixture record is classified as open."""
        assert classify_rights(sample_records[1]) == "open"

    def test_fixture_restricted_record(
        self,
        sample_records: list[DigitalNZRecord],
    ) -> None:
        """Verify third fixture record is classified as restricted."""
        assert classify_rights(sample_records[2]) == "restricted"


# ---------------------------------------------------------------------------
# Normalisation tests
# ---------------------------------------------------------------------------


class TestNormaliseRecord:
    """Tests for record normalisation to the Open NZ Corpus schema."""

    def test_normalise_restricted_record(
        self,
        sample_records: list[DigitalNZRecord],
    ) -> None:
        """Verify a restricted record is normalised correctly."""
        nrec = normalise_record(sample_records[2])
        assert nrec.rights_classification == "restricted"
        assert "rightsstatements.org" in nrec.rights_note
        assert nrec.record_id == 1234569

    def test_normalise_maps_title_to_display_title(
        self,
        sample_records: list[DigitalNZRecord],
    ) -> None:
        """Verify title is mapped to display_title."""
        nrec = normalise_record(sample_records[0])
        assert nrec.display_title == "Tram going up Maori Hill in Dunedin"

    def test_normalise_no_date(self) -> None:
        """Record with no date should have None published_date."""
        rec = DigitalNZRecord(record_id=99, title="No date")
        nrec = normalise_record(rec)
        assert nrec.published_date is None

    def test_normalise_open_record(
        self,
        sample_records: list[DigitalNZRecord],
    ) -> None:
        """Verify an open-licensed record is normalised correctly."""
        nrec = normalise_record(sample_records[0])
        assert nrec.display_title == sample_records[0].title
        assert nrec.description == sample_records[0].description
        assert nrec.creator == sample_records[0].creator
        assert nrec.published_date == "1920-01-01T12:00:00.000Z"
        assert nrec.rights_classification == "open"
        assert "creativecommons" in nrec.rights_note.lower()
        assert nrec.source_url == sample_records[0].landing_url
        assert nrec.source_name == "Dunedin City Library"
        assert nrec.collection == "TAPUHI"
        assert nrec.category == ["Images"]

    def test_normalise_no_identifier(self) -> None:
        """Record with no dc_identifier has None canonical_uri."""
        rec = DigitalNZRecord(record_id=100, title="No identifier")
        nrec = normalise_record(rec)
        assert nrec.canonical_uri is None

    def test_normalise_preserves_raw_record_ref(
        self,
        sample_records: list[DigitalNZRecord],
    ) -> None:
        """Verify raw_record reference is preserved."""
        nrec = normalise_record(sample_records[0])
        assert nrec.raw_record is sample_records[0]


# ---------------------------------------------------------------------------
# Probe class tests (with mocked HTTP)
# ---------------------------------------------------------------------------


class TestDigitalNZProbe:
    """Tests for the DigitalNZProbe class using mocked HTTP."""

    def test_init_defaults(self) -> None:
        """Verify default initialisation."""
        probe = DigitalNZProbe()
        assert probe._base_url == "https://api.digitalnz.org/v3"
        assert probe._api_key is None

    def test_init_with_api_key(self) -> None:
        """Verify API key is set in session headers."""
        probe = DigitalNZProbe(api_key="test-key-123")
        assert probe._session.headers.get("Authentication-Token") == "test-key-123"

    def test_search_with_mock(
        self,
        mock_response: dict[str, Any],
    ) -> None:
        """Verify search returns structured results with mocked API."""
        probe = DigitalNZProbe()
        result = probe.search(query="Māori", per_page=3)
        assert isinstance(result, SearchResult)
        assert result.total_count == 864030
        assert len(result.records) == 3
        assert result.records[0].title == "Tram going up Maori Hill in Dunedin"

    def test_search_invalid_per_page_too_high(self) -> None:
        """Verify per_page > MAX_PER_PAGE raises ValueError."""
        probe = DigitalNZProbe()
        with pytest.raises(ValueError, match="per_page"):
            probe.search(query="test", per_page=MAX_PER_PAGE + 1)

    def test_search_invalid_page(self) -> None:
        """Verify page < 1 raises ValueError."""
        probe = DigitalNZProbe()
        with pytest.raises(ValueError, match="page"):
            probe.search(query="test", page=0)

    def test_search_all_with_mock(
        self,
        mock_response: dict[str, Any],
    ) -> None:
        """Verify search_all returns aggregated results."""
        probe = DigitalNZProbe()
        result = probe.search_all(query="Māori", max_results=5)
        assert len(result.records) <= 5
        assert result.total_count > 0

    def test_parse_record(
        self,
        record_fixture_data: dict[str, Any],
    ) -> None:
        """Verify raw dict is correctly parsed into DigitalNZRecord."""
        probe = DigitalNZProbe()
        raw = record_fixture_data["record"]
        rec = probe._parse_record(raw)
        assert rec.record_id == 1234567
        assert rec.title == "Tram going up Maori Hill in Dunedin"
        assert rec.creator == ["Not specified"]

    def test_rate_limit_enforcement(self) -> None:
        """Verify rate limiter adds delay between requests."""
        import time  # noqa: PLC0415

        probe = DigitalNZProbe(request_delay=0.1)
        start = time.monotonic()
        probe._rate_limit()
        probe._rate_limit()
        elapsed = time.monotonic() - start
        assert elapsed >= 0.1

    def test_search_all_breaks_when_no_more_results(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Verify search_all stops when API returns fewer results."""
        probe = DigitalNZProbe()
        call_count: int = 0

        def _one_page_mock(
            self: Any,  # noqa: ARG001, ARG002
            url: str,  # noqa: ARG001
            **kwargs: Any,  # noqa: ARG001, ARG002
        ) -> requests.Response:
            nonlocal call_count
            call_count += 1
            data = {
                "search": {
                    "page": 1,
                    "per_page": 2,
                    "result_count": 2,
                    "results": [{"id": i, "title": f"Record {i}"} for i in range(1, 3)],
                }
            }
            resp = requests.Response()
            resp.status_code = 200
            resp._content = json.dumps(data).encode("utf-8")
            resp.headers["Content-Type"] = "application/json"
            return resp

        monkeypatch.setattr("requests.Session.get", _one_page_mock)
        result = probe.search_all(query="test", max_results=10)
        assert len(result.records) == 2
        assert call_count == 1


# ---------------------------------------------------------------------------
# Pagination tests
# ---------------------------------------------------------------------------


class TestPagination:
    """Tests for pagination handling."""

    def test_search_per_page_default(self) -> None:
        """Verify default per_page is DEFAULT_PER_PAGE."""
        assert DEFAULT_PER_PAGE == 20

    def test_max_per_page_constant(self) -> None:
        """Verify MAX_PER_PAGE is 100."""
        assert MAX_PER_PAGE == 100

    def test_search_all_with_multi_page_mock(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Verify search_all fetches multiple pages."""
        probe = DigitalNZProbe()
        call_count: int = 0

        def _multi_page_mock(
            self: Any,  # noqa: ARG001, ARG002
            url: str,  # noqa: ARG001
            **kwargs: Any,  # noqa: ARG001, ARG002
        ) -> requests.Response:
            nonlocal call_count
            call_count += 1
            start_id = (call_count - 1) * 2 + 1
            data = {
                "search": {
                    "page": call_count,
                    "per_page": 2,
                    "result_count": 10,
                    "results": [
                        {"id": i, "title": f"Record {i}"} for i in range(start_id, start_id + 2)
                    ],
                }
            }
            resp = requests.Response()
            resp.status_code = 200
            resp._content = json.dumps(data).encode("utf-8")
            resp.headers["Content-Type"] = "application/json"
            return resp

        monkeypatch.setattr("requests.Session.get", _multi_page_mock)
        result = probe.search_all(query="test", max_results=3)
        assert len(result.records) == 2
        assert call_count == 1


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


class TestCLI:
    """Tests for the CLI entry point."""

    def test_main_help(self) -> None:
        """Verify --help exits with code 0."""
        from nlp_policy_nz.digitalnz_probe import main as cli_main  # noqa: PLC0415

        with pytest.raises(SystemExit) as exc:
            cli_main(argv=["--help"])
        assert exc.value.code == 0

    def test_main_invalid_args(self) -> None:
        """Verify invalid args produce exit code 2."""
        from nlp_policy_nz.digitalnz_probe import main as cli_main  # noqa: PLC0415

        with pytest.raises(SystemExit) as exc:
            cli_main(argv=["--unknown-flag"])
        assert exc.value.code == 2

    def test_main_save_fixtures(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Verify --save-fixtures writes fixture files."""
        from nlp_policy_nz.digitalnz_probe import main as cli_main  # noqa: PLC0415

        fixtures_dir = tmp_path / "fixtures"
        output_file = tmp_path / "output.json"
        fixture_path = (
            Path(__file__).resolve().parent / "fixtures" / "digitalnz_search_fixture.json"
        )
        with fixture_path.open("r", encoding="utf-8") as fh:
            fixture_data = json.load(fh)

        def _mock_request(
            self: Any,
            endpoint: str,
            params: dict[str, Any],  # noqa: ARG001
        ) -> dict[str, Any]:
            return fixture_data

        monkeypatch.setattr(
            "nlp_policy_nz.digitalnz_probe.DigitalNZProbe._request",
            _mock_request,
        )

        result = cli_main(
            argv=[
                "--save-fixtures",
                "--query",
                "Māori",
                "--max-results",
                "3",
                "--fixtures-dir",
                str(fixtures_dir),
                "--output",
                str(output_file),
            ]
        )
        assert result == 0
        assert (fixtures_dir / "digitalnz_search_fixture.json").exists()
        assert (fixtures_dir / "digitalnz_single_record.json").exists()

    def test_main_query_output(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Verify --query with --output writes results JSON."""
        from nlp_policy_nz.digitalnz_probe import main as cli_main  # noqa: PLC0415

        output_file = tmp_path / "results.json"
        fixture_path = (
            Path(__file__).resolve().parent / "fixtures" / "digitalnz_search_fixture.json"
        )
        with fixture_path.open("r", encoding="utf-8") as fh:
            fixture_data = json.load(fh)

        def _mock_request(
            self: Any,
            endpoint: str,
            params: dict[str, Any],  # noqa: ARG001
        ) -> dict[str, Any]:
            return fixture_data

        monkeypatch.setattr(
            "nlp_policy_nz.digitalnz_probe.DigitalNZProbe._request",
            _mock_request,
        )

        result = cli_main(
            argv=[
                "--query",
                "Māori",
                "--max-results",
                "3",
                "--output",
                str(output_file),
            ]
        )
        assert result == 0
        assert output_file.exists()
        with output_file.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        assert data["query"] == "Māori"
        assert data["total_count"] == 864030
        assert len(data["records"]) == 3
        assert "display_title" in data["records"][0]
        assert "rights_classification" in data["records"][0]
