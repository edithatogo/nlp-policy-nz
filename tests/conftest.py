"""Pytest configuration, Hypothesis settings, and shared fixtures for the
nlp-policy-nz test suite.

This module configures:
- Hypothesis properties (max examples, deadline)
- Shared test fixtures for NZ legislative and Hansard text samples
"""

import pytest
from hypothesis import HealthCheck, settings

# ---------------------------------------------------------------------------
# Hypothesis global settings
# ---------------------------------------------------------------------------
settings.register_profile(
    "ci",
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile("ci")


# ---------------------------------------------------------------------------
# Fixtures – sample NZ legislative text  # noqa: RUF003
# ---------------------------------------------------------------------------
@pytest.fixture
def sample_legislation_text() -> str:
    """Return a short snippet of NZ legislation containing typical markup
    (sections, subsections, defined terms, and references to other
    enactments)."""
    return (
        "(1) This Act is the Legislation (Repeals and Amendments) Act 2024.\n"
        "(2) In this Act, unless the context otherwise requires,—\n"
        "    (a) **commencement** means the date on which this Act receives "
        "the Royal assent; and\n"
        "    (b) **enactment** means an enactment (within the meaning of "
        "section 29 of the Legislation Act 2019) that is repealed or amended "
        "by Schedule 1.\n"
        "(3) Section 5 of the Māori Language Act 2016 provides that **Te Reo "
        "Māori** is an official language of New Zealand."
    )


@pytest.fixture
def sample_hansard_text() -> str:
    """Return a short excerpt of NZ Hansard (parliamentary debate) containing
    spoken language, macronised Te Reo, and procedural references."""
    return (
        "Hon Member: Kia ora koutou katoa. E te Mana Whakawā, tēnā koe.\n"
        "I rise today to speak on the third reading of the Taxation (Annual "
        "Rates for 2024–2025) Bill.\n"  # noqa: RUF001
        "The Minister of Finance has outlined the Government's commitment to "
        "fiscal responsibility while investing in health, education, and "
        "infrastructure.\n"
        "Speaker: The question is that the amendment be agreed to."
    )
