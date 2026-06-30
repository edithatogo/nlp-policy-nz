"""Tests for PROV-O provenance recording and sidecar integration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from nlp_policy_nz.cli.main import main
from nlp_policy_nz.provenance import (
    ProvenanceRecorder,
    load_provenance_sidecar,
    provenance_sidecar_path,
    serialize_prov_o_jsonld,
)
from nlp_policy_nz.provenance import recorder as recorder_module


def _case_dir(name: str) -> Path:
    """Return a small workspace-local test directory."""
    path = Path(".tmp") / "provenance-tests" / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_recorder_captures_pipeline_context() -> None:
    """Recorder captures version, model, parameters, timestamps, and output."""
    recorder = ProvenanceRecorder(
        pipeline_name="process_legislation",
        pipeline_version="1.2.3",
        model_versions={"legal-bert": "1.0"},
        parameters={"generate_embeddings": False},
        commit_sha="abc1234",
    )

    record = recorder.finish(
        input_paths=[Path("input.xml")],
        output_path=Path("output.parquet"),
        record_count=2,
        zenodo_doi="10.5072/zenodo.12345",
    )

    assert record.pipeline_version == "1.2.3"
    assert record.model_versions == {"legal-bert": "1.0"}
    assert record.parameters["generate_embeddings"] is False
    assert record.commit_sha == "abc1234"
    assert record.output_path == "output.parquet"
    assert record.record_count == 2
    assert record.started_at <= record.ended_at


def test_serializer_emits_prov_o_jsonld() -> None:
    """Serializer emits PROV-O Entity, Activity, and Agent JSON-LD nodes."""
    record = ProvenanceRecorder(
        pipeline_name="process_hansard",
        pipeline_version="0.1.0",
        model_versions={"embedding": "test-model"},
        parameters={"source": "hansard"},
        commit_sha="def5678",
    ).finish(
        input_paths=[Path("speech.txt")],
        output_path=Path("hansard.parquet"),
        record_count=1,
    )

    data = serialize_prov_o_jsonld(record)

    assert data["@context"]["prov"] == "http://www.w3.org/ns/prov#"
    assert data["@type"] == "prov:Bundle"
    assert any(node["@type"] == "prov:Activity" for node in data["@graph"])
    assert any(node["@type"] == "prov:Entity" for node in data["@graph"])
    assert any(node["@type"] == "prov:Agent" for node in data["@graph"])


def test_serializer_includes_inputs_and_zenodo_doi() -> None:
    record = ProvenanceRecorder(
        pipeline_name="process_legislation",
        pipeline_version="0.2.0",
        model_versions={"embedding": "demo"},
        parameters={"source": "legislation"},
        commit_sha="abc1234",
    ).finish(
        input_paths=[Path("a.txt"), Path("b.txt")],
        output_path=Path("out.parquet"),
        record_count=2,
        zenodo_doi="10.5072/zenodo.12345",
    )

    data = serialize_prov_o_jsonld(record)
    assert data["@graph"][2]["schema:sameAs"] == "10.5072/zenodo.12345"
    assert {node["schema:contentUrl"] for node in data["@graph"][3:]} == {"a.txt", "b.txt"}


def test_sidecar_round_trip() -> None:
    """Sidecar helper writes and reads ``.prov.json`` beside Parquet output."""
    tmp_path = _case_dir("sidecar")
    parquet = tmp_path / "dataset.parquet"
    record = ProvenanceRecorder(
        pipeline_name="process_legislation",
        pipeline_version="0.1.0",
        model_versions={},
        parameters={},
        commit_sha="unknown",
    ).finish(input_paths=[], output_path=parquet, record_count=0)

    sidecar = record.write_sidecar(parquet)

    assert sidecar == tmp_path / "dataset.prov.json"
    assert provenance_sidecar_path(parquet) == sidecar
    loaded = load_provenance_sidecar(parquet)
    assert loaded["@type"] == "prov:Bundle"


def test_sidecar_loader_accepts_json_path(tmp_path: Path) -> None:
    sidecar = tmp_path / "dataset.prov.json"
    sidecar.write_text('{"@type": "prov:Bundle"}', encoding="utf-8")

    assert load_provenance_sidecar(sidecar) == {"@type": "prov:Bundle"}


def test_process_legislation_writes_provenance_sidecar(monkeypatch) -> None:
    """Processing APIs write a provenance sidecar next to Parquet output."""
    from nlp_policy_nz import pipeline_api  # noqa: PLC0415

    tmp_path = _case_dir("process-legislation")
    input_file = tmp_path / "act.txt"
    output_file = tmp_path / "legislation.parquet"
    input_file.write_text("The Minister must report.", encoding="utf-8")

    class FakeNlp:
        def __init__(self) -> None:
            self.pipe_names: list[str] = []

        def add_pipe(self, *_args: Any, **_kwargs: Any) -> None:
            self.pipe_names.append("deontic_modality")

        def __call__(self, _text: str) -> Any:
            return type("Doc", (), {"ents": [], "spans": {}})()

    def _write_fake_parquet(_records: list[Any], out: str | Path) -> Path:
        path = Path(out)
        path.write_bytes(b"parquet")
        return path

    def _fake_nlp() -> FakeNlp:
        return FakeNlp()

    monkeypatch.setattr(pipeline_api, "create_nlp_pipeline", _fake_nlp)
    monkeypatch.setattr(pipeline_api, "create_citation_ruler", lambda _nlp: None)
    monkeypatch.setattr(
        pipeline_api,
        "chunk_legislation_document",
        lambda _text, _nlp, year, number: [{"doc_id": "doc-1", "text": "Body"}],
    )
    monkeypatch.setattr(pipeline_api, "_extract_te_reo_terms", lambda _text: [])
    monkeypatch.setattr(pipeline_api, "_extract_citations", lambda _text, _nlp: [])
    monkeypatch.setattr(pipeline_api, "detect_modality", lambda _text, _nlp: [])
    monkeypatch.setattr(pipeline_api, "detect_temporal_expressions", lambda _text, _nlp: [])
    monkeypatch.setattr(pipeline_api, "classify_legal_effect", lambda _text, _nlp: None)
    monkeypatch.setattr(pipeline_api, "serialize_to_parquet", _write_fake_parquet)

    result = pipeline_api.process_legislation(
        input_file,
        output_file,
        generate_embeddings=False,
    )

    assert result == output_file.resolve()
    sidecar = provenance_sidecar_path(result)
    assert sidecar.is_file()
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    assert data["@type"] == "prov:Bundle"
    assert "process_legislation" in json.dumps(data)


def test_process_legislation_records_embedding_model_version(monkeypatch) -> None:
    """Embedding-enabled runs record the loaded embedding model identity."""
    from nlp_policy_nz import pipeline_api  # noqa: PLC0415

    tmp_path = _case_dir("process-legislation-model")
    input_file = tmp_path / "act.txt"
    output_file = tmp_path / "legislation.parquet"
    input_file.write_text("The Minister must report.", encoding="utf-8")

    class FakeNlp:
        def __init__(self) -> None:
            self.pipe_names: list[str] = []

        def add_pipe(self, *_args: Any, **_kwargs: Any) -> None:
            self.pipe_names.append("deontic_modality")

        def __call__(self, _text: str) -> Any:
            return type("Doc", (), {"ents": [], "spans": {}})()

    class FakeModel:
        config = type("Config", (), {"_name_or_path": "test/legal-bert"})()

    class FakeTokenizer:
        name_or_path = "fallback/tokenizer"

        def __init__(self) -> None:
            self.init_kwargs: dict[str, str] = {}

    def _write_fake_parquet(_records: list[Any], out: str | Path) -> Path:
        path = Path(out)
        path.write_bytes(b"parquet")
        return path

    monkeypatch.setattr(pipeline_api, "create_nlp_pipeline", FakeNlp)
    monkeypatch.setattr(pipeline_api, "create_citation_ruler", lambda _nlp: None)
    monkeypatch.setattr(
        pipeline_api,
        "chunk_legislation_document",
        lambda _text, _nlp, year, number: [{"doc_id": "doc-1", "text": "Body"}],
    )
    monkeypatch.setattr(pipeline_api, "_extract_te_reo_terms", lambda _text: [])
    monkeypatch.setattr(pipeline_api, "_extract_citations", lambda _text, _nlp: [])
    monkeypatch.setattr(pipeline_api, "detect_modality", lambda _text, _nlp: [])
    monkeypatch.setattr(pipeline_api, "detect_temporal_expressions", lambda _text, _nlp: [])
    monkeypatch.setattr(pipeline_api, "classify_legal_effect", lambda _text, _nlp: None)
    monkeypatch.setattr(pipeline_api, "serialize_to_parquet", _write_fake_parquet)
    monkeypatch.setattr(pipeline_api, "load_model", lambda: (FakeModel(), FakeTokenizer()))
    monkeypatch.setattr(
        pipeline_api,
        "generate_embedding",
        lambda _text, _model, _tokenizer: [0.1],
    )

    result = pipeline_api.process_legislation(
        input_file,
        output_file,
        generate_embeddings=True,
    )

    data = json.loads(provenance_sidecar_path(result).read_text(encoding="utf-8"))
    assert data["@graph"][1]["schema:instrument"] == {
        "embedding_model": "test/legal-bert",
    }


def test_recorder_finish_uses_fallbacks_and_write_sidecar_default(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(recorder_module, "_package_version", lambda: "9.9.9")
    monkeypatch.setattr(recorder_module, "_git_commit_sha", lambda: "deadbeef")
    monkeypatch.setattr(recorder_module, "_utc_now", lambda: "2026-06-29T00:00:00Z")

    recorder = ProvenanceRecorder(
        pipeline_name="process_legislation",
        model_versions={"embedding": "demo"},
        parameters={"source": "legislation"},
        started_at="2026-06-29T00:00:00Z",
    )
    record = recorder.finish(
        input_paths=[tmp_path / "input.xml"],
        output_path=tmp_path / "output.parquet",
        record_count=3,
    )

    assert record.pipeline_version == "9.9.9"
    assert record.commit_sha == "deadbeef"
    assert record.run_id == "urn:nlp-policy-nz:run:2026-06-29T00:00:00Z"
    assert record.input_paths == [str(tmp_path / "input.xml")]
    assert record.output_path == str(tmp_path / "output.parquet")
    assert record.to_jsonld()["@type"] == "prov:Bundle"
    assert record.write_sidecar().name == "output.prov.json"


def test_package_version_and_git_commit_fallbacks(monkeypatch) -> None:
    class PackageNotFoundError(Exception):
        pass

    monkeypatch.setattr(recorder_module.metadata, "PackageNotFoundError", PackageNotFoundError)
    monkeypatch.setattr(recorder_module.metadata, "version", lambda _name: (_ for _ in ()).throw(PackageNotFoundError()))
    monkeypatch.setattr(recorder_module.subprocess, "run", lambda *args, **kwargs: (_ for _ in ()).throw(OSError()))

    assert recorder_module._package_version() == "0.0.0+local"
    assert recorder_module._git_commit_sha() == "unknown"


def test_cli_provenance_displays_sidecar(capsys) -> None:
    """CLI provenance subcommand displays sidecar JSON-LD."""
    tmp_path = _case_dir("cli")
    parquet = tmp_path / "dataset.parquet"
    parquet.write_bytes(b"parquet")
    record = ProvenanceRecorder(
        pipeline_name="process_hansard",
        pipeline_version="0.1.0",
        model_versions={},
        parameters={},
        commit_sha="unknown",
    ).finish(input_paths=[], output_path=parquet, record_count=0)
    record.write_sidecar(parquet)

    rc = main(["provenance", str(parquet)])

    assert rc == 0
    assert "process_hansard" in capsys.readouterr().out


def test_release_archive_includes_provenance_metadata() -> None:
    """Release metadata includes provenance payload when a sidecar exists."""
    tmp_path = _case_dir("release")
    parquet = tmp_path / "dataset.parquet"
    parquet.write_bytes(b"parquet")
    sidecar = tmp_path / "dataset.prov.json"
    sidecar.write_text('{"@type": "prov:Bundle"}', encoding="utf-8")

    with patch("nlp_policy_nz.integrations.release.pq.read_table") as read_table:
        read_table.return_value = [object(), object()]
        from nlp_policy_nz.integrations.release import ReleaseManager  # noqa: PLC0415

        archive = ReleaseManager(token="tok").create_release_archive(
            parquet,
            version="1.0.0",
            title="Release",
            description="Desc",
            creators=[{"name": "Doe, Jane"}],
            output_dir=tmp_path,
        )

    import tarfile  # noqa: PLC0415

    with tarfile.open(archive, "r:gz") as tar:
        metadata_member = tar.extractfile("metadata.json")
        assert metadata_member is not None
        metadata = json.loads(metadata_member.read())

    assert metadata["provenance"]["@type"] == "prov:Bundle"


def test_zenodo_deposit_payload_includes_provenance_notes(monkeypatch) -> None:
    """Zenodo deposit creation carries provenance metadata in the payload."""
    from nlp_policy_nz.integrations import zenodo  # noqa: PLC0415

    captured: dict[str, Any] = {}

    class FakeResponse:
        ok = True

        def json(self) -> dict[str, Any]:
            return {"id": 123}

    def _post(url: str, **kwargs: Any) -> FakeResponse:
        captured["url"] = url
        captured.update(kwargs)
        return FakeResponse()

    monkeypatch.setattr(zenodo.requests, "post", _post)

    result = zenodo.create_sandbox_deposit(
        title="Dataset",
        description="Desc",
        creators=[{"name": "Doe, Jane"}],
        token="tok",
        provenance_metadata={"@type": "prov:Bundle"},
    )

    notes = captured["json"]["metadata"]["notes"]
    assert result == {"id": 123}
    assert "prov:Bundle" in notes
