"""Tests for the Storage Layer (Track 6).

The storage layer manages persistence of pipeline outputs — vector
embeddings, structured annotations, and metadata — into a database
back-end such as LanceDB.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from nlp_policy_nz.storage.serialization import (
    SCHEMA_FIELDS,
    PipelineRecord,
    deserialize_to_dataframe,
    load_from_parquet,
    records_to_dataframe,
    serialize_to_parquet,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_records() -> list[PipelineRecord]:
    """Return a small list of representative pipeline records for testing."""
    return [
        PipelineRecord(
            doc_id="leg-001",
            corpus_source="legislation",
            raw_text="This is the text of the first Act.",
            cleaned_tokens=["This", "is", "the", "text", "of", "the", "first", "Act"],
            nz_act_citations=["Act 2023 No 1"],
            te_reo_terms=["Aotearoa"],
            embeddings=[0.1, 0.2, 0.3],
        ),
        PipelineRecord(
            doc_id="han-001",
            corpus_source="hansard",
            raw_text="Speech from the member for Auckland.",
            cleaned_tokens=["Speech", "from", "the", "member", "for", "Auckland"],
            nz_act_citations=[],
            te_reo_terms=["Whanganui", "Aotearoa"],
            embeddings=None,
        ),
        PipelineRecord(
            doc_id="leg-002",
            corpus_source="legislation",
            raw_text="Amendment to the principal Act.",
            cleaned_tokens=["Amendment", "to", "the", "principal", "Act"],
            nz_act_citations=["Act 2023 No 1", "Act 2020 No 15"],
            te_reo_terms=[],
            embeddings=[0.4, 0.5, 0.6],
        ),
    ]


# ---------------------------------------------------------------------------
# Struct tests
# ---------------------------------------------------------------------------


class TestPipelineRecord:
    """Tests for the PipelineRecord msgspec struct."""

    def test_struct_creation(self) -> None:
        """Verify a PipelineRecord can be constructed with all fields."""
        rec = PipelineRecord(
            doc_id="test-1",
            corpus_source="hansard",
            raw_text="Some text.",
            cleaned_tokens=["Some", "text"],
            nz_act_citations=["Act 2021 No 5"],
            te_reo_terms=["kōrero"],
            embeddings=[0.9, 0.8],
        )
        assert rec.doc_id == "test-1"
        assert rec.corpus_source == "hansard"
        assert rec.raw_text == "Some text."
        assert rec.cleaned_tokens == ["Some", "text"]
        assert rec.nz_act_citations == ["Act 2021 No 5"]
        assert rec.te_reo_terms == ["kōrero"]
        assert rec.embeddings == [0.9, 0.8]

    def test_embeddings_default_none(self) -> None:
        """Verify embeddings field defaults to None when omitted."""
        rec = PipelineRecord(
            doc_id="no-embed",
            corpus_source="legislation",
            raw_text="No embeddings.",
            cleaned_tokens=["No", "embeddings"],
            nz_act_citations=[],
            te_reo_terms=[],
        )
        assert rec.embeddings is None

    def test_struct_field_names(self) -> None:
        """Verify the struct field names match SCHEMA_FIELDS exactly."""
        field_names = list(PipelineRecord.__struct_fields__)  # type: ignore[attr-defined]
        assert field_names == SCHEMA_FIELDS


# ---------------------------------------------------------------------------
# DataFrame conversion tests
# ---------------------------------------------------------------------------


class TestRecordsToDataFrame:
    """Tests for :func:`records_to_dataframe`."""

    def test_valid_conversion(self, sample_records: list[PipelineRecord]) -> None:
        """Verify a valid Narwhals DataFrame is returned from records."""
        df = records_to_dataframe(sample_records)
        assert set(df.columns) == set(SCHEMA_FIELDS)
        assert df.shape[0] == len(sample_records)

    def test_empty_records_raises(self) -> None:
        """Verify empty input raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            records_to_dataframe([])

    def test_columns_ordered(self, sample_records: list[PipelineRecord]) -> None:
        """Verify column ordering matches SCHEMA_FIELDS."""
        df = records_to_dataframe(sample_records)
        assert list(df.columns) == SCHEMA_FIELDS


# ---------------------------------------------------------------------------
# Parquet round-trip tests
# ---------------------------------------------------------------------------


class TestParquetRoundTrip:
    """Tests for Parquet serialization and deserialization."""

    def test_serialize_and_load(
        self,
        sample_records: list[PipelineRecord],
        tmp_path: Path,
    ) -> None:
        """Write records to Parquet and verify they can be read back."""
        parquet_path = tmp_path / "test_records.parquet"
        result = serialize_to_parquet(sample_records, parquet_path)
        assert result == parquet_path.resolve()
        assert parquet_path.is_file()

        loaded = load_from_parquet(parquet_path)
        assert len(loaded) == len(sample_records)

        for original, loaded_rec in zip(sample_records, loaded, strict=False):
            assert loaded_rec.doc_id == original.doc_id
            assert loaded_rec.corpus_source == original.corpus_source
            assert loaded_rec.raw_text == original.raw_text
            assert loaded_rec.cleaned_tokens == original.cleaned_tokens
            assert loaded_rec.nz_act_citations == original.nz_act_citations
            assert loaded_rec.te_reo_terms == original.te_reo_terms
            assert loaded_rec.embeddings == original.embeddings

    def test_roundtrip_preserves_none_embeddings(
        self,
        sample_records: list[PipelineRecord],
        tmp_path: Path,
    ) -> None:
        """Verify records with None embeddings survive the round-trip."""
        parquet_path = tmp_path / "none_embed.parquet"
        serialize_to_parquet(sample_records, parquet_path)
        loaded = load_from_parquet(parquet_path)
        han = next(r for r in loaded if r.doc_id == "han-001")
        assert han.embeddings is None

    def test_deserialize_to_dataframe(
        self,
        sample_records: list[PipelineRecord],
        tmp_path: Path,
    ) -> None:
        """Verify deserialize_to_dataframe returns a Narwhals DataFrame."""
        parquet_path = tmp_path / "df_test.parquet"
        serialize_to_parquet(sample_records, parquet_path)
        df = deserialize_to_dataframe(parquet_path)
        assert set(df.columns) == set(SCHEMA_FIELDS)
        assert df.shape[0] == len(sample_records)

    def test_file_not_found(self) -> None:
        """Verify FileNotFoundError is raised for missing files."""
        missing = Path("/nonexistent/path/data.parquet")
        with pytest.raises(FileNotFoundError, match="not found"):
            load_from_parquet(missing)
        with pytest.raises(FileNotFoundError, match="not found"):
            deserialize_to_dataframe(missing)

    def test_empty_records_raises_on_serialize(self, tmp_path: Path) -> None:
        """Verify serializing empty records raises ValueError."""
        parquet_path = tmp_path / "empty.parquet"
        with pytest.raises(ValueError, match="empty"):
            serialize_to_parquet([], parquet_path)

    def test_string_path(
        self,
        sample_records: list[PipelineRecord],
        tmp_path: Path,
    ) -> None:
        """Verify str paths are accepted as well as Path objects."""
        parquet_path = str(tmp_path / "str_path.parquet")
        result = serialize_to_parquet(sample_records, parquet_path)
        assert isinstance(result, Path)
        loaded = load_from_parquet(parquet_path)
        assert len(loaded) == len(sample_records)
