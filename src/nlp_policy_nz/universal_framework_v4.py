"""Universal framework v4 with Akoma Ntoso v3 output support."""

from __future__ import annotations

from dataclasses import dataclass
from xml.etree import ElementTree as ET

from nlp_policy_nz.schema.akn_v3 import (
    OASIS_AKN_V3_XSD_URL,
    AKNDocument,
    AKNValidator,
    FRBRMetadata,
    emit_amendment,
    emit_bill,
    emit_debate,
    emit_judgment,
)


@dataclass(frozen=True)
class FrameworkConfig:
    """Configuration for v4 source-to-AKN conversion."""

    country: str
    jurisdiction: str
    source_data_format: str
    target_schema_standard: str
    document_type: str = "bill"
    date: str = "1970-01-01"
    author: str = "nlp-policy-nz"
    language: str = "eng"
    version: str = "1"
    akn_schema_source: str | None = None


def _extract_xml_payload(raw_data: str) -> tuple[str, str, list[str]]:
    """Extract identifier, title, and text paragraphs from a source XML chunk."""
    try:
        root = ET.fromstring(raw_data)  # noqa: S314 - local framework input, no entity expansion.
    except ET.ParseError:
        text = raw_data.strip()
        return "raw-001", "Imported document", [text] if text else ["No source text supplied."]

    identifier = root.attrib.get("id") or root.attrib.get("eId") or "xml-001"
    title = root.attrib.get("title") or root.attrib.get("name") or root.tag.rsplit("}", 1)[-1].title()
    paragraphs = [
        text.strip()
        for text in ("".join(node.itertext()) for node in root.iter())
        if text.strip()
    ]
    if not paragraphs:
        paragraphs = ["No source text supplied."]
    return identifier, title, paragraphs


def run_framework(config: FrameworkConfig, raw_data: str) -> AKNDocument:
    """Convert source data to a validated AKN v3 document."""
    if config.target_schema_standard.lower().replace(" ", "") not in {
        "akoma-ntoso",
        "akomantoso",
        "akn",
    }:
        msg = f"Unsupported target schema standard: {config.target_schema_standard}"
        raise ValueError(msg)

    identifier, title, body = _extract_xml_payload(raw_data)
    metadata = FRBRMetadata(
        country=config.country,
        document_type=config.document_type,
        identifier=identifier,
        date=config.date,
        author=config.author,
        language=config.language,
        version=config.version,
    )
    emitters = {
        "amendment": emit_amendment,
        "bill": emit_bill,
        "debate": emit_debate,
        "judgment": emit_judgment,
    }
    try:
        emitter = emitters[config.document_type]
    except KeyError as exc:
        msg = f"Unsupported AKN document type: {config.document_type}"
        raise ValueError(msg) from exc

    xml = emitter(metadata, title, body)
    AKNValidator(config.akn_schema_source or OASIS_AKN_V3_XSD_URL).validate_or_raise(xml)
    return AKNDocument(xml=xml, document_type=config.document_type, metadata=metadata)
