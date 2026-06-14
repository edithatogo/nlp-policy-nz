"""Feature extraction utilities for committee, submissions, and regulations review pipelines.

Provides functions to extract structured metadata from select committee reports,
parliament submissions, and regulations review proceedings, mapping them into
the additive fields on :class:`~nlp_policy_nz.storage.serialization.PipelineRecord`.
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Pattern helpers
# ---------------------------------------------------------------------------

_BILL_REF_PATTERN = re.compile(
    r"(?P<type>Bill|Act|Regulation)\s+(?P<year>\d{4})\s+(?:No\.?\s*)?(?P<number>\d+)",
    re.IGNORECASE,
)

_COMMITTEE_NAME_PATTERN = re.compile(
    r"(Select Committee|Committee|Regulations Review Committee)",
)


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------


def extract_bill_reference(text: str) -> str | None:
    """Extract the first bill/act reference from *text*.

    Parameters
    ----------
    text : str
        Free-form text to scan (e.g. a submission body or report title).

    Returns
    -------
    str or None
        The matched bill reference string, or *None* if no match is found.

    """
    if not text:
        return None
    match = _BILL_REF_PATTERN.search(text)
    return match.group(0) if match else None


def extract_committee_name(text: str) -> str | None:
    """Extract the first committee name mention from *text*.

    Parameters
    ----------
    text : str
        Free-form text to scan.

    Returns
    -------
    str or None
        The matched committee name, or *None*.

    """
    if not text:
        return None
    match = _COMMITTEE_NAME_PATTERN.search(text)
    return match.group(0) if match else None


def extract_submission_metadata(
    *,
    submitter_name: str | None = None,
    committee: str | None = None,
    bill_reference: str | None = None,
    text_content: str | None = None,
) -> dict[str, Any]:
    """Build a metadata dict for a parliament submission record.

    Parameters
    ----------
    submitter_name : str or None
        Name of the submission author.
    committee : str or None
        Name of the committee (falls back to extraction from *text_content*).
    bill_reference : str or None
        Bill reference (falls back to extraction from *text_content*).
    text_content : str or None
        Full text content used for fallback extraction.

    Returns
    -------
    dict[str, Any]
        A dictionary with keys ``submitter_name``, ``committee``,
        ``bill_reference``, and ``linkage_confidence``.

    """
    resolved_committee = committee or (
        extract_committee_name(text_content) if text_content else None
    )
    resolved_bill = bill_reference or (
        extract_bill_reference(text_content) if text_content else None
    )

    return {
        "submitter_name": submitter_name,
        "committee": resolved_committee,
        "bill_reference": resolved_bill,
        "linkage_confidence": 0.8 if resolved_bill else None,
    }


def extract_regulations_review_metadata(
    *,
    challenged_regulation: str | None = None,
    grounds: str | None = None,
    committee: str | None = None,
    text_content: str | None = None,
) -> dict[str, Any]:
    """Build a metadata dict for a regulations review proceeding record.

    Parameters
    ----------
    challenged_regulation : str or None
        The regulation being challenged.
    grounds : str or None
        Grounds for the challenge.
    committee : str or None
        Committee name (falls back to extraction from *text_content*).
    text_content : str or None
        Full text content used for fallback extraction.

    Returns
    -------
    dict[str, Any]
        A dictionary with keys ``committee``, ``challenged_regulation``,
        and ``grounds``.

    """
    resolved_committee = committee or (
        extract_committee_name(text_content) if text_content else None
    )

    return {
        "committee": resolved_committee,
        "challenged_regulation": challenged_regulation,
        "grounds": grounds,
    }


def extract_select_committee_metadata(
    *,
    report_title: str | None = None,
    committee: str | None = None,
    bill_reference: str | None = None,
    findings: list[str] | None = None,
    recommendations: list[str] | None = None,
    text_content: str | None = None,
) -> dict[str, Any]:
    """Build a metadata dict for a select committee report record.

    Parameters
    ----------
    report_title : str or None
        Title of the report.
    committee : str or None
        Committee name (falls back to extraction from *report_title*).
    bill_reference : str or None
        Bill reference (falls back to extraction from *report_title*
        or *text_content*).
    findings : list[str] or None
        Extracted findings.
    recommendations : list[str] or None
        Extracted recommendations.
    text_content : str or None
        Full text content used for fallback extraction.

    Returns
    -------
    dict[str, Any]
        A dictionary with keys ``committee``, ``report_title``,
        ``bill_reference``, ``findings``, and ``recommendations``.

    """
    search_text = report_title or text_content or ""
    resolved_committee = committee or extract_committee_name(search_text)
    resolved_bill = bill_reference or extract_bill_reference(search_text)

    return {
        "committee": resolved_committee,
        "report_title": report_title,
        "bill_reference": resolved_bill,
        "findings": findings or [],
        "recommendations": recommendations or [],
    }
