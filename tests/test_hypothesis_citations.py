"""Property-based tests for citation ID helpers."""

from __future__ import annotations

from hypothesis import given, strategies as st

from nlp_policy_nz.syntactic import generate_hansard_id, generate_legislation_id


@given(
    year=st.integers(min_value=1840, max_value=2100),
    number=st.integers(min_value=1, max_value=999),
    section=st.integers(min_value=0, max_value=500),
)
def test_legislation_ids_keep_expected_prefix_and_padding(
    year: int,
    number: int,
    section: int,
) -> None:
    """Generated legislation IDs remain stable over valid numeric ranges."""
    doc_id = generate_legislation_id(year, number, section)

    assert doc_id == f"NZ-ACT-{year}-{number:03d}-SEC-{section}"


@given(
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28),
    speech_num=st.integers(min_value=1, max_value=99),
)
def test_hansard_ids_keep_expected_prefix_and_padding(
    month: int,
    day: int,
    speech_num: int,
) -> None:
    """Generated Hansard IDs remain stable over valid date-like inputs."""
    date = f"2024-{month:02d}-{day:02d}"
    doc_id = generate_hansard_id(date, speech_num)

    assert doc_id == f"NZ-HANS-{date}-SP-{speech_num:02d}"
