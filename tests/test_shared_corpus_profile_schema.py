from __future__ import annotations

import json
import re
from pathlib import Path


def test_shared_corpus_schema_parameterizes_country_and_corpus_id() -> None:
    schema = json.loads(Path("schemas/shared_nz_corpus_core.schema.json").read_text())
    country = schema["properties"]["country"]
    corpus_id = schema["properties"]["corpus_id"]

    assert country["default"] == "NZ"
    assert "const" not in country
    assert re.fullmatch(country["pattern"], "NZ")
    assert re.fullmatch(country["pattern"], "AU")
    assert not re.fullmatch(country["pattern"], "Australia")

    assert corpus_id["default"] == "corpus-nz-legislation"
    assert "enum" not in corpus_id
    assert re.fullmatch(corpus_id["pattern"], "corpus-nz-legislation")
    assert re.fullmatch(corpus_id["pattern"], "corpus-au-vic-foi")
    assert not re.fullmatch(corpus_id["pattern"], "not-a-corpus")


def test_shared_schema_retains_exact_new_zealand_defaults() -> None:
    schema = json.loads(Path("schemas/shared_nz_corpus_core.schema.json").read_text())

    assert schema["properties"]["country"]["default"] == "NZ"
    assert schema["properties"]["jurisdiction"]["default"] == "New Zealand"
    assert schema["properties"]["corpus_id"]["default"] == "corpus-nz-legislation"
