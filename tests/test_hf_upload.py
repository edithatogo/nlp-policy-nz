"""Tests for Hugging Face Hub Upload Integration (Track 8, Task 1.1).

Tests the dataset upload pipeline: Parquet → HF Dataset conversion,
repository creation, and push-to-hub functionality.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import datasets
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from nlp_policy_nz.integrations.hf_uploader import (
    UploadError,
    _resolve_token,
    create_dataset_repo,
    deploy_space,
    get_hf_token,
    parquet_to_dataset,
    push_dataset_to_hub,
)
from nlp_policy_nz.storage.serialization import (
    PipelineRecord,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_records() -> list[PipelineRecord]:
    """Return a small list of pipeline records for testing."""
    return [
        PipelineRecord(
            doc_id="leg-001",
            corpus_source="legislation",
            raw_text="This is the text of the first Act.",
            cleaned_tokens=["This", "is", "the", "text"],
            nz_act_citations=["Act 2023 No 1"],
            te_reo_terms=["Aotearoa"],
            embeddings=[0.1, 0.2, 0.3],
        ),
        PipelineRecord(
            doc_id="han-001",
            corpus_source="hansard",
            raw_text="Speech from the member.",
            cleaned_tokens=["Speech", "from", "the", "member"],
            nz_act_citations=[],
            te_reo_terms=["kōrero"],
            embeddings=None,
        ),
    ]


@pytest.fixture
def sample_parquet(tmp_path: Path, sample_records: list[PipelineRecord]) -> Path:
    """Create and return a temporary Parquet file with sample records."""
    path = tmp_path / "sample.parquet"
    data = {
        "doc_id": [r.doc_id for r in sample_records],
        "corpus_source": [r.corpus_source for r in sample_records],
        "raw_text": [r.raw_text for r in sample_records],
        "cleaned_tokens": [r.cleaned_tokens for r in sample_records],
        "nz_act_citations": [r.nz_act_citations for r in sample_records],
        "te_reo_terms": [r.te_reo_terms for r in sample_records],
        "embeddings": [r.embeddings for r in sample_records],
    }
    table = pa.table(data)
    pq.write_table(table, str(path))
    return path


# ---------------------------------------------------------------------------
# Token resolution tests
# ---------------------------------------------------------------------------


class TestTokenResolution:
    """Tests for HF token resolution helpers."""

    def test_get_hf_token_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify token is read from HF_TOKEN env var."""
        monkeypatch.setenv("HF_TOKEN", "test-token-123")
        assert get_hf_token() == "test-token-123"

    def test_get_hf_token_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify ValueError is raised when HF_TOKEN is not set."""
        monkeypatch.delenv("HF_TOKEN", raising=False)
        with pytest.raises(ValueError, match="HF_TOKEN"):
            get_hf_token()

    def test_resolve_token_explicit(self) -> None:
        """Verify explicit token is returned as-is."""
        assert _resolve_token("explicit-token") == "explicit-token"

    def test_resolve_token_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify fallback to env var when token is None."""
        monkeypatch.setenv("HF_TOKEN", "env-token")
        assert _resolve_token(None) == "env-token"

    def test_resolve_token_none_when_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify None returned when neither explicit nor env token is set."""
        monkeypatch.delenv("HF_TOKEN", raising=False)
        assert _resolve_token(None) is None


# ---------------------------------------------------------------------------
# Parquet → Dataset conversion tests
# ---------------------------------------------------------------------------


class TestParquetToDataset:
    """Tests for :func:`parquet_to_dataset`."""

    def test_conversion(self, sample_parquet: Path) -> None:
        """Verify a Parquet file converts to a HF Dataset."""
        ds = parquet_to_dataset(sample_parquet)
        assert isinstance(ds, datasets.Dataset)
        assert len(ds) == 2

    def test_columns_preserved(self, sample_parquet: Path) -> None:
        """Verify all pipeline schema columns are present."""
        ds = parquet_to_dataset(sample_parquet)
        assert "doc_id" in ds.column_names
        assert "corpus_source" in ds.column_names
        assert "raw_text" in ds.column_names

    def test_file_not_found(self) -> None:
        """Verify FileNotFoundError for a missing Parquet file."""
        with pytest.raises(FileNotFoundError, match="not found"):
            parquet_to_dataset("/nonexistent/file.parquet")

    def test_string_path(self, sample_parquet: Path) -> None:
        """Verify string paths are accepted."""
        ds = parquet_to_dataset(str(sample_parquet))
        assert len(ds) == 2


# ---------------------------------------------------------------------------
# Repository creation tests
# ---------------------------------------------------------------------------


class TestCreateDatasetRepo:
    """Tests for :func:`create_dataset_repo`."""

    @patch("nlp_policy_nz.integrations.hf_uploader.HfApi")
    def test_creates_repo(self, mock_api_cls: MagicMock) -> None:
        """Verify HfApi.create_repo is called with correct parameters."""
        mock_api = MagicMock()
        mock_api_cls.return_value = mock_api
        mock_api.create_repo.return_value = "https://huggingface.co/datasets/test/repo"

        url = create_dataset_repo("test/repo", private=False, token="tok")

        assert url == "https://huggingface.co/datasets/test/repo"
        mock_api.create_repo.assert_called_once_with(
            repo_id="test/repo",
            repo_type="dataset",
            private=False,
            exist_ok=True,
        )

    @patch("nlp_policy_nz.integrations.hf_uploader.HfApi")
    def test_private_repo(self, mock_api_cls: MagicMock) -> None:
        """Verify private flag is passed through."""
        mock_api = MagicMock()
        mock_api_cls.return_value = mock_api
        mock_api.create_repo.return_value = "https://huggingface.co/datasets/pvt/repo"

        create_dataset_repo("pvt/repo", private=True, token="tok")
        mock_api.create_repo.assert_called_once_with(
            repo_id="pvt/repo",
            repo_type="dataset",
            private=True,
            exist_ok=True,
        )


# ---------------------------------------------------------------------------
# Push to Hub tests
# ---------------------------------------------------------------------------


class TestPushDatasetToHub:
    """Tests for :func:`push_dataset_to_hub`."""

    @patch("nlp_policy_nz.integrations.hf_uploader.HfApi")
    @patch("nlp_policy_nz.integrations.hf_uploader.parquet_to_dataset")
    def test_push_success(
        self,
        mock_parquet_to_ds: MagicMock,
        mock_api_cls: MagicMock,
        sample_parquet: Path,
    ) -> None:
        """Verify successful push returns the dataset URL."""
        mock_ds = MagicMock(spec=datasets.Dataset)
        mock_parquet_to_ds.return_value = mock_ds

        mock_api = MagicMock()
        mock_api_cls.return_value = mock_api
        mock_api.create_repo.return_value = "https://huggingface.co/datasets/user/ds"

        url = push_dataset_to_hub(
            sample_parquet,
            "user/ds",
            token="tok",
            commit_message="Upload test",
        )

        assert url == "https://huggingface.co/datasets/user/ds"
        mock_ds.push_to_hub.assert_called_once_with(
            "user/ds",
            split="train",
            token="tok",
            commit_message="Upload test",
        )

    @patch("nlp_policy_nz.integrations.hf_uploader.HfApi")
    @patch("nlp_policy_nz.integrations.hf_uploader.parquet_to_dataset")
    def test_push_default_commit_message(
        self,
        mock_parquet_to_ds: MagicMock,
        mock_api_cls: MagicMock,
        sample_parquet: Path,
    ) -> None:
        """Verify a default commit message is used when none is provided."""
        mock_ds = MagicMock(spec=datasets.Dataset)
        mock_parquet_to_ds.return_value = mock_ds

        mock_api = MagicMock()
        mock_api_cls.return_value = mock_api
        mock_api.create_repo.return_value = "https://huggingface.co/datasets/user/ds"

        push_dataset_to_hub(sample_parquet, "user/ds", token="tok")

        call_kwargs = mock_ds.push_to_hub.call_args
        assert "Upload sample.parquet" in call_kwargs.kwargs["commit_message"]

    def test_push_file_not_found(self) -> None:
        """Verify FileNotFoundError for missing Parquet file."""
        with pytest.raises(FileNotFoundError, match="not found"):
            push_dataset_to_hub("/missing.parquet", "user/ds", token="tok")


# ---------------------------------------------------------------------------
# Deploy Space tests
# ---------------------------------------------------------------------------


class TestDeploySpace:
    """Tests for :func:`deploy_space`."""

    def test_dry_run(self, tmp_path: Path) -> None:
        """Verify dry-run returns URL without uploading."""
        spaces_dir = tmp_path / "spaces"
        spaces_dir.mkdir()
        (spaces_dir / "app.py").write_text("# app")
        (spaces_dir / "requirements.txt").write_text("gradio")

        url = deploy_space(
            "user/test-space",
            spaces_dir=str(spaces_dir),
            token="tok",
            dry_run=True,
        )
        assert "dry-run" in url
        assert "user/test-space" in url

    def test_spaces_dir_not_found(self) -> None:
        """Verify FileNotFoundError for missing spaces directory."""
        with pytest.raises(FileNotFoundError, match="not found"):
            deploy_space("user/space", spaces_dir="/nonexistent/dir", token="tok")

    def test_missing_app_py(self, tmp_path: Path) -> None:
        """Verify FileNotFoundError when app.py is missing."""
        spaces_dir = tmp_path / "spaces"
        spaces_dir.mkdir()
        (spaces_dir / "requirements.txt").write_text("gradio")

        with pytest.raises(FileNotFoundError, match="app.py"):
            deploy_space("user/space", spaces_dir=str(spaces_dir), token="tok")

    def test_missing_requirements_txt(self, tmp_path: Path) -> None:
        """Verify FileNotFoundError when requirements.txt is missing."""
        spaces_dir = tmp_path / "spaces"
        spaces_dir.mkdir()
        (spaces_dir / "app.py").write_text("# app")

        with pytest.raises(FileNotFoundError, match="requirements.txt"):
            deploy_space("user/space", spaces_dir=str(spaces_dir), token="tok")

    @patch("nlp_policy_nz.integrations.hf_uploader.HfApi")
    def test_creates_repo_and_uploads(
        self,
        mock_api_cls: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Verify HfApi is called to create repo and upload folder."""
        spaces_dir = tmp_path / "spaces"
        spaces_dir.mkdir()
        (spaces_dir / "app.py").write_text("# app")
        (spaces_dir / "requirements.txt").write_text("gradio")

        mock_api = MagicMock()
        mock_api_cls.return_value = mock_api

        url = deploy_space(
            "user/test-space",
            spaces_dir=str(spaces_dir),
            token="tok",
            commit_message="Deploy test",
        )

        assert url == "https://huggingface.co/spaces/user/test-space"
        mock_api.create_repo.assert_called_once_with(
            repo_id="user/test-space",
            repo_type="space",
            space_sdk="gradio",
            exist_ok=True,
        )
        mock_api.upload_folder.assert_called_once()

    @patch("nlp_policy_nz.integrations.hf_uploader.HfApi")
    def test_default_commit_message(
        self,
        mock_api_cls: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Verify a default commit message is used when none is provided."""
        spaces_dir = tmp_path / "spaces"
        spaces_dir.mkdir()
        (spaces_dir / "app.py").write_text("# app")
        (spaces_dir / "requirements.txt").write_text("gradio")

        mock_api = MagicMock()
        mock_api_cls.return_value = mock_api

        deploy_space(
            "user/test-space",
            spaces_dir=str(spaces_dir),
            token="tok",
        )

        call_kwargs = mock_api.upload_folder.call_args
        assert "Deploy Gradio Space" in call_kwargs.kwargs["commit_message"]

    @patch("nlp_policy_nz.integrations.hf_uploader.HfApi")
    def test_upload_failure_raises_error(
        self,
        mock_api_cls: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Verify UploadError is raised when upload fails."""
        spaces_dir = tmp_path / "spaces"
        spaces_dir.mkdir()
        (spaces_dir / "app.py").write_text("# app")
        (spaces_dir / "requirements.txt").write_text("gradio")

        mock_api = MagicMock()
        mock_api_cls.return_value = mock_api
        mock_api.upload_folder.side_effect = Exception("Upload failed")

        with pytest.raises(UploadError, match="Failed to deploy Space"):
            deploy_space(
                "user/test-space",
                spaces_dir=str(spaces_dir),
                token="tok",
            )


# ---------------------------------------------------------------------------
# Integration test: Full upload pipeline (mock)
# ---------------------------------------------------------------------------


class TestUploadIntegration:
    """Integration test for the full upload pipeline using mocks.

    Verifies that Parquet → Dataset → Repo creation → Push to Hub works
    end-to-end when all external API calls are mocked.
    """

    @patch("datasets.Dataset.push_to_hub")
    @patch("nlp_policy_nz.integrations.hf_uploader.HfApi")
    def test_full_upload_flow(
        self,
        mock_api_cls: MagicMock,
        mock_push_to_hub: MagicMock,
        sample_parquet: Path,
    ) -> None:
        """Verify the complete upload pipeline works end-to-end."""
        mock_api = MagicMock()
        mock_api_cls.return_value = mock_api
        mock_api.create_repo.return_value = (
            "https://huggingface.co/datasets/user/integration-ds"
        )

        url = push_dataset_to_hub(
            sample_parquet,
            "user/integration-ds",
            token="test-token",
            split="train",
            commit_message="Integration test upload",
        )

        assert url == "https://huggingface.co/datasets/user/integration-ds"
        mock_api.create_repo.assert_called_once()
        mock_push_to_hub.assert_called_once()


    @patch("nlp_policy_nz.integrations.hf_uploader.HfApi")
    def test_full_deploy_flow(
        self,
        mock_api_cls: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Verify the complete deploy pipeline works end-to-end."""
        spaces_dir = tmp_path / "spaces"
        spaces_dir.mkdir()
        (spaces_dir / "app.py").write_text("import gradio as gr")
        (spaces_dir / "requirements.txt").write_text("gradio>=4.0.0")
        (spaces_dir / "README.md").write_text("---\nemoji: 🔍\n---", encoding="utf-8")


        mock_api = MagicMock()
        mock_api_cls.return_value = mock_api

        url = deploy_space(
            "user/integration-space",
            spaces_dir=str(spaces_dir),
            token="test-token",
            commit_message="Integration test deploy",
        )

        assert url == "https://huggingface.co/spaces/user/integration-space"
        mock_api.create_repo.assert_called_once()
        mock_api.upload_folder.assert_called_once()
