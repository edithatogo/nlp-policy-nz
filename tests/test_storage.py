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


@pytest.fixture
def sample_committee_records() -> list[PipelineRecord]:
    """Return pipeline records with additive committee/submission fields."""
    return [
        PipelineRecord(
            doc_id="sc-001",
            corpus_source="select_committee",
            raw_text="Report of the Finance and Expenditure Committee on the Taxation Bill 2024.",
            cleaned_tokens=["Report", "of", "the", "Finance", "Committee"],
            nz_act_citations=[],
            te_reo_terms=[],
            embeddings=None,
            committee="Finance and Expenditure Committee",
            bill_reference="Taxation Bill 2024",
            report_title="Finance and Expenditure Report",
            findings=["Revenue impact positive"],
            recommendations=["Proceed with amendments"],
        ),
        PipelineRecord(
            doc_id="sub-001",
            corpus_source="parliament_submission",
            raw_text="Submission from Greenpeace on the Climate Bill 2025.",
            cleaned_tokens=["Submission", "from", "Greenpeace"],
            nz_act_citations=[],
            te_reo_terms=[],
            embeddings=None,
            submitter_name="Greenpeace NZ",
            committee="Environment Select Committee",
            bill_reference="Climate Bill 2025",
            linkage_confidence=0.95,
        ),
        PipelineRecord(
            doc_id="rr-001",
            corpus_source="regulations_review",
            raw_text="Regulations Review Committee proceeding on challenge to Regulation 2024 No 10.",
            cleaned_tokens=["Regulations", "Review", "Committee", "proceeding"],
            nz_act_citations=[],
            te_reo_terms=[],
            embeddings=None,
            committee="Regulations Review Committee",
            challenged_regulation="Regulation 2024 No 10",
            grounds="Ultra vires the empowering Act",
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

    def test_roundtrip_preserves_empty_entity_context_as_none(
        self,
        tmp_path: Path,
    ) -> None:
        """Empty resolver context dicts should serialize as null."""
        record = PipelineRecord(
            doc_id="ctx-001",
            corpus_source="hansard",
            raw_text="Jacinda Ardern spoke.",
            cleaned_tokens=["Jacinda", "Ardern", "spoke"],
            nz_act_citations=[],
            te_reo_terms=[],
            resolved_entities=[
                {
                    "entity_id": "mp:jacinda-ardern",
                    "name": "Jacinda Ardern",
                    "entity_type": "mp",
                    "qid": "Q139616",
                    "start": 0,
                    "end": 14,
                    "text": "Jacinda Ardern",
                    "confidence": 0.99,
                    "context": {},
                }
            ],
        )
        parquet_path = tmp_path / "context_none.parquet"

        serialize_to_parquet([record], parquet_path)
        loaded = load_from_parquet(parquet_path)

        assert loaded[0].resolved_entities[0]["context"] is None

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


# ---------------------------------------------------------------------------
# Additive committee / submission fields round-trip tests
# ---------------------------------------------------------------------------


class TestCommitteeRecordsRoundTrip:
    """Tests for serialization/deserialization of additive committee fields."""

    def test_committee_record_struct_defaults(self) -> None:
        """Verify additive fields default to None when omitted."""
        rec = PipelineRecord(
            doc_id="sc-002",
            corpus_source="select_committee",
            raw_text="Some report text.",
            cleaned_tokens=["Some", "report", "text"],
            nz_act_citations=[],
            te_reo_terms=[],
        )
        assert rec.submitter_name is None
        assert rec.committee is None
        assert rec.bill_reference is None
        assert rec.linkage_confidence is None
        assert rec.challenged_regulation is None
        assert rec.grounds is None
        assert rec.report_title is None
        assert rec.findings is None
        assert rec.recommendations is None

    def test_committee_record_construction(self) -> None:
        """Verify a PipelineRecord with all committee fields can be built."""
        rec = PipelineRecord(
            doc_id="sc-full",
            corpus_source="select_committee",
            raw_text="Full report text here.",
            cleaned_tokens=["Full", "report"],
            nz_act_citations=["Act 2024 No 5"],
            te_reo_terms=[],
            embeddings=[0.1, 0.2],
            submitter_name="NZ Law Society",
            committee="Justice Select Committee",
            bill_reference="Criminal Procedure Bill 2024",
            linkage_confidence=0.9,
            challenged_regulation=None,
            grounds=None,
            report_title="Criminal Procedure Review",
            findings=["Current process is slow", "Needs digital reform"],
            recommendations=["Adopt e-filing", "Streamline appeals"],
        )
        assert rec.submitter_name == "NZ Law Society"
        assert rec.committee == "Justice Select Committee"
        assert rec.bill_reference == "Criminal Procedure Bill 2024"
        assert rec.linkage_confidence == 0.9
        assert rec.report_title == "Criminal Procedure Review"
        assert rec.findings == ["Current process is slow", "Needs digital reform"]
        assert rec.recommendations == ["Adopt e-filing", "Streamline appeals"]

    def test_committee_records_to_dataframe(
        self,
        sample_committee_records: list[PipelineRecord],
    ) -> None:
        """Verify DataFrame conversion includes all additive fields."""
        df = records_to_dataframe(sample_committee_records)
        assert set(df.columns) == set(SCHEMA_FIELDS)
        assert df.shape[0] == len(sample_committee_records)

        # Check additive columns are present and non-null for appropriate rows
        col = df["submitter_name"]
        assert col is not None
        col = df["committee"]
        assert col is not None
        col = df["bill_reference"]
        assert col is not None

    def test_committee_parquet_roundtrip(
        self,
        sample_committee_records: list[PipelineRecord],
        tmp_path: Path,
    ) -> None:
        """Verify committee records survive Parquet round-trip."""
        parquet_path = tmp_path / "committee_test.parquet"
        serialize_to_parquet(sample_committee_records, parquet_path)
        assert parquet_path.is_file()

        loaded = load_from_parquet(parquet_path)
        assert len(loaded) == len(sample_committee_records)

        for orig, loaded_rec in zip(sample_committee_records, loaded, strict=False):
            assert loaded_rec.doc_id == orig.doc_id
            assert loaded_rec.corpus_source == orig.corpus_source
            assert loaded_rec.submitter_name == orig.submitter_name
            assert loaded_rec.committee == orig.committee
            assert loaded_rec.bill_reference == orig.bill_reference
            assert loaded_rec.linkage_confidence == orig.linkage_confidence
            assert loaded_rec.challenged_regulation == orig.challenged_regulation
            assert loaded_rec.grounds == orig.grounds
            assert loaded_rec.report_title == orig.report_title
            assert loaded_rec.findings == orig.findings
            assert loaded_rec.recommendations == orig.recommendations
