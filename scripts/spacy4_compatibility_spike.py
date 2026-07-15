#!/usr/bin/env python
"""Run the isolated spaCy 4 compatibility spike and write JSON evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

BASELINE_VERSION = "3.8.14"
CANDIDATE_VERSION = "4.0.0.dev3"
TRANSFORMERS_PROBE_VERSION = "4.49.0"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _package_version(name: str) -> str | None:
    """Return an installed package version without making import mandatory."""
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _run_baseline(iterations: int) -> dict[str, Any]:
    """Measure the current XML-to-spans-to-manifest extraction path."""
    import spacy

    from nlp_policy_nz.xml_parser import (
        SAMPLE_NZ_XML,
        LegislativeXMLParser,
        nz_xml_structure_injector,
    )

    nlp = spacy.blank("en")
    nlp.add_pipe(nz_xml_structure_injector.__name__)
    timings: list[float] = []
    output = ""
    span_fingerprint = ""
    source_text, metadata = LegislativeXMLParser(SAMPLE_NZ_XML).parse()
    source_sha256 = hashlib.sha256(source_text.encode("utf-8")).hexdigest()

    for _ in range(max(1, iterations)):
        started = time.perf_counter()
        doc = nlp.make_doc(source_text)
        doc._.nz_xml_metadata = metadata
        doc = nlp(doc)
        spans = tuple(
            {"start": span.start_char, "end": span.end_char, "text": span.text}
            for span in doc.spans["nz_xml_structure"]
        )
        output = json.dumps(
            {
                "record_id": "spacy4-spike-0001",
                "family": "entity",
                "label": "xml_structure",
                "source_trace": {
                    "citation_path": "fixture/nz-legislation/sample-act",
                    "source_sha256": source_sha256,
                    "spans": spans,
                },
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        timings.append(time.perf_counter() - started)
        span_fingerprint = hashlib.sha256(json.dumps(spans, sort_keys=True).encode()).hexdigest()

    return {
        "status": "measured",
        "spacy_version": _package_version("spacy") or spacy.__version__,
        "python_version": platform.python_version(),
        "transformers_version": _package_version("transformers"),
        "transformers_probe_version": TRANSFORMERS_PROBE_VERSION,
        "iterations": len(timings),
        "mean_ms": round(sum(timings) / len(timings) * 1000, 6),
        "span_count": len(spans),
        "span_fingerprint": span_fingerprint,
        "serialization_bytes": len(output.encode("utf-8")),
        "serialization_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
        "fixture_sha256": source_sha256,
        "accuracy": {
            "status": "not_measured",
            "reason": "The repository has no labelled FOI-O gold set; span alignment is measured instead.",
        },
    }


def _probe_candidate(python_version: str) -> dict[str, Any]:
    """Attempt an isolated candidate install without mutating project environments."""
    uv = shutil.which("uv")
    if uv is None and os.name == "nt":
        local_uv = Path.home() / ".local" / "bin" / "uv.exe"
        uv = str(local_uv) if local_uv.is_file() else None
    if uv is None:
        return {"status": "not_run", "reason": "uv is not available"}
    command = [
        uv,
        "run",
        "--no-project",
        "--python",
        python_version,
        "--prerelease=allow",
        "--with",
        f"spacy=={CANDIDATE_VERSION}",
        "--with",
        f"transformers=={TRANSFORMERS_PROBE_VERSION}",
        "--with",
        "click>=8.0",
        "python",
        "-c",
        "import spacy, transformers; print(spacy.__version__, transformers.__version__)",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    detail = (result.stderr or result.stdout).strip().splitlines()
    return {
        "status": "importable" if result.returncode == 0 else "blocked",
        "python_version": python_version,
        "candidate_version": CANDIDATE_VERSION,
        "transformers_probe_version": TRANSFORMERS_PROBE_VERSION,
        "return_code": result.returncode,
        "detail": "\n".join(detail[-8:]),
        "command": " ".join(command),
    }


def main() -> int:
    """Run the spike and write a machine-readable evidence record."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--probe-candidate", action="store_true")
    parser.add_argument("--python-version", default="3.12")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts/track104/spacy4_compatibility_spike.json",
    )
    args = parser.parse_args()
    evidence = {
        "track": "104_spacy4_compatibility_spike",
        "status": "candidate_blocked",
        "production_policy": {
            "spacy_spec": ">=3.7.0 (locked baseline 3.8.14),<4.0.0",
            "switch_to_spacy4": False,
            "rollback": "Keep the spaCy 3.8.14 lock and revert only the isolated spike artifacts.",
        },
        "baseline": _run_baseline(args.iterations),
        "candidate": (
            _probe_candidate(args.python_version)
            if args.probe_candidate
            else {"status": "not_probed", "candidate_version": CANDIDATE_VERSION}
        ),
        "matrix": [
            {"python": "3.12", "baseline": "measured", "candidate": "blocked_or_not_probed"},
            {"python": "3.13", "baseline": "compatibility_ci", "candidate": "not_probed"},
            {"python": "3.14", "baseline": "not_supported", "candidate": "not_supported"},
        ],
        "reproducibility": {
            "fixture": "src/nlp_policy_nz/xml_parser.py:SAMPLE_NZ_XML",
            "iterations": max(1, args.iterations),
            "candidate_requires_prerelease_allow": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote evidence to {args.output}")  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
