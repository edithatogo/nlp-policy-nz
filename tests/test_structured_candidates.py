"""Tests for the offline Track 105 candidate adapter."""

from nlp_policy_nz.storage import PipelineRecord
from nlp_policy_nz.structured_candidates import build_candidate_record


def test_candidate_is_canonical_but_non_authoritative() -> None:
    record = build_candidate_record(
        doc_id="fixture-1",
        corpus_source="track105_fixture",
        raw_text="The bill must commence.",
        extracted={"cleaned_tokens": ["bill", "commence"], "stance": "neutral"},
    )

    assert isinstance(record, PipelineRecord)
    assert record.cleaned_tokens == ["bill", "commence"]
    assert record.argument_label_source == "candidate"
    assert record.stance_label_source == "candidate"
    assert record.schema_version == "1.1"


def test_candidate_rejects_scalar_lists() -> None:
    try:
        build_candidate_record(
            doc_id="fixture-1",
            corpus_source="track105_fixture",
            raw_text="text",
            extracted={"te_reo_terms": "not-a-list"},
        )
    except TypeError as error:
        assert "te_reo_terms" in str(error)
    else:
        raise AssertionError("scalar candidate fields must be rejected")
