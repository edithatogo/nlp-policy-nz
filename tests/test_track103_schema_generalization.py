"""Tests for Track 103 shared-schema generalization."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _schema():
    return json.loads((ROOT / "schemas/shared_nz_corpus_core.schema.json").read_text(encoding="utf-8"))


def _record(**updates):
    record = {
        "corpus_id": "corpus-au-commonwealth",
        "record_id": "record-1",
        "source_id": "source-1",
        "jurisdiction": "Australia",
        "country": "AU",
        "document_type": "other",
        "display_title": "Example record",
        "language": "en",
        "record_schema_version": "v1",
        "canonical_uri": "https://example.test/record-1",
        "source_url": "https://example.test/source-1",
        "source_version": "1",
        "effective_date": None,
        "published_date": None,
        "last_modified_date": None,
        "content_sha256": "a" * 64,
        "manifest_sha256": "b" * 64,
        "coverage_status": "candidate",
        "rights_note": "fixture only",
        "provenance": {"source": "fixture"},
    }
    record.update(updates)
    return record


def test_schema_accepts_non_nz_profile_shape():
    schema = _schema()
    record = _record()

    assert re.fullmatch(schema["properties"]["corpus_id"]["pattern"], record["corpus_id"])
    assert re.fullmatch(schema["properties"]["country"]["pattern"], record["country"])
    assert record["jurisdiction"]


def test_nz_default_profile_shape_remains_valid():
    record = _record(
        corpus_id="corpus-nz-legislation",
        jurisdiction="New Zealand",
        country="NZ",
    )

    schema = _schema()

    assert re.fullmatch(schema["properties"]["corpus_id"]["pattern"], record["corpus_id"])
    assert re.fullmatch(schema["properties"]["country"]["pattern"], record["country"])
