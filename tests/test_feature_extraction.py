"""Tests for the feature extraction module (Track 10 — committee/submission features)."""

from __future__ import annotations

from nlp_policy_nz.feature_extraction import (
    extract_bill_reference,
    extract_committee_name,
    extract_regulations_review_metadata,
    extract_select_committee_metadata,
    extract_submission_metadata,
)


class TestExtractBillReference:
    """Tests for :func:`extract_bill_reference`."""

    def test_standard_bill(self) -> None:
        result = extract_bill_reference("The Taxation Bill 2024 No 15 is under review.")
        assert result == "Bill 2024 No 15"

    def test_standard_act(self) -> None:
        result = extract_bill_reference("Refer to the Act 2023 No 1 for details.")
        assert result == "Act 2023 No 1"

    def test_regulation(self) -> None:
        result = extract_bill_reference("Challenge to Regulation 2024 No 10.")
        assert result == "Regulation 2024 No 10"

    def test_no_match(self) -> None:
        result = extract_bill_reference("Just some random text without references.")
        assert result is None

    def test_empty_string(self) -> None:
        result = extract_bill_reference("")
        assert result is None

    def test_none_input(self) -> None:
        result = extract_bill_reference(None)  # type: ignore[arg-type]
        assert result is None

    def test_multiple_matches_returns_first(self) -> None:
        result = extract_bill_reference(
            "Act 2023 No 1 and Act 2024 No 5 are both relevant."
        )
        assert result == "Act 2023 No 1"


class TestExtractCommitteeName:
    """Tests for :func:`extract_committee_name`."""

    def test_select_committee(self) -> None:
        result = extract_committee_name(
            "This report is from the Finance Select Committee."
        )
        assert result == "Select Committee"

    def test_regulations_review_committee(self) -> None:
        result = extract_committee_name(
            "The Regulations Review Committee considered the complaint."
        )
        assert result == "Regulations Review Committee"

    def test_generic_committee(self) -> None:
        result = extract_committee_name("The Committee met on Monday.")
        assert result == "Committee"

    def test_no_match(self) -> None:
        result = extract_committee_name("No committee mentioned here.")
        assert result is None

    def test_empty_string(self) -> None:
        result = extract_committee_name("")
        assert result is None

    def test_none_input(self) -> None:
        result = extract_committee_name(None)  # type: ignore[arg-type]
        assert result is None


class TestExtractSubmissionMetadata:
    """Tests for :func:`extract_submission_metadata`."""

    def test_full_metadata(self) -> None:
        metadata = extract_submission_metadata(
            submitter_name="Greenpeace NZ",
            committee="Environment Select Committee",
            bill_reference="Climate Bill 2025",
        )
        assert metadata["submitter_name"] == "Greenpeace NZ"
        assert metadata["committee"] == "Environment Select Committee"
        assert metadata["bill_reference"] == "Climate Bill 2025"
        assert metadata["linkage_confidence"] == 0.8

    def test_fallback_extraction(self) -> None:
        metadata = extract_submission_metadata(
            submitter_name="NZ Law Society",
            text_content="Submission regarding the Courts Bill 2024 No 10.",
        )
        assert metadata["submitter_name"] == "NZ Law Society"
        assert metadata["bill_reference"] == "Bill 2024 No 10"

    def test_minimal_metadata(self) -> None:
        metadata = extract_submission_metadata(submitter_name="Anonymous")
        assert metadata["submitter_name"] == "Anonymous"
        assert metadata["committee"] is None
        assert metadata["bill_reference"] is None
        assert metadata["linkage_confidence"] is None


class TestExtractRegulationsReviewMetadata:
    """Tests for :func:`extract_regulations_review_metadata`."""

    def test_full_metadata(self) -> None:
        metadata = extract_regulations_review_metadata(
            challenged_regulation="Regulation 2024 No 10",
            grounds="Ultra vires the empowering Act",
            committee="Regulations Review Committee",
        )
        assert metadata["committee"] == "Regulations Review Committee"
        assert metadata["challenged_regulation"] == "Regulation 2024 No 10"
        assert metadata["grounds"] == "Ultra vires the empowering Act"

    def test_fallback_extraction(self) -> None:
        metadata = extract_regulations_review_metadata(
            text_content="The Regulations Review Committee met to consider Regulation 2023 No 5."
        )
        assert metadata["committee"] == "Regulations Review Committee"

    def test_minimal_metadata(self) -> None:
        metadata = extract_regulations_review_metadata()
        assert metadata["committee"] is None
        assert metadata["challenged_regulation"] is None
        assert metadata["grounds"] is None


class TestExtractSelectCommitteeMetadata:
    """Tests for :func:`extract_select_committee_metadata`."""

    def test_full_metadata(self) -> None:
        metadata = extract_select_committee_metadata(
            report_title="Finance Report on the Taxation Bill 2024",
            committee="Finance and Expenditure Committee",
            findings=["Revenue impact positive"],
            recommendations=["Proceed with amendments"],
        )
        assert metadata["committee"] == "Finance and Expenditure Committee"
        assert metadata["report_title"] == "Finance Report on the Taxation Bill 2024"
        assert metadata["findings"] == ["Revenue impact positive"]
        assert metadata["recommendations"] == ["Proceed with amendments"]

    def test_fallback_extraction(self) -> None:
        metadata = extract_select_committee_metadata(
            report_title="Report of the Select Committee on the Health Bill 2025"
        )
        assert metadata["committee"] == "Select Committee"

    def test_minimal_metadata(self) -> None:
        metadata = extract_select_committee_metadata()
        assert metadata["committee"] is None
        assert metadata["report_title"] is None
        assert metadata["findings"] == []
        assert metadata["recommendations"] == []
