from __future__ import annotations

from typing import Any

import pytest

from nlp_policy_nz.integrations import huggingface as hf


def test_get_hf_token_and_resolve_token(monkeypatch) -> None:
    monkeypatch.delenv(hf.HF_TOKEN_ENV_VAR, raising=False)

    with pytest.raises(ValueError, match=hf.HF_TOKEN_ENV_VAR):
        hf.get_hf_token()

    assert hf._resolve_token("explicit-token") == "explicit-token"
    assert hf._resolve_token(None) is None

    monkeypatch.setenv(hf.HF_TOKEN_ENV_VAR, "env-token")
    assert hf.get_hf_token() == "env-token"
    assert hf._resolve_token(None) == "env-token"


def test_load_dataset_success_and_failure(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    def fake_load_dataset(path: str, *, split: str, streaming: bool, token: str | None):
        captured.update(
            {
                "path": path,
                "split": split,
                "streaming": streaming,
                "token": token,
            }
        )
        return [{"path": path, "split": split}]

    monkeypatch.setattr(hf.datasets, "load_dataset", fake_load_dataset)

    rows = list(hf.load_hansard_dataset(split="test", streaming=False, token="tok"))
    assert rows == [{"path": "nz-hansard", "split": "test"}]
    assert captured == {
        "path": "nz-hansard",
        "split": "test",
        "streaming": False,
        "token": "tok",
    }

    rows = list(hf.load_legislation_dataset(split="validation", streaming=True, token=None))
    assert rows == [{"path": "nz-legislation", "split": "validation"}]
    assert captured["path"] == "nz-legislation"

    def failing_load_dataset(*_args: Any, **_kwargs: Any):
        raise RuntimeError("boom")

    monkeypatch.setattr(hf.datasets, "load_dataset", failing_load_dataset)
    with pytest.raises(hf.DatasetLoadError) as excinfo:
        hf._load_dataset("nz-hansard", split="train", streaming=True, token=None)

    assert "Failed to load dataset 'nz-hansard'" in str(excinfo.value)
