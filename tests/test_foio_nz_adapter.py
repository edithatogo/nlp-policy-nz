from __future__ import annotations

from pathlib import Path

import pytest

from nlp_policy_nz.extraction import (
    ExtractedSpan,
    ExtractionFamily,
    ExtractionRecord,
    FoioNewZealandProfileSnapshot,
    NewZealandJurisdiction,
    SourceTrace,
    build_new_zealand_archive_bundle,
    load_new_zealand_evaluation_fixture,
    route_new_zealand_jurisdiction,
)


def _snapshot() -> FoioNewZealandProfileSnapshot:
    return FoioNewZealandProfileSnapshot(
        profile_id="foio-nz-oia@0.9.0",
        archive_repository="edithatogo/fyi-archive",
        archive_revision="a" * 40,
        archive_content_sha256="b" * 64,
        source_pack_revision="sha256:source-pack-candidate",
        source_pack_sha256="c" * 64,
        legal_source_url="https://www.legislation.govt.nz/act/public/1982/0156/latest/versions.aspx",
        ontology_version="foi-o@1.0.0",
        schema_version="1.0",
        extraction_contract_version="1.0",
        pipeline_version="nlp-policy-nz@candidate",
        retrieved_at="2026-07-21T00:00:00Z",
    )


def _record(*, path: str = "nz/oia/request") -> ExtractionRecord:
    return ExtractionRecord(
        record_id="nz:1",
        family=ExtractionFamily.OBLIGATION,
        label="observed-obligation",
        value="observed text",
        source_trace=SourceTrace(
            citation_path=path,
            source_sha256="b" * 64,
            source_url="https://fyi.org.nz/list/all",
            retrieved_at="2026-07-21T00:00:00Z",
            spans=(ExtractedSpan(start=0, end=8, text="observed"),),
        ),
        attributes={"review": "candidate"},
    )


def test_router_routes_explicit_nz_and_abstains_on_ambiguous_sources() -> None:
    assert route_new_zealand_jurisdiction(_record()).jurisdiction is NewZealandJurisdiction.NZ
    assert route_new_zealand_jurisdiction(_record(path="commonwealth/nsw/foi"), explicit_jurisdiction="AU").status == "abstained"
    assert route_new_zealand_jurisdiction(_record(path="unknown/source"), explicit_jurisdiction=None).status == "routed"


def test_bundle_is_candidate_only_and_enforces_source_digest() -> None:
    bundle = build_new_zealand_archive_bundle([_record()], _snapshot())
    assert bundle.review_status == "candidate"
    assert bundle.manifest.records[0].attributes["foio_nz_provenance"]["profile_id"] == "foio-nz-oia@0.9.0"
    bad = _record().model_copy(update={"source_trace": _record().source_trace.model_copy(update={"source_sha256": "d" * 64})})
    with pytest.raises(ValueError, match="source digest"):
        build_new_zealand_archive_bundle([bad], _snapshot())


def test_fixture_contract_requires_all_evaluation_dimensions() -> None:
    fixture = load_new_zealand_evaluation_fixture(Path("data/foio/nz_evaluation_fixture.json"))
    assert fixture.fixture_status == "contract-only"
    assert set(fixture.fixture_families) == {"positive", "negative", "temporal", "non-equivalence"}
