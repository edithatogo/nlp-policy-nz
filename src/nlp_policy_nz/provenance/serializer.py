"""PROV-O JSON-LD serialization."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nlp_policy_nz.provenance.recorder import ProvenanceRecord


PROV_CONTEXT: dict[str, str] = {
    "prov": "http://www.w3.org/ns/prov#",
    "schema": "https://schema.org/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}


def serialize_prov_o_jsonld(record: ProvenanceRecord) -> dict[str, Any]:
    """Serialize a provenance record as PROV-O-compatible JSON-LD."""
    activity_id = f"{record.run_id}:activity"
    agent_id = f"urn:nlp-policy-nz:agent:{record.agent_name}"
    output_id = f"urn:nlp-policy-nz:entity:{record.output_path}"

    graph: list[dict[str, Any]] = [
        {
            "@id": agent_id,
            "@type": "prov:Agent",
            "prov:type": "prov:SoftwareAgent",
            "schema:name": record.agent_name,
            "schema:softwareVersion": record.pipeline_version,
            "schema:identifier": record.commit_sha,
        },
        {
            "@id": activity_id,
            "@type": "prov:Activity",
            "prov:startedAtTime": record.started_at,
            "prov:endedAtTime": record.ended_at,
            "prov:wasAssociatedWith": {"@id": agent_id},
            "schema:name": record.pipeline_name,
            "schema:softwareVersion": record.pipeline_version,
            "schema:identifier": record.commit_sha,
            "schema:instrument": record.model_versions,
            "schema:object": record.parameters,
        },
        {
            "@id": output_id,
            "@type": "prov:Entity",
            "prov:wasGeneratedBy": {"@id": activity_id},
            "schema:contentUrl": record.output_path,
            "schema:encodingFormat": "application/vnd.apache.parquet",
            "schema:numberOfItems": record.record_count,
        },
    ]

    for input_path in record.input_paths:
        graph.append(
            {
                "@id": f"urn:nlp-policy-nz:entity:{input_path}",
                "@type": "prov:Entity",
                "schema:contentUrl": input_path,
                "prov:wasUsedBy": {"@id": activity_id},
            }
        )

    if record.zenodo_doi:
        graph[2]["schema:sameAs"] = record.zenodo_doi

    return {
        "@context": PROV_CONTEXT,
        "@id": record.run_id,
        "@type": "prov:Bundle",
        "@graph": graph,
    }
