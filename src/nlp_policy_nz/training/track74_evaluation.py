"""Track 74 held-out NZ legal/Hansard evaluation set helpers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal, cast

from nlp_policy_nz.training.eval import classification_prf, exact_match, token_f1

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TRACK74_MANIFEST_PATH = ROOT / "data" / "track74" / "held_out_evaluation_set.json"
DEFAULT_TRACK74_REPORT_PATH = ROOT / "data" / "track74" / "baseline_report.json"

Track74SourceKind = Literal["legislation", "hansard", "court_decision"]
Track74MetricKind = Literal["exact_match", "token_f1", "classification_accuracy"]


@dataclass(frozen=True, slots=True)
class Track74TrainingDocument:
    """One known training-pool document excluded from the held-out split."""

    source_id: str
    source_path: str
    source_kind: Track74SourceKind
    source_title: str
    document_version: str
    document_date: str
    source_hash: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready representation of the training document."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Track74EvaluationCase:
    """One held-out evaluation case with provenance and a baseline prediction."""

    case_id: str
    task: str
    source_id: str
    source_kind: Track74SourceKind
    source_path: str
    source_title: str
    document_version: str
    document_date: str
    source_hash: str
    split_reason: str
    metric_kind: Track74MetricKind
    prompt: str
    reference_answer: str
    baseline_prediction: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready representation of the evaluation case."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Track74EvaluationManifest:
    """Repo-side manifest for the held-out NZ legal/Hansard evaluation set."""

    track_id: str
    track_number: int
    status: str
    selection_rules: tuple[str, ...]
    promotion_threshold: float
    training_pool: tuple[Track74TrainingDocument, ...]
    held_out_cases: tuple[Track74EvaluationCase, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready manifest payload."""
        return {
            "track_id": self.track_id,
            "track_number": self.track_number,
            "status": self.status,
            "selection_rules": list(self.selection_rules),
            "promotion_threshold": self.promotion_threshold,
            "training_pool": [item.to_dict() for item in self.training_pool],
            "held_out_cases": [item.to_dict() for item in self.held_out_cases],
        }


@dataclass(frozen=True, slots=True)
class Track74CaseScore:
    """One scored Track 74 evaluation case."""

    case_id: str
    metric_kind: Track74MetricKind
    score: float
    reference_answer: str
    baseline_prediction: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready case score payload."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Track74EvaluationReport:
    """Repo-side baseline report for the held-out evaluation set."""

    manifest_track_id: str
    leakage_free: bool
    example_count: int
    task_scores: dict[str, float]
    overall_score: float
    promotion_threshold: float
    promotion_ready: bool
    case_scores: tuple[Track74CaseScore, ...]
    validation_errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready report payload."""
        return {
            "manifest_track_id": self.manifest_track_id,
            "leakage_free": self.leakage_free,
            "example_count": self.example_count,
            "task_scores": dict(sorted(self.task_scores.items())),
            "overall_score": self.overall_score,
            "promotion_threshold": self.promotion_threshold,
            "promotion_ready": self.promotion_ready,
            "case_scores": [item.to_dict() for item in self.case_scores],
            "validation_errors": list(self.validation_errors),
        }


def _hash_text(text: str) -> str:
    """Return a stable SHA-256 hash for a source text."""
    return sha256(text.encode("utf-8")).hexdigest()


def _repo_path(*parts: str) -> Path:
    """Return a workspace-relative path inside the repository."""
    return ROOT.joinpath(*parts)


def _read_text(path: Path) -> str:
    """Read UTF-8 text from *path*."""
    return path.read_text(encoding="utf-8")


def default_track74_training_pool() -> tuple[Track74TrainingDocument, ...]:
    """Return the repo-side training pool excluded from the held-out split."""
    legislation = _repo_path("data", "samples", "sample_legislation.txt")
    hansard = _repo_path("data", "samples", "sample_hansard.txt")
    axiomatic = _repo_path("tests", "fixtures", "axiom", "nz_source_section.txt")
    mleb = _repo_path("data", "track22", "nz_mleb_fixture.json")
    mleb_payload = json.loads(mleb.read_text(encoding="utf-8"))
    documents = [
        Track74TrainingDocument(
            source_id="train-legislation-sample",
            source_path=legislation.relative_to(ROOT).as_posix(),
            source_kind="legislation",
            source_title="Sample legislation fixture",
            document_version="fixture",
            document_date="2024-01-01",
            source_hash=_hash_text(_read_text(legislation)),
        ),
        Track74TrainingDocument(
            source_id="train-hansard-sample",
            source_path=hansard.relative_to(ROOT).as_posix(),
            source_kind="hansard",
            source_title="Sample Hansard fixture",
            document_version="fixture",
            document_date="2024-01-01",
            source_hash=_hash_text(_read_text(hansard)),
        ),
        Track74TrainingDocument(
            source_id="train-axiom-source-section",
            source_path=axiomatic.relative_to(ROOT).as_posix(),
            source_kind="legislation",
            source_title="Axiom source section fixture",
            document_version="fixture",
            document_date="2024-01-01",
            source_hash=_hash_text(_read_text(axiomatic)),
        ),
    ]
    for document in mleb_payload["documents"]:
        documents.append(
            Track74TrainingDocument(
                source_id=str(document["doc_id"]),
                source_path=mleb.relative_to(ROOT).as_posix(),
                source_kind=cast("Track74SourceKind", str(document["source_type"])),
                source_title=str(document["title"]),
                document_version=str(mleb_payload["schema_version"]),
                document_date="2024-01-01",
                source_hash=_hash_text(str(document["text"])),
            )
        )
    return tuple(documents)


def default_track74_evaluation_cases() -> tuple[Track74EvaluationCase, ...]:
    """Return the deterministic held-out evaluation cases."""
    return (
        Track74EvaluationCase(
            case_id="track74-case-01",
            task="classification",
            source_id="holdout-legislation-commencement",
            source_kind="legislation",
            source_path="data/track74/sources/legislation_commencement.txt",
            source_title="Held-out commencement clause",
            document_version="track74-holdout-v1",
            document_date="2026-06-01",
            source_hash=_hash_text(
                _read_text(_repo_path("data", "track74", "sources", "legislation_commencement.txt"))
            ),
            split_reason="Held out from the training pool to preserve commencement-detection evidence.",
            metric_kind="classification_accuracy",
            prompt="Classify whether this clause is about commencement or an operative duty.",
            reference_answer="commencement",
            baseline_prediction="commencement",
        ),
        Track74EvaluationCase(
            case_id="track74-case-02",
            task="stance",
            source_id="holdout-hansard-water-services",
            source_kind="hansard",
            source_path="data/track74/sources/hansard_water_services.txt",
            source_title="Held-out Hansard water services debate",
            document_version="track74-holdout-v1",
            document_date="2026-06-02",
            source_hash=_hash_text(
                _read_text(_repo_path("data", "track74", "sources", "hansard_water_services.txt"))
            ),
            split_reason="Reserved for stance and policy-position gating on Hansard text.",
            metric_kind="classification_accuracy",
            prompt="Classify the stance of the speech on water services reform.",
            reference_answer="support",
            baseline_prediction="neutral",
        ),
        Track74EvaluationCase(
            case_id="track74-case-03",
            task="retrieval",
            source_id="holdout-legislation-tikanga",
            source_kind="legislation",
            source_path="data/track74/sources/legislation_tikanga.txt",
            source_title="Held-out tikanga and public administration clause",
            document_version="track74-holdout-v1",
            document_date="2026-06-03",
            source_hash=_hash_text(
                _read_text(_repo_path("data", "track74", "sources", "legislation_tikanga.txt"))
            ),
            split_reason="Reserved for retrieval and citation-search gating without reuse of fixture text.",
            metric_kind="exact_match",
            prompt="Retrieve the key phrase describing tikanga and public administration.",
            reference_answer="recognise tikanga Māori and provide for public administration",
            baseline_prediction="recognise tikanga Māori and provide for public administration",
        ),
        Track74EvaluationCase(
            case_id="track74-case-04",
            task="extraction",
            source_id="holdout-hansard-treaty",
            source_kind="hansard",
            source_path="data/track74/sources/hansard_treaty.txt",
            source_title="Held-out Treaty principles Hansard debate",
            document_version="track74-holdout-v1",
            document_date="2026-06-04",
            source_hash=_hash_text(
                _read_text(_repo_path("data", "track74", "sources", "hansard_treaty.txt"))
            ),
            split_reason="Reserved for extraction-style evaluation on Treaty principles.",
            metric_kind="token_f1",
            prompt="Extract the core treaty-principles phrase from the speech.",
            reference_answer="partnership protection and participation",
            baseline_prediction="partnership and protection",
        ),
    )


def default_track74_manifest() -> Track74EvaluationManifest:
    """Return the default Track 74 held-out evaluation manifest."""
    return Track74EvaluationManifest(
        track_id="track74_nz_legal_hansard_evaluation_set_20260704",
        track_number=74,
        status="planned",
        selection_rules=(
            "Hold out NZ legislation and Hansard examples from the repo-side fixture pool.",
            "Keep source-path, source-hash, version, date, and split reason for every case.",
            "Reject any case whose hash overlaps the explicitly enumerated training pool.",
            "Use one stable baseline prediction per case so CI can compare future models deterministically.",
        ),
        promotion_threshold=0.75,
        training_pool=default_track74_training_pool(),
        held_out_cases=default_track74_evaluation_cases(),
    )


def validate_track74_manifest(
    manifest: Track74EvaluationManifest,
) -> tuple[bool, tuple[str, ...]]:
    """Return whether the manifest is leakage-free and structurally valid."""
    errors: list[str] = []
    training_hashes = {item.source_hash for item in manifest.training_pool}
    seen_case_ids: set[str] = set()
    seen_source_ids: set[str] = set()
    for item in manifest.held_out_cases:
        if item.case_id in seen_case_ids:
            errors.append(f"duplicate case id: {item.case_id}")
        seen_case_ids.add(item.case_id)
        if item.source_id in seen_source_ids:
            errors.append(f"duplicate source id: {item.source_id}")
        seen_source_ids.add(item.source_id)
        if not item.source_hash:
            errors.append(f"missing hash for case {item.case_id}")
        if item.source_hash in training_hashes:
            errors.append(f"leakage detected for case {item.case_id}")
        source_path = _repo_path(*Path(item.source_path).parts)
        if not source_path.is_file():
            errors.append(f"missing source file for case {item.case_id}: {item.source_path}")
            continue
        if _hash_text(_read_text(source_path)) != item.source_hash:
            errors.append(f"source hash mismatch for case {item.case_id}")
    return (not errors, tuple(errors))


def score_track74_case(case: Track74EvaluationCase) -> Track74CaseScore:
    """Score one Track 74 case deterministically."""
    if case.metric_kind == "exact_match":
        score = exact_match(case.baseline_prediction, case.reference_answer)
    elif case.metric_kind == "token_f1":
        score = token_f1(case.baseline_prediction.split(), case.reference_answer.split())
    else:
        metrics = classification_prf([case.baseline_prediction], [case.reference_answer])
        score = metrics["accuracy"]
    return Track74CaseScore(
        case_id=case.case_id,
        metric_kind=case.metric_kind,
        score=round(score, 4),
        reference_answer=case.reference_answer,
        baseline_prediction=case.baseline_prediction,
    )


def evaluate_track74_manifest(
    manifest: Track74EvaluationManifest,
) -> Track74EvaluationReport:
    """Evaluate the held-out set against the repo-side baseline predictions."""
    leakage_free, errors = validate_track74_manifest(manifest)
    case_scores = tuple(score_track74_case(case) for case in manifest.held_out_cases)
    task_buckets: dict[str, list[float]] = {}
    for case, score in zip(manifest.held_out_cases, case_scores, strict=True):
        task_buckets.setdefault(case.task, []).append(score.score)
    task_scores = {
        task: round(sum(values) / len(values), 4) for task, values in sorted(task_buckets.items())
    }
    overall_score = round(sum(score.score for score in case_scores) / len(case_scores), 4)
    promotion_ready = leakage_free and overall_score >= manifest.promotion_threshold
    return Track74EvaluationReport(
        manifest_track_id=manifest.track_id,
        leakage_free=leakage_free,
        example_count=len(manifest.held_out_cases),
        task_scores=task_scores,
        overall_score=overall_score,
        promotion_threshold=manifest.promotion_threshold,
        promotion_ready=promotion_ready,
        case_scores=case_scores,
        validation_errors=errors,
    )


def render_track74_manifest_json(manifest: Track74EvaluationManifest | None = None) -> str:
    """Return the Track 74 manifest as formatted JSON."""
    resolved = manifest or default_track74_manifest()
    return json.dumps(resolved.to_dict(), indent=2, ensure_ascii=False) + "\n"


def render_track74_report_json(
    report: Track74EvaluationReport | None = None,
) -> str:
    """Return the Track 74 baseline report as formatted JSON."""
    resolved = report or evaluate_track74_manifest(default_track74_manifest())
    return json.dumps(resolved.to_dict(), indent=2, ensure_ascii=False) + "\n"


def render_track74_report_markdown(
    report: Track74EvaluationReport | None = None,
) -> str:
    """Return a concise Track 74 evaluation summary as Markdown."""
    resolved = report or evaluate_track74_manifest(default_track74_manifest())
    lines = [
        "# Track 74 Evaluation",
        "",
        f"- Leakage free: {resolved.leakage_free}",
        f"- Example count: {resolved.example_count}",
        f"- Overall score: {resolved.overall_score:.4f}",
        f"- Promotion threshold: {resolved.promotion_threshold:.4f}",
        f"- Promotion ready: {resolved.promotion_ready}",
        "",
        "## Task Scores",
        "",
    ]
    lines.extend(f"- {task}: {score:.4f}" for task, score in resolved.task_scores.items())
    if resolved.validation_errors:
        lines.extend(["", "## Validation Errors", ""])
        lines.extend(f"- {error}" for error in resolved.validation_errors)
    return "\n".join(lines) + "\n"
