"""Tests for the Zenodo archive builder.

Verifies :class:`ZenodoArchiver` and :func:`archive_to_zenodo` with
mocked API calls covering successful flows, error cases, and DOI
retrieval.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from nlp_policy_nz.integrations.zenodo import DepositError
from nlp_policy_nz.integrations.zenodo_archive import (
    ZenodoArchiver,
    archive_to_zenodo,
)


@pytest.fixture
def mock_deposit_response() -> dict:
    """Return a simulated Zenodo deposit creation response."""
    return {"id": 12345, "title": "Test Deposit"}


@pytest.fixture
def mock_upload_response() -> dict:
    """Return a simulated Zenodo file upload response."""
    return {"key": "test.parquet", "size": 1024}


@pytest.fixture
def mock_publish_response() -> dict:
    """Return a simulated Zenodo publish response."""
    return {
        "id": 12345,
        "doi": "10.5072/zenodo.12345",
        "state": "done",
        "title": "Test Deposit",
    }


class TestZenodoArchiver:
    """Tests for the :class:`ZenodoArchiver` class."""

    def test_init_with_token(self) -> None:
        """Archiver stores an explicit token."""
        archiver = ZenodoArchiver(token="tok-123")
        assert archiver._token == "tok-123"  # noqa: S105

    def test_init_without_token(self) -> None:
        """Archiver defaults token to None."""
        archiver = ZenodoArchiver()
        assert archiver._token is None

    def test_resolve_token_explicit(self) -> None:
        """Explicit token is returned without env lookup."""
        archiver = ZenodoArchiver(token="my-tok")
        assert archiver._resolve_token() == "my-tok"

    def test_resolve_token_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Token falls back to environment variable."""
        monkeypatch.setenv("ZENODO_SANDBOX_TOKEN", "env-tok")
        archiver = ZenodoArchiver()
        assert archiver._resolve_token() == "env-tok"

    def test_create_archive_file_not_found(self, tmp_path) -> None:
        """FileNotFoundError raised for missing file."""
        archiver = ZenodoArchiver(token="tok")
        with pytest.raises(FileNotFoundError, match="File not found"):
            archiver.create_archive(
                title="T",
                description="D",
                creators=[{"name": "A"}],
                file_path=tmp_path / "missing.parquet",
            )

    def test_create_archive_full_flow(
        self,
        tmp_path,
        mock_deposit_response,
        mock_upload_response,
        mock_publish_response,
    ) -> None:
        """Full create, upload, publish flow succeeds."""
        dummy_file = tmp_path / "data.parquet"
        dummy_file.write_bytes(b"parquet-data")

        archiver = ZenodoArchiver(token="tok-123")

        with (
            patch(
                "nlp_policy_nz.integrations.zenodo_archive.create_sandbox_deposit",
                return_value=mock_deposit_response,
            ) as mock_create,
            patch(
                "nlp_policy_nz.integrations.zenodo_archive.upload_file_to_deposit",
                return_value=mock_upload_response,
            ) as mock_upload,
            patch(
                "nlp_policy_nz.integrations.zenodo_archive.publish_deposit",
                return_value=mock_publish_response,
            ) as mock_publish,
        ):
            result = archiver.create_archive(
                title="Test",
                description="Desc",
                creators=[{"name": "Doe, Jane"}],
                file_path=str(dummy_file),
            )

        mock_create.assert_called_once()
        mock_upload.assert_called_once()
        mock_publish.assert_called_once()
        assert result["doi"] == "10.5072/zenodo.12345"

    def test_create_archive_api_failure(self, tmp_path) -> None:
        """DepositError raised when API call fails."""
        dummy_file = tmp_path / "data.parquet"
        dummy_file.write_bytes(b"parquet-data")

        archiver = ZenodoArchiver(token="tok")

        with (
            patch(
                "nlp_policy_nz.integrations.zenodo_archive.create_sandbox_deposit",
                side_effect=DepositError("API error", status_code=500),
            ),
            pytest.raises(DepositError, match="API error"),
        ):
            archiver.create_archive(
                title="T",
                description="D",
                creators=[{"name": "A"}],
                file_path=str(dummy_file),
            )


class TestArchiveToZenodo:
    """Tests for the :func:`archive_to_zenodo` convenience function."""

    def test_archive_to_zenodo_full_flow(
        self,
        tmp_path,
        mock_deposit_response,
        mock_upload_response,
        mock_publish_response,
    ) -> None:
        """Convenience function delegates to archiver correctly."""
        dummy_file = tmp_path / "data.parquet"
        dummy_file.write_bytes(b"parquet-data")

        with (
            patch(
                "nlp_policy_nz.integrations.zenodo_archive.create_sandbox_deposit",
                return_value=mock_deposit_response,
            ),
            patch(
                "nlp_policy_nz.integrations.zenodo_archive.upload_file_to_deposit",
                return_value=mock_upload_response,
            ),
            patch(
                "nlp_policy_nz.integrations.zenodo_archive.publish_deposit",
                return_value=mock_publish_response,
            ),
        ):
            result = archive_to_zenodo(
                title="Test",
                description="Desc",
                creators=[{"name": "Doe, Jane"}],
                file_path=str(dummy_file),
                token="tok",
            )

        assert result["doi"] == "10.5072/zenodo.12345"

    def test_archive_to_zenodo_file_not_found(self, tmp_path) -> None:
        """FileNotFoundError raised for missing file."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            archive_to_zenodo(
                title="T",
                description="D",
                creators=[{"name": "A"}],
                file_path=tmp_path / "missing.parquet",
                token="tok",
            )


class TestGetDoi:
    """Tests for :meth:`ZenodoArchiver.get_doi`."""

    def test_get_doi_success(self) -> None:
        """DOI returned from published deposit."""
        archiver = ZenodoArchiver(token="tok")

        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"doi": "10.5072/zenodo.99999"}

        with patch(
            "nlp_policy_nz.integrations.zenodo_archive.requests.get",
            return_value=mock_resp,
        ):
            doi = archiver.get_doi("99999")

        assert doi == "10.5072/zenodo.99999"

    def test_get_doi_no_doi(self) -> None:
        """None returned when deposit has no DOI."""
        archiver = ZenodoArchiver(token="tok")

        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"title": "Draft"}

        with patch(
            "nlp_policy_nz.integrations.zenodo_archive.requests.get",
            return_value=mock_resp,
        ):
            doi = archiver.get_doi("11111")

        assert doi is None

    def test_get_doi_api_error(self) -> None:
        """DepositError raised on API failure."""
        archiver = ZenodoArchiver(token="tok")

        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 404
        mock_resp.reason = "Not Found"
        mock_resp.text = "not found"

        with (
            patch(
                "nlp_policy_nz.integrations.zenodo_archive.requests.get",
                return_value=mock_resp,
            ),
            pytest.raises(DepositError, match="Failed to fetch deposit"),
        ):
            archiver.get_doi("40400")


class TestProductionEnvironment:
    """Tests for production environment support."""

    def test_archiver_production_environment_stored(self) -> None:
        """ZenodoArchiver stores the production environment."""
        archiver = ZenodoArchiver(token="tok", environment="production")
        assert archiver._environment == "production"

    def test_archiver_default_environment_is_sandbox(self) -> None:
        """ZenodoArchiver defaults to sandbox environment."""
        archiver = ZenodoArchiver(token="tok")
        assert archiver._environment == "sandbox"

    def test_archive_to_zenodo_passes_environment(
        self,
        tmp_path,
        mock_deposit_response,
        mock_upload_response,
        mock_publish_response,
    ) -> None:
        """archive_to_zenodo passes environment through to the archiver."""
        dummy_file = tmp_path / "data.parquet"
        dummy_file.write_bytes(b"parquet-data")

        with (
            patch(
                "nlp_policy_nz.integrations.zenodo_archive.create_sandbox_deposit",
                return_value=mock_deposit_response,
            ) as mock_create,
            patch(
                "nlp_policy_nz.integrations.zenodo_archive.upload_file_to_deposit",
                return_value=mock_upload_response,
            ) as mock_upload,
            patch(
                "nlp_policy_nz.integrations.zenodo_archive.publish_deposit",
                return_value=mock_publish_response,
            ) as mock_publish,
        ):
            archive_to_zenodo(
                title="Test",
                description="Desc",
                creators=[{"name": "Doe, Jane"}],
                file_path=str(dummy_file),
                token="tok",
                environment="production",
            )

        # Each low-level call should receive environment="production"
        for call in mock_create.call_args_list:
            assert call.kwargs.get("environment") == "production"
        for call in mock_upload.call_args_list:
            assert call.kwargs.get("environment") == "production"
        for call in mock_publish.call_args_list:
            assert call.kwargs.get("environment") == "production"

    def test_create_archive_production_uses_production_url(
        self,
        tmp_path,
        mock_deposit_response,
        mock_upload_response,
        mock_publish_response,
    ) -> None:
        """create_archive with environment='production' passes it through."""
        dummy_file = tmp_path / "data.parquet"
        dummy_file.write_bytes(b"parquet-data")

        archiver = ZenodoArchiver(token="tok", environment="production")

        with (
            patch(
                "nlp_policy_nz.integrations.zenodo_archive.create_sandbox_deposit",
                return_value=mock_deposit_response,
            ) as mock_create,
            patch(
                "nlp_policy_nz.integrations.zenodo_archive.upload_file_to_deposit",
                return_value=mock_upload_response,
            ) as mock_upload,
            patch(
                "nlp_policy_nz.integrations.zenodo_archive.publish_deposit",
                return_value=mock_publish_response,
            ) as mock_publish,
        ):
            archiver.create_archive(
                title="Test",
                description="Desc",
                creators=[{"name": "Doe, Jane"}],
                file_path=str(dummy_file),
            )

        for call in mock_create.call_args_list:
            assert call.kwargs.get("environment") == "production"
        for call in mock_upload.call_args_list:
            assert call.kwargs.get("environment") == "production"
        for call in mock_publish.call_args_list:
            assert call.kwargs.get("environment") == "production"
