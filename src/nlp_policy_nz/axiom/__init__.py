"""Axiom Foundation interoperability helpers for NZ legal NLP."""

from __future__ import annotations

from nlp_policy_nz.axiom.linkage import (
    BILL_STATUSES,
    BillAction,
    BillHansardLink,
    BillStatus,
    BillVersion,
    normalise_bill_status,
)
from nlp_policy_nz.axiom.rulespec import (
    RuleSpecReference,
    make_rulespec_reference,
    pipeline_record_rulespec_reference,
    source_verification_metadata,
)
from nlp_policy_nz.axiom.source import (
    DOCUMENT_TYPES,
    DocumentType,
    SourceSection,
    SourceSectionMetadata,
    StalenessReport,
    compare_source_staleness,
    source_section_to_pipeline_record,
    source_sha256,
)

__all__ = [
    "BILL_STATUSES",
    "DOCUMENT_TYPES",
    "BillAction",
    "BillHansardLink",
    "BillStatus",
    "BillVersion",
    "DocumentType",
    "RuleSpecReference",
    "SourceSection",
    "SourceSectionMetadata",
    "StalenessReport",
    "compare_source_staleness",
    "make_rulespec_reference",
    "normalise_bill_status",
    "pipeline_record_rulespec_reference",
    "source_section_to_pipeline_record",
    "source_sha256",
    "source_verification_metadata",
]
