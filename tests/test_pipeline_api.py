"""Tests for the pipeline_api module."""

from __future__ import annotations

from pathlib import Path

import pytest

from nlp_policy_nz.pipeline_api import (
    _collect_input_files,
    _model_version_from_loaded,
    _resolve_path,
    _valid_context_date,
)
from nlp_policy_nz.semantic.model_loader import DEFAULT_MODEL


def test_resolve_path() -> None:
    """Test resolving a string and a Path."""
    assert _resolve_path(".").is_absolute()
    assert _resolve_path(Path()).is_absolute()

    resolved_str = _resolve_path("test_dir")
    resolved_path = _resolve_path(Path("test_dir"))
    assert resolved_str == resolved_path


def test_collect_input_files_single_file(tmp_path: Path) -> None:
    """Test collecting a single input file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    files = _collect_input_files(test_file)
    assert len(files) == 1
    assert files[0] == test_file.resolve()


def test_collect_input_files_directory(tmp_path: Path) -> None:
    """Test collecting input files from a directory."""
    (tmp_path / "test1.txt").write_text("content")
    (tmp_path / "test2.xml").write_text("content")
    (tmp_path / "test3.json").write_text("content")
    (tmp_path / "ignored.pdf").write_text("content")

    files = _collect_input_files(tmp_path)
    assert len(files) == 3
    file_names = {f.name for f in files}
    assert file_names == {"test1.txt", "test2.xml", "test3.json"}


def test_collect_input_files_empty_directory(tmp_path: Path) -> None:
    """Test collecting input files from an empty directory raises an error."""
    with pytest.raises(FileNotFoundError, match="No supported input files found in directory"):
        _collect_input_files(tmp_path)


def test_collect_input_files_missing_path() -> None:
    """Test collecting input files from a missing path raises an error."""
    with pytest.raises(FileNotFoundError, match="Input path does not exist"):
        _collect_input_files(Path("nonexistent_path_xyz123"))


class DummyModel:
    def __init__(self, name_or_path: str | None = None) -> None:
        if name_or_path:
            self.config = type("Config", (), {"_name_or_path": name_or_path})()


class DummyTokenizer:
    def __init__(
        self, name_or_path: str | None = None, init_kwargs_name: str | None = None
    ) -> None:
        if name_or_path:
            self.name_or_path = name_or_path
        if init_kwargs_name:
            self.init_kwargs = {"name_or_path": init_kwargs_name}


def test_model_version_from_loaded() -> None:
    """Test extracting model version from loaded models and tokenizers."""
    # Test fallback to DEFAULT_MODEL
    assert _model_version_from_loaded(DummyModel(), DummyTokenizer()) == DEFAULT_MODEL

    # Test model config _name_or_path precedence
    model = DummyModel("model_config_path")
    tokenizer = DummyTokenizer(name_or_path="tokenizer_path", init_kwargs_name="init_kwargs_path")
    assert _model_version_from_loaded(model, tokenizer) == "model_config_path"

    # Test tokenizer init_kwargs precedence over tokenizer.name_or_path
    model_no_config = DummyModel()
    assert _model_version_from_loaded(model_no_config, tokenizer) == "init_kwargs_path"

    # Test tokenizer.name_or_path
    tokenizer_no_kwargs = DummyTokenizer(name_or_path="tokenizer_path")
    assert _model_version_from_loaded(model_no_config, tokenizer_no_kwargs) == "tokenizer_path"


def test_valid_context_date() -> None:
    """Test validation of context dates."""
    assert _valid_context_date("2024-01-01") == "2024-01-01"
    assert _valid_context_date("unknown-date") is None
    assert _valid_context_date("") is None


def test_pipeline_api_import() -> None:
    """Basic test to ensure the module imports correctly."""
    import nlp_policy_nz.pipeline_api as pa

    assert hasattr(pa, "process_legislation")
    assert hasattr(pa, "process_hansard")
