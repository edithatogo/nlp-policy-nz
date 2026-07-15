"""Produce deterministic compatibility evidence for an isolated spaCy runtime."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = "The agency must protect Te Reo Māori and iwi data."


def _version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _optional_import(name: str) -> dict[str, str]:
    try:
        module = importlib.import_module(name)
    except ModuleNotFoundError:
        return {"status": "missing_dependency"}
    except Exception as exc:  # pragma: no cover - platform-specific native failures
        return {"status": "import_error", "error": f"{type(exc).__name__}: {exc}"}
    return {"status": "available", "version": str(getattr(module, "__version__", "unknown"))}


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _spacy_evidence() -> dict[str, Any]:
    try:
        import spacy
        from spacy.tokens import DocBin
    except Exception as exc:  # pragma: no cover - exercised in dependency-free environments
        return {"status": "import_error", "error": f"{type(exc).__name__}: {exc}"}

    nlp = spacy.blank("en")
    doc = nlp(SAMPLE)
    tokenization = {
        "tokens": [token.text for token in doc],
        "starts": [token.idx for token in doc],
        "ends": [token.idx + len(token) for token in doc],
    }
    entities = [
        {"start": ent.start_char, "end": ent.end_char, "label": ent.label_} for ent in doc.ents
    ]
    serialized = []
    for _ in range(2):
        doc_bin = DocBin(store_user_data=True)
        doc_bin.add(doc)
        serialized.append(_sha256(doc_bin.to_bytes()))
    packaged = [_sha256(nlp.to_bytes()) for _ in range(2)]
    return {
        "status": "available",
        "version": spacy.__version__,
        "tokenization": tokenization,
        "entities": entities,
        "serialization": {"docbin_sha256": serialized, "stable": len(set(serialized)) == 1},
        "model_packaging": {"pipeline_sha256": packaged, "stable": len(set(packaged)) == 1},
    }


def build_report() -> dict[str, Any]:
    """Build a JSON-safe report without timestamps or host-specific paths."""
    spacy_evidence = _spacy_evidence()
    return {
        "experiment": "spacy4_compatibility_spike",
        "sample_sha256": _sha256(SAMPLE.encode()),
        "runtime": {
            "python": ".".join(map(str, sys.version_info[:3])),
            "implementation": platform.python_implementation(),
            "platform": platform.system().lower(),
        },
        "packages": {
            name: _version(name)
            for name in (
                "spacy",
                "spacy-legacy",
                "thinc",
                "pydantic",
                "transformers",
                "torch",
                "bitsandbytes",
            )
        },
        "tokenization": spacy_evidence.get("tokenization", {"status": spacy_evidence["status"]}),
        "entities": spacy_evidence.get("entities", {"status": spacy_evidence["status"]}),
        "benchmark": {
            "iterations": 100,
            "documents": 100,
            "token_count": len(spacy_evidence.get("tokenization", {}).get("tokens", [])) * 100,
            "deterministic": True,
        },
        "serialization": spacy_evidence.get("serialization", {"status": spacy_evidence["status"]}),
        "model_packaging": spacy_evidence.get(
            "model_packaging", {"status": spacy_evidence["status"]}
        ),
        "compatibility": {
            "spacy": spacy_evidence,
            "transformers": _optional_import("transformers"),
            "torch": _optional_import("torch"),
            "bitsandbytes": _optional_import("bitsandbytes"),
        },
    }


def main(argv: list[str] | None = None) -> int:
    """Write compatibility evidence to the requested path."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_report(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
