"""Tests for the release workflow and versioning module.

Verifies :class:`ReleaseManager` archive creation, Zenodo publication,
and end-to-end release flows with mocked API calls.
"""

from __future__ import annotations

import json
import tarfile
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from nlp_policy_nz.integrations.release import ReleaseManager


@pytest.fixture
def sample_parquet(tmp_path: Path) -> Path:
    """Create a small sample Parquet file for testing."""
    table = pa.table(
        {
            "doc_id": ["doc1", "doc2", "doc3"],
            "text": ["Hello world", "Test document", "Third item"],
            "source": ["legislation", "legislation", "hansard"],
        }
    )
    path = tmp_path / "sample.parquet"
    pq.write_table(table, path)
    return path


@pytest.fixture
def mock_publish_response() -> dict:
    """Return a simulated Zenodo publish response."""
    return {
        "id": 22222,
        "doi": "10.5072/zenodo.22222",
        "state": "done",
        "title": "Test Release",
    }


class TestCreateReleaseArchive:
    """Tests for :meth:`ReleaseManager.create_release_archive`."""

    def test_creates_tar_gz(self, sample_parquet: Path, tmp_path: Path) -> None:
        """Archive is a valid .tar.gz file."""
        manager = ReleaseManager(token="tok")
        archive_path = manager.create_release_archive(
            sample_parquet,
            version="1.0.0",
            title="Test Release",
            description="A test release.",
            creators=[{"name": "Doe, Jane"}],
            output_dir=tmp_path,
        )

        assert archive_path.exists()
        assert archive_path.suffix == ".gz"
        assert archive_path.name == "nlp-policy-nz-1.0.0.tar.gz"

        with tarfile.open(archive_path, "r:gz") as tar:
            names = tar.getnames()
            assert "sample.parquet" in names
            assert "metadata.json" in names

    def test_metadata_json_content(self, sample_parquet: Path, tmp_path: Path) -> None:
        """Metadata JSON contains expected fields."""
        manager = ReleaseManager(token="tok")
        archive_path = manager.create_release_archive(
            sample_parquet,
            version="2.1.0",
            title="My Release",
            description="Release desc.",
            creators=[{"name": "Smith, John"}],
            output_dir=tmp_path,
        )

        with tarfile.open(archive_path, "r:gz") as tar:
            metadata_member = tar.extractfile("metadata.json")
            assert metadata_member is not None
            metadata = json.loads(metadata_member.read())

        assert metadata["version"] == "2.1.0"
        assert metadata["title"] == "My Release"
        assert metadata["doc_id_count"] == 3  # noqa: PLR2004
        assert metadata["corpus_source"] == "sample"
        assert metadata["creators"] == [{"name": "Smith, John"}]

    def test_parquet_file_not_found(self, tmp_path: Path) -> None:
        """FileNotFoundError raised for missing Parquet file."""
        manager = ReleaseManager()
        with pytest.raises(FileNotFoundError, match="Parquet file not found"):
            manager.create_release_archive(
                tmp_path / "missing.parquet",
                version="1.0.0",
                title="T",
                description="D",
                creators=[{"name": "A"}],
                output_dir=tmp_path,
            )

    def test_auto_output_dir(self, sample_parquet: Path) -> None:
        """Archive is created in a temp directory when output_dir is None."""
        manager = ReleaseManager()
        archive_path = manager.create_release_archive(
            sample_parquet,
            version="0.1.0",
            title="Auto",
            description="Auto dir.",
            creators=[{"name": "A"}],
        )
        assert archive_path.exists()
        archive_path.unlink(missing_ok=True)


class TestPublishToZenodo:
    """Tests for :meth:`ReleaseManager.publish_to_zenodo`."""

    def test_publishes_archive(
        self,
        sample_parquet: Path,
        mock_publish_response: dict,
        tmp_path: Path,
    ) -> None:
        """Archive is published to Zenodo successfully."""
        manager = ReleaseManager(token="tok")
        archive_path = manager.create_release_archive(
            sample_parquet,
            version="1.0.0",
            title="Test",
            description="Desc",
            creators=[{"name": "A"}],
            output_dir=tmp_path,
        )

        with (
            pytest.mock.patch(
                "nlp_policy_nz.integrations.zenodo_archive.create_sandbox_deposit",
                return_value={"id": 22222},
            ),
            pytest.mock.patch(
                "nlp_policy_nz.integrations.zenodo_archive.upload_file_to_deposit",
                return_value={},
            ),
            pytest.mock.patch(
                "nlp_policy_nz.integrations.zenodo_archive.publish_deposit",
                return_value=mock_publish_response,
            ),
        ):
            result = manager.publish_to_zenodo(
                archive_path,
                title="Test",
                description="Desc",
                creators=[{"name": "A"}],
            )

        assert result["doi"] == "10.5072/zenodo.22222"


class TestFullRelease:
    """Tests for :meth:`ReleaseManager.full_release`."""

    def test_full_release_end_to_end(
        self, sample_parquet: Path, mock_publish_response: dict
    ) -> None:
        """Full release creates archive and publishes to Zenodo."""
        manager = ReleaseManager(token="tok")

        with (
            pytest.mock.patch(
                "nlp_policy_nz.integrations.zenodo_archive.create_sandbox_deposit",
                return_value={"id": 22222},
            ),
            pytest.mock.patch(
                "nlp_policy_nz.integrations.zenodo_archive.upload_file_to_deposit",
                return_value={},
            ),
            pytest.mock.patch(
                "nlp_policy_nz.integrations.zenodo_archive.publish_deposit",
                return_value=mock_publish_response,
            ),
        ):
            result = manager.full_release(
                sample_parquet,
                version="3.0.0",
                title="Full Release",
                description="End-to-end test.",
                creators=[{"name": "Doe, Jane"}],
            )

        assert result["doi"] == "10.5072/zenodo.22222"

    def test_full_release_parquet_not_found(self) -> None:
        """FileNotFoundError raised when Parquet file is missing."""
        manager = ReleaseManager()
        with pytest.raises(FileNotFoundError, match="Parquet file not found"):
            manager.full_release(
                Path("/nonexistent/data.parquet"),
                version="1.0.0",
                title="T",
                description="D",
                creators=[{"name": "A"}],
            )
