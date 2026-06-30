"""Evaluate Track 13 models against accepted silver labels when available."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from nlp_policy_nz.discourse.argument import ArgumentDetector
from nlp_policy_nz.discourse.stance import StanceClassifier
from nlp_policy_nz.training.eval import classification_prf

LABELS_PATH = Path("data/track13/silver_argument_labels.jsonl")
DISAGREEMENTS_PATH = Path("data/track13/silver_argument_disagreements.jsonl")
METRICS_PATH = Path("artifacts/track13/silver_eval_metrics.json")
REPORT_PATH = Path("artifacts/track13/silver_eval_report.md")


def main() -> int:
    """Run Track 13 silver evaluation and write metrics/report artifacts."""
    accepted = _load_jsonl(LABELS_PATH)
    disagreements = _load_jsonl(DISAGREEMENTS_PATH)
    metrics = {
        "track": 13,
        "evaluation_type": "silver",
        "status": "blocked_no_accepted_silver_labels" if not accepted else "evaluated",
        "accepted_silver_label_count": len(accepted),
        "disagreement_queue_count": len(disagreements),
        "accepted_metrics": _evaluate_rows(accepted) if accepted else None,
        "disagreement_diagnostic_metrics": _evaluate_rows(disagreements) if disagreements else None,
        "caveats": [
            "Accepted silver evaluation requires rows in data/track13/silver_argument_labels.jsonl.",
            "Current disagreement diagnostics are not acceptance evidence.",
            "No fine-tuned Legal-BERT Track 13 model artifact was loaded by this script.",
            "Stance diagnostics use relation_label as a pro/con/neutral proxy.",
        ],
    }
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(_render_report(metrics), encoding="utf-8")
    sys.stdout.write(
        json.dumps({"metrics": str(METRICS_PATH), "report": str(REPORT_PATH)}, indent=2)
    )
    sys.stdout.write("\n")
    return 0


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def _evaluate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    detector = ArgumentDetector()
    stance_classifier = StanceClassifier()
    claim_refs: list[str] = []
    claim_preds: list[str] = []
    premise_refs: list[str] = []
    premise_preds: list[str] = []
    relation_refs: list[str] = []
    relation_preds: list[str] = []
    stance_refs: list[str] = []
    stance_preds: list[str] = []

    for row in rows:
        text = str(row["text"])
        detected = {component.component_type for component in detector.detect(text)}
        claim_refs.append(_normalize_claim(str(row["claim_label"])))
        claim_preds.append("claim" if "conclusion" in detected else "non_argument")
        premise_refs.append(_normalize_premise(str(row["premise_label"])))
        premise_preds.append("premise" if "premise" in detected else "none")
        relation_refs.append(str(row["relation_label"]))
        relation_preds.append(
            "attack" if _has_attack_cue(text) else ("support" if "premise" in detected else "none")
        )
        stance_refs.append(_relation_to_stance(str(row["relation_label"])))
        stance_preds.append(stance_classifier.classify(text).stance)

    return {
        "rows": len(rows),
        "argument_claim": classification_prf(claim_preds, claim_refs),
        "argument_premise": classification_prf(premise_preds, premise_refs),
        "argument_relation": classification_prf(relation_preds, relation_refs),
        "stance_proxy": classification_prf(stance_preds, stance_refs),
    }


def _normalize_claim(label: str) -> str:
    return "claim" if label in {"claim", "major_claim"} else "non_argument"


def _normalize_premise(label: str) -> str:
    return "premise" if label in {"premise", "evidence"} else "none"


def _relation_to_stance(label: str) -> str:
    if label == "support":
        return "pro"
    if label == "attack":
        return "con"
    return "neutral"


def _has_attack_cue(text: str) -> bool:
    folded = text.casefold()
    return any(cue in folded for cue in ("oppose", "reject", "harmful", "despite", "do not apply"))


def _render_report(metrics: dict[str, Any]) -> str:
    accepted = metrics["accepted_metrics"]
    diagnostic = metrics["disagreement_diagnostic_metrics"]
    lines = [
        "# Track 13 Silver Evaluation",
        "",
        f"- Status: {metrics['status']}",
        f"- Accepted silver labels: {metrics['accepted_silver_label_count']}",
        f"- Disagreement queue rows: {metrics['disagreement_queue_count']}",
        "",
        "## Accepted Silver Evaluation",
        "",
    ]
    if accepted is None:
        lines.append(
            "No accepted silver labels are available, so the practical silver evaluation gate remains blocked."
        )
    else:
        lines.extend(_metric_lines(accepted))
    lines.extend(["", "## Disagreement Queue Diagnostic", ""])
    if diagnostic is None:
        lines.append("No disagreement rows are available.")
    else:
        lines.extend(_metric_lines(diagnostic))
    lines.extend(["", "## Caveats", ""])
    lines.extend(f"- {caveat}" for caveat in metrics["caveats"])
    return "\n".join(lines) + "\n"


def _metric_lines(metrics: dict[str, Any]) -> list[str]:
    return [
        f"- Rows: {metrics['rows']}",
        f"- Claim accuracy: {metrics['argument_claim']['accuracy']:.3f}",
        f"- Premise accuracy: {metrics['argument_premise']['accuracy']:.3f}",
        f"- Relation accuracy: {metrics['argument_relation']['accuracy']:.3f}",
        f"- Stance proxy accuracy: {metrics['stance_proxy']['accuracy']:.3f}",
    ]


if __name__ == "__main__":
    raise SystemExit(main())
