"""Tests for Hugging Face Dataset Card Generator (Track 8, Task 1.3).

Tests the auto-generation of YAML frontmatter and markdown dataset cards.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nlp_policy_nz.integrations.dataset_card import (
    generate_dataset_card,
    write_dataset_card,
)

if TYPE_CHECKING:
    from pathlib import Path

# ---------------------------------------------------------------------------
# generate_dataset_card tests
# ---------------------------------------------------------------------------


class TestGenerateDatasetCard:
    """Tests for :func:`generate_dataset_card`."""

    def test_contains_yaml_frontmatter(self) -> None:
        """Verify output starts with YAML frontmatter."""
        card = generate_dataset_card("user/test-ds")
        assert card.startswith("---")
        assert "license: mit" in card

    def test_contains_title(self) -> None:
        """Verify the title appears as a markdown heading."""
        card = generate_dataset_card("user/test-ds", title="My Dataset")
        assert "# My Dataset" in card

    def test_contains_repo_id_in_usage(self) -> None:
        """Verify the repo_id is embedded in the usage example."""
        card = generate_dataset_card("user/my-ds")
        assert 'load_dataset("user/my-ds"' in card

    def test_total_chunks_formatted(self) -> None:
        """Verify total_chunks is comma-formatted in the output."""
        card = generate_dataset_card("user/ds", total_chunks=12345)
        assert "12,345" in card

    def test_total_chunks_na_when_none(self) -> None:
        """Verify N/A is shown when total_chunks is None."""
        card = generate_dataset_card("user/ds", total_chunks=None)
        assert "N/A" in card

    def test_embedding_dim_included(self) -> None:
        """Verify embedding dimension appears in the schema table."""
        card = generate_dataset_card("user/ds", embedding_dim=768)
        assert "768" in card

    def test_embedding_dim_na_when_none(self) -> None:
        """Verify N/A when embedding_dim is None."""
        card = generate_dataset_card("user/ds", embedding_dim=None)
        assert "N/A" in card

    def test_custom_tags(self) -> None:
        """Verify custom tags appear in YAML frontmatter."""
        card = generate_dataset_card("user/ds", tags=["foo", "bar"])
        assert "- foo" in card
        assert "- bar" in card

    def test_default_tags(self) -> None:
        """Verify default tags are included when none specified."""
        card = generate_dataset_card("user/ds")
        assert "- nlp" in card
        assert "- new-zealand" in card

    def test_schema_table_present(self) -> None:
        """Verify the schema table lists all pipeline columns."""
        card = generate_dataset_card("user/ds")
        for col in ["doc_id", "corpus_source", "raw_text", "embeddings"]:
            assert col in card

    def test_citation_bibtex(self) -> None:
        """Verify a BibTeX citation block is present."""
        card = generate_dataset_card("user/ds", year=2026)
        assert "@misc" in card
        assert "2026" in card

    def test_custom_year(self) -> None:
        """Verify a custom year is used in the citation."""
        card = generate_dataset_card("user/ds", year=2025)
        assert "2025" in card


# ---------------------------------------------------------------------------
# write_dataset_card tests
# ---------------------------------------------------------------------------


class TestWriteDatasetCard:
    """Tests for :func:`write_dataset_card`."""

    def test_writes_file(self, tmp_path: Path) -> None:
        """Verify a README.md file is created on disk."""
        out = write_dataset_card(
            tmp_path / "README.md",
            repo_id="user/ds",
            title="Test",
        )
        assert out.is_file()
        assert out.name == "README.md"

    def test_content_matches_generate(self, tmp_path: Path) -> None:
        """Verify written content matches generate_dataset_card output."""
        out = write_dataset_card(
            tmp_path / "README.md",
            repo_id="user/ds",
            title="Test",
        )
        expected = generate_dataset_card("user/ds", title="Test")
        assert out.read_text(encoding="utf-8") == expected

    def test_returns_resolved_path(self, tmp_path: Path) -> None:
        """Verify the returned path is absolute."""
        out = write_dataset_card(tmp_path / "README.md", repo_id="user/ds")
        assert out.is_absolute()
