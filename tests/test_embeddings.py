"""Tests for the semantic layer embeddings (Track 5, Task 5.2).

Validates the ``EmbeddingResult`` struct, standalone embedding functions, and
the ``EmbeddingGenerator`` class — all *without* loading actual transformer
models (too heavyweight for CI).
"""

from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import get_type_hints

import pytest
import torch

from nlp_policy_nz.semantic.embeddings import (
    EmbeddingGenerator,
    EmbeddingResult,
    _mean_pooling,
    generate_embedding,
    generate_embeddings_batch,
)

# ---------------------------------------------------------------------------
# EmbeddingResult struct
# ---------------------------------------------------------------------------


class TestEmbeddingResult:
    """Validate the ``EmbeddingResult`` msgspec struct."""

    def test_struct_fields_exist(self) -> None:
        """Struct should define all five required fields."""
        fields = set(EmbeddingResult.__struct_fields__)
        assert fields == {"doc_id", "text", "embedding", "model_name", "dimension"}

    def test_struct_field_types(self) -> None:
        """Each field should have the correct type annotation."""
        hints = get_type_hints(EmbeddingResult)
        assert hints["doc_id"] is str
        assert hints["text"] is str
        assert hints["embedding"] == list[float]
        assert hints["model_name"] is str
        assert hints["dimension"] is int

    def test_default_instantiation(self) -> None:
        """Creating an instance with all fields should work."""
        result = EmbeddingResult(
            doc_id="doc1",
            text="Some policy text",
            embedding=[0.1, 0.2, 0.3],
            model_name="test-model",
            dimension=3,
        )
        assert result.doc_id == "doc1"
        assert result.text == "Some policy text"
        assert result.embedding == [0.1, 0.2, 0.3]
        assert result.model_name == "test-model"
        assert result.dimension == 3  # noqa: PLR2004

    def test_is_msgspec_struct(self) -> None:
        """``EmbeddingResult`` should be a subclass of ``msgspec.Struct``."""
        import msgspec  # noqa: PLC0415

        assert issubclass(EmbeddingResult, msgspec.Struct)

    def test_repr(self) -> None:
        """String representation should be informative."""
        result = EmbeddingResult(
            doc_id="d1",
            text="hello",
            embedding=[0.5],
            model_name="m",
            dimension=1,
        )
        assert "EmbeddingResult" in repr(result)
        assert "d1" in repr(result)


# ---------------------------------------------------------------------------
# generate_embedding (signature only)
# ---------------------------------------------------------------------------


class TestGenerateEmbedding:
    """Validate the ``generate_embedding`` function signature."""

    def test_function_exists(self) -> None:
        """``generate_embedding`` should be a callable function."""
        assert callable(generate_embedding)

    def test_signature_parameters(self) -> None:
        """Function should accept ``text``, ``model``, ``tokenizer``, and
        ``max_length``."""
        sig = inspect.signature(generate_embedding)
        params = list(sig.parameters.keys())
        assert "text" in params
        assert "model" in params
        assert "tokenizer" in params
        assert "max_length" in params

    def test_max_length_default(self) -> None:
        """``max_length`` should default to ``512``."""
        sig = inspect.signature(generate_embedding)
        param = sig.parameters["max_length"]
        assert param.default == 512  # noqa: PLR2004

    def test_return_type_annotation(self) -> None:
        """Return type should be ``list[float]``."""
        sig = inspect.signature(generate_embedding)
        # String annotation due to ``from __future__ import annotations``
        assert sig.return_annotation == "list[float]"

    def test_requires_model_and_tokenizer(self) -> None:
        """Calling without a model/tokenizer should raise ``TypeError``."""
        with pytest.raises(TypeError):
            generate_embedding("test")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# generate_embeddings_batch (signature only)
# ---------------------------------------------------------------------------


class TestGenerateEmbeddingsBatch:
    """Validate the ``generate_embeddings_batch`` function signature."""

    def test_function_exists(self) -> None:
        """``generate_embeddings_batch`` should be a callable function."""
        assert callable(generate_embeddings_batch)

    def test_signature_parameters(self) -> None:
        """Function should accept ``texts``, ``model``, ``tokenizer``,
        ``batch_size``, and ``max_length``."""
        sig = inspect.signature(generate_embeddings_batch)
        params = list(sig.parameters.keys())
        assert "texts" in params
        assert "model" in params
        assert "tokenizer" in params
        assert "batch_size" in params
        assert "max_length" in params

    def test_batch_size_default(self) -> None:
        """``batch_size`` should default to ``32``."""
        sig = inspect.signature(generate_embeddings_batch)
        assert sig.parameters["batch_size"].default == 32  # noqa: PLR2004

    def test_max_length_default(self) -> None:
        """``max_length`` should default to ``512``."""
        sig = inspect.signature(generate_embeddings_batch)
        assert sig.parameters["max_length"].default == 512  # noqa: PLR2004

    def test_return_type_annotation(self) -> None:
        """Return type should be ``list[list[float]]``."""
        sig = inspect.signature(generate_embeddings_batch)
        assert sig.return_annotation == "list[list[float]]"


# ---------------------------------------------------------------------------
# EmbeddingGenerator class (no model loading)
# ---------------------------------------------------------------------------


class TestEmbeddingGenerator:
    """Validate the ``EmbeddingGenerator`` class interface."""

    def test_init_defaults(self) -> None:
        """Default initialisation should set ``model_name=None`` and
        ``device='cpu'``."""
        gen = EmbeddingGenerator()
        assert gen._model_name is None
        assert gen._device == "cpu"

    def test_init_custom(self) -> None:
        """Custom ``model_name`` and ``device`` should be stored."""
        gen = EmbeddingGenerator(model_name="bert-base-uncased", device="cuda")
        assert gen._model_name == "bert-base-uncased"
        assert gen._device == "cuda"

    def test_model_property_raises_before_load(self) -> None:
        """Accessing ``model`` before loading should raise ``RuntimeError``."""
        gen = EmbeddingGenerator()
        with pytest.raises(RuntimeError, match="not loaded"):
            _ = gen.model

    def test_tokenizer_property_raises_before_load(self) -> None:
        """Accessing ``tokenizer`` before loading should raise
        ``RuntimeError``."""
        gen = EmbeddingGenerator()
        with pytest.raises(RuntimeError, match="not loaded"):
            _ = gen.tokenizer

    def test_model_name_property_empty_before_load(self) -> None:
        """``model_name`` should be an empty string before loading."""
        gen = EmbeddingGenerator()
        assert gen.model_name == ""

    def test_has_context_manager(self) -> None:
        """``EmbeddingGenerator`` should support ``with`` statements."""
        gen = EmbeddingGenerator()
        assert hasattr(gen, "__enter__")
        assert hasattr(gen, "__exit__")

    def test_context_manager_protocol_mocked(self) -> None:
        """``__enter__`` should return ``self`` (same instance) with mocked
        ``load`` to avoid actual model downloads."""
        gen = EmbeddingGenerator()
        original_load = gen.load
        gen.load = lambda: None  # no-op to avoid model loading
        returned = gen.__enter__()
        assert returned is gen
        gen.load = original_load

    def test_embed_method_exists(self) -> None:
        """``embed`` should be a callable method."""
        gen = EmbeddingGenerator()
        assert callable(gen.embed)

    def test_embed_signature(self) -> None:
        """``embed`` should accept a single ``text`` argument."""
        sig = inspect.signature(EmbeddingGenerator.embed)
        params = list(sig.parameters.keys())
        assert "text" in params
        assert "self" in params

    def test_embed_return_type(self) -> None:
        """``embed`` return annotation should be ``EmbeddingResult``."""
        hints = get_type_hints(EmbeddingGenerator.embed)
        assert hints["return"] == EmbeddingResult

    def test_embed_batch_method_exists(self) -> None:
        """``embed_batch`` should be a callable method."""
        gen = EmbeddingGenerator()
        assert callable(gen.embed_batch)

    def test_embed_batch_signature(self) -> None:
        """``embed_batch`` should accept ``texts`` and optional
        ``doc_ids``."""
        sig = inspect.signature(EmbeddingGenerator.embed_batch)
        params = list(sig.parameters.keys())
        assert "texts" in params
        assert "doc_ids" in params
        assert "self" in params

    def test_embed_batch_return_type(self) -> None:
        """``embed_batch`` return annotation should be
        ``list[EmbeddingResult]``."""
        hints = get_type_hints(EmbeddingGenerator.embed_batch)
        assert hints["return"] == list[EmbeddingResult]

    def test_load_method_exists(self) -> None:
        """``load`` should be a callable method."""
        gen = EmbeddingGenerator()
        assert callable(gen.load)

    def test_unload_method_exists(self) -> None:
        """``unload`` should be a callable method."""
        gen = EmbeddingGenerator()
        assert callable(gen.unload)


# ---------------------------------------------------------------------------
# behavioural coverage
# ---------------------------------------------------------------------------


class _FakeTokenizer:
    def __call__(self, texts, **_kwargs):
        batch_size = 1 if isinstance(texts, str) else len(texts)
        return {"attention_mask": torch.tensor([[1, 1, 0]] * batch_size)}


class _FakeModel:
    def __call__(self, **inputs):
        batch_size, seq_len = inputs["attention_mask"].shape
        token_embeddings = torch.tensor(
            [[[1.0, 2.0], [3.0, 4.0], [100.0, 100.0]]] * batch_size,
            dtype=torch.float32,
        )
        assert token_embeddings.shape[1] == seq_len
        return SimpleNamespace(last_hidden_state=token_embeddings)


class TestEmbeddingBehaviour:
    def test_mean_pooling_ignores_padding(self) -> None:
        token_embeddings = torch.tensor([[[1.0, 2.0], [3.0, 4.0], [100.0, 100.0]]])
        attention_mask = torch.tensor([[1, 1, 0]])

        pooled = _mean_pooling(token_embeddings, attention_mask)

        assert pooled.tolist() == [[2.0, 3.0]]

    def test_generate_embedding_uses_model_and_tokenizer(self) -> None:
        embedding = generate_embedding("hello", _FakeModel(), _FakeTokenizer())
        assert embedding == [2.0, 3.0]

    def test_generate_embeddings_batch_chunks_inputs(self) -> None:
        embeddings = generate_embeddings_batch(
            ["a", "b", "c"],
            _FakeModel(),
            _FakeTokenizer(),
            batch_size=2,
        )

        assert embeddings == [[2.0, 3.0], [2.0, 3.0], [2.0, 3.0]]

    def test_generator_load_embed_and_unload(self, monkeypatch) -> None:
        calls: dict[str, object] = {}

        class FakeModel:
            def __init__(self) -> None:
                self.config = SimpleNamespace(_name_or_path="loaded/model")

            def eval(self) -> None:
                calls["eval"] = True

            def to(self, device: str) -> None:
                calls["to"] = device

        class FakeTokenizer:
            pass

        monkeypatch.setattr(
            "nlp_policy_nz.semantic.embeddings.load_model",
            lambda model_name=None: (FakeModel(), FakeTokenizer()),
        )
        monkeypatch.setattr(
            "nlp_policy_nz.semantic.embeddings.unload_model",
            lambda model: calls.setdefault("unloaded", model),
        )
        monkeypatch.setattr(
            "nlp_policy_nz.semantic.embeddings.generate_embedding",
            lambda text, model, tokenizer: [float(len(text))],
        )
        monkeypatch.setattr(
            "nlp_policy_nz.semantic.embeddings.generate_embeddings_batch",
            lambda texts, model, tokenizer: [[float(len(text))] for text in texts],
        )

        gen = EmbeddingGenerator(model_name="custom/model", device="cpu")
        gen.load()
        assert gen.model_name == "custom/model"
        assert calls["eval"] is True

        result = gen.embed("abc")
        assert result == EmbeddingResult(
            doc_id="",
            text="abc",
            embedding=[3.0],
            model_name="custom/model",
            dimension=1,
        )

        batch = gen.embed_batch(["a", "bc"], doc_ids=["doc-a", "doc-b"])
        assert [item.doc_id for item in batch] == ["doc-a", "doc-b"]
        assert [item.dimension for item in batch] == [1, 1]

        with pytest.raises(ValueError):
            gen.embed_batch(["a"], doc_ids=["too", "many"])

        gen.unload()
        assert "unloaded" in calls
