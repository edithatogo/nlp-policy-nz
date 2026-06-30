from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from nlp_policy_nz import pipeline_api
from nlp_policy_nz.ontology import standards


def test_ontology_standard_round_trips_and_registry_helpers(tmp_path: Path) -> None:
    standard = standards.OntologyStandard(
        standard_id="demo",
        label="Demo",
        source_url="https://example.test/demo",
        license="CC0",
        namespace="https://example.test/ns#",
        local_representation="demo -> uri",
        coverage_status="prototype",
    ).with_aliases("Alias One", "Alias Two")

    assert standard.to_dict()["aliases"] == ["Alias One", "Alias Two"]

    resource = standards.LegislativeResource(
        jurisdiction="nz",
        authority="pco",
        year=2024,
        document_kind="act",
        number="12",
        version="1",
        language="mi",
    )
    draft_resource = resource.with_draft_stage("introduced")
    eli_base = "https://example.test/ontology/eli/"
    dl_base = "https://example.test/ontology/eli-dl/"

    eli_uri = standards.build_eli_uri(resource, base_uri=eli_base)
    draft_uri = standards.build_eli_dl_uri(draft_resource, base_uri=dl_base)
    assert standards.parse_eli_uri(eli_uri, base_uri=eli_base) == resource
    assert standards.parse_eli_uri(draft_uri, base_uri=dl_base) == draft_resource
    assert standards.build_eli_uri(draft_resource, base_uri=dl_base) == draft_uri

    with pytest.raises(ValueError):
        standards.build_eli_dl_uri(resource, base_uri=dl_base)
    with pytest.raises(ValueError):
        standards.parse_eli_uri("https://example.test/not-eli", base_uri=eli_base)

    identifier = standards.ECLIIdentifier(
        country_code="nz",
        court_code="hc",
        year=2024,
        sequence="123",
    )
    parsed_identifier = standards.parse_ecli_identifier(standards.build_ecli_identifier(identifier))
    assert parsed_identifier.country_code == "NZ"
    assert parsed_identifier.court_code == "HC"
    assert parsed_identifier.year == identifier.year
    assert parsed_identifier.sequence == identifier.sequence
    with pytest.raises(ValueError):
        standards.parse_ecli_identifier("bad-value")

    concept = standards.ControlledConcept(
        scheme_id="eurovoc",
        concept_id="child-1",
        pref_label="Child Concept",
        notation="A1",
        broader=("parent-1",),
    )
    concept_payload = standards.build_eurovoc_concept(concept)
    assert standards.parse_controlled_concept(concept_payload) == concept

    broader_string_payload = dict(concept_payload)
    broader_string_payload["skos:broader"] = "https://example.test/scheme/parent-2"
    parsed_broader = standards.parse_controlled_concept(broader_string_payload)
    assert parsed_broader.broader == ("parent-2",)

    with pytest.raises(ValueError):
        standards.parse_controlled_concept(
            {
                "@id": "https://example.test/scheme/item",
                "skos:inScheme": "https://example.test/scheme/",
                "skos:prefLabel": "not-an-object",
            }
        )

    profile = standards.LegislationProfile(
        identifier="Public Act 2024",
        name="Public Act 2024",
        jurisdiction="NZ",
        legislation_type="Act",
        date_published="2024-01-01",
        url="https://example.test/acts/public-act-2024",
        same_as=("https://example.test/acts/public-act-2024",),
    )
    schema_payload = standards.build_schema_legislation(profile)
    assert standards.parse_schema_legislation(schema_payload) == profile

    schema_string_payload = dict(schema_payload)
    schema_string_payload["schema:sameAs"] = "https://example.test/acts/public-act-2024"
    assert standards.parse_schema_legislation(schema_string_payload).same_as == (
        "https://example.test/acts/public-act-2024",
    )

    manifest = standards.build_ontology_standards_manifest(tmp_path)
    assert manifest["repository_root"] == str(tmp_path)
    assert manifest["summary"]["total_standards"] == len(manifest["standards"])
    assert set(manifest["summary"]["round_trip_standard_ids"]) <= set(manifest["standard_ids"])
    assert standards.ontology_standard_ids() == tuple(sorted(standards.ontology_standard_ids()))
    assert standards.ontology_standard_mappings()["eli"] == standards.get_ontology_standard("eli").namespace
    with pytest.raises(KeyError):
        standards.get_ontology_standard("missing-standard")

    manifest_path = tmp_path / "ontology-standards.json"
    written = standards.write_ontology_standards_manifest(manifest_path, repo_root_path=tmp_path)
    assert written == manifest_path.resolve()
    assert standards.load_ontology_standards_manifest(written) == manifest
    assert standards.dump_ontology_standards_manifest(tmp_path)

    assert standards._clean_segments("https://example.test/root/a/b") == ["root", "a", "b"]
    assert standards._join_uri("https://example.test/root/", "/a/", "b") == "https://example.test/root/a/b"
    assert standards._slug(" Demo Title! ") == "demo-title"
    assert standards._strip_template_prefix(["a", "b", "c"], ("a", "b")) == ["c"]
    with pytest.raises(ValueError):
        standards._strip_template_prefix(["x"], ("a",))


def test_pipeline_helper_branches_and_search_paths(monkeypatch, tmp_path: Path) -> None:
    class FakeLanguageIdentifier:
        def detect_code_switching(self, text: str) -> list[tuple[str, str]]:
            return [("mi", "kāwanatanga"), ("en", text)]

    class FakeEntity:
        def __init__(self, entity_type: str, name: str, aliases: tuple[str, ...]) -> None:
            self.entity_type = entity_type
            self.name = name
            self._aliases = aliases

        def names(self) -> tuple[str, ...]:
            return (self.name, *self._aliases)

    @dataclass
    class FakeEntityRecord:
        text: str
        label_: str

        def to_dict(self) -> dict[str, str]:
            return {"text": self.text, "label": self.label_}

    @dataclass
    class FakeDivision:
        ayes_count: int
        nays_count: int
        abstains_count: int
        votes: list[dict[str, Any]]
        party_votes: list[dict[str, Any]]
        motion: str

    class FakeResolver:
        def __init__(self) -> None:
            self.calls: list[tuple[str, Any]] = []

        def resolve_doc(self, doc: Any, context: Any = None) -> list[FakeEntityRecord]:
            self.calls.append((getattr(doc, "text", ""), context))
            return [FakeEntityRecord("resolved", "ENTITY")]

    class FakeNlp:
        def __init__(self) -> None:
            self.pipe_names: list[str] = []
            self.resolver = FakeResolver()

        def add_pipe(self, name: str, last: bool = False) -> None:  # noqa: ARG002
            self.pipe_names.append(name)

        def get_pipe(self, _name: str) -> FakeResolver:
            return self.resolver

        def __call__(self, text: str) -> Any:
            return SimpleNamespace(
                text=text,
                ents=[
                    SimpleNamespace(label_="NZ_ACT", text="Act 1"),
                    SimpleNamespace(label_="OTHER", text="ignore"),
                ],
                spans={
                    "nz_cross_references": [SimpleNamespace(label_="SECTION", text="section 5")]
                },
            )

    class FakeLanceDBAdapter:
        def __init__(self, uri: str) -> None:
            self.uri = uri
            self._exists = True

        def index_exists(self) -> bool:
            return self._exists

        def search(self, query_embedding: list[float], top_k: int = 10) -> list[dict[str, Any]]:
            return [{"query_embedding": query_embedding, "top_k": top_k, "uri": self.uri}]

    monkeypatch.setattr(pipeline_api, "LanguageIdentifier", FakeLanguageIdentifier)
    monkeypatch.setattr(pipeline_api, "default_nz_entities", lambda: [FakeEntity("party", "Labour", ("LP",))])
    monkeypatch.setattr(pipeline_api, "NzEntityResolverComponent", FakeResolver)
    monkeypatch.setattr(
        pipeline_api,
        "parse_division",
        lambda text: FakeDivision(
            ayes_count=1,
            nays_count=0,
            abstains_count=0,
            votes=[{"name": text}],
            party_votes=[{"party": "Labour"}],
            motion="Question agreed to.",
        ),
    )
    monkeypatch.setattr(pipeline_api, "amendments_to_dicts", lambda items: [{"item": item} for item in items])
    monkeypatch.setattr(pipeline_api, "parse_amendments", lambda text: [text, text.upper()])
    monkeypatch.setattr(pipeline_api, "load_model", lambda: (object(), object()))
    monkeypatch.setattr(pipeline_api, "generate_embedding", lambda text, model, tokenizer: [len(text)])
    monkeypatch.setattr(pipeline_api, "LanceDBAdapter", FakeLanceDBAdapter)

    model_config = SimpleNamespace(_name_or_path="model/config")
    tokenizer_kwargs = SimpleNamespace(init_kwargs={"name_or_path": "tokenizer/kwargs"})
    tokenizer_direct = SimpleNamespace(name_or_path="tokenizer/direct", init_kwargs={})

    assert pipeline_api._model_version_from_loaded(SimpleNamespace(config=model_config), object()) == "model/config"
    assert (
        pipeline_api._model_version_from_loaded(
            SimpleNamespace(config=SimpleNamespace(_name_or_path=None)),
            tokenizer_kwargs,
        )
        == "tokenizer/kwargs"
    )
    assert (
        pipeline_api._model_version_from_loaded(
            SimpleNamespace(config=SimpleNamespace(_name_or_path=None)),
            tokenizer_direct,
        )
        == "tokenizer/direct"
    )
    assert (
        pipeline_api._model_version_from_loaded(
            SimpleNamespace(config=SimpleNamespace(_name_or_path=None)),
            SimpleNamespace(init_kwargs={}),
        )
        == pipeline_api.DEFAULT_MODEL
    )

    file_path = tmp_path / "input.txt"
    file_path.write_text("Body", encoding="utf-8")
    dir_path = tmp_path / "inputs"
    dir_path.mkdir()
    (dir_path / "b.json").write_text("{}", encoding="utf-8")
    (dir_path / "a.txt").write_text("x", encoding="utf-8")
    (dir_path / "ignore.md").write_text("skip", encoding="utf-8")

    assert pipeline_api._resolve_path(file_path).is_absolute()
    assert pipeline_api._collect_input_files(file_path) == [file_path.resolve()]
    assert [path.name for path in pipeline_api._collect_input_files(dir_path)] == ["a.txt", "b.json"]
    with pytest.raises(FileNotFoundError):
        pipeline_api._collect_input_files(tmp_path / "missing")
    with pytest.raises(FileNotFoundError):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        pipeline_api._collect_input_files(empty_dir)

    assert pipeline_api._extract_te_reo_terms("text") == ["kāwanatanga"]
    assert pipeline_api._extract_citations("text", FakeNlp()) == ["Act 1", "[SECTION] section 5"]

    assert pipeline_api._extract_voting_record("question agreed to") == {
        "ayes_count": 1,
        "nays_count": 0,
        "abstains_count": 0,
        "votes": [{"name": "question agreed to"}],
        "party_votes": [{"party": "Labour"}],
        "motion": "Question agreed to.",
    }
    monkeypatch.setattr(
        pipeline_api,
        "parse_division",
        lambda _text: SimpleNamespace(
            ayes_count=0,
            nays_count=0,
            abstains_count=0,
            votes=[],
            party_votes=[],
            motion=None,
        ),
    )
    assert pipeline_api._extract_voting_record("no division") is None

    monkeypatch.setattr(
        pipeline_api,
        "parse_division",
        lambda text: FakeDivision(
            ayes_count=0,
            nays_count=0,
            abstains_count=0,
            votes=[],
            party_votes=[],
            motion="No division.",
        ),
    )
    assert pipeline_api._extract_voting_record("empty") is None
    monkeypatch.setattr(
        pipeline_api,
        "parse_division",
        lambda text: FakeDivision(
            ayes_count=1,
            nays_count=0,
            abstains_count=0,
            votes=[{"name": text}],
            party_votes=[{"party": "Labour"}],
            motion="Question agreed to.",
        ),
    )

    assert pipeline_api._extract_amendment_records("alpha") == [{"item": "alpha"}, {"item": "ALPHA"}]
    assert pipeline_api._text_mentions_entity("The Labour Party agrees", FakeEntity("party", "Labour Party", ("LP",)))
    assert not pipeline_api._text_mentions_entity("The Greens", FakeEntity("party", "Labour Party", ("LP",)))
    assert pipeline_api._valid_context_date("2024-06-30") == "2024-06-30"
    assert pipeline_api._valid_context_date("30/06/2024") is None

    nlp = FakeNlp()
    resolver = pipeline_api._ensure_nz_entity_resolver(nlp)
    assert isinstance(resolver, FakeResolver)
    assert nlp.pipe_names == ["nz_entity_resolver"]

    entities = pipeline_api._resolve_named_entities(
        "Labour Party",
        nlp,
        context=SimpleNamespace(party="Labour", electorate=None, date="2024-06-30"),
    )
    assert entities == [{"text": "resolved", "label": "ENTITY"}]
    assert nlp.resolver.calls[-1][1].party == "Labour"

    class NoPipeNlp:
        pass

    assert isinstance(pipeline_api._ensure_nz_entity_resolver(NoPipeNlp()), FakeResolver)
    assert pipeline_api._resolve_named_entities("text", NoPipeNlp()) == []

    db_path = tmp_path / "lancedb"
    db_path.mkdir()
    assert pipeline_api.search_similar("query", db_path=db_path, top_k=3) == [
        {"query_embedding": [5], "top_k": 3, "uri": str(db_path.resolve())}
    ]

    class MissingIndexAdapter(FakeLanceDBAdapter):
        def index_exists(self) -> bool:
            return False

    monkeypatch.setattr(pipeline_api, "LanceDBAdapter", MissingIndexAdapter)
    with pytest.raises(RuntimeError):
        pipeline_api.search_similar("query", db_path=db_path, top_k=3)

    with pytest.raises(FileNotFoundError):
        pipeline_api.search_similar("query", db_path=tmp_path / "missing-db")
