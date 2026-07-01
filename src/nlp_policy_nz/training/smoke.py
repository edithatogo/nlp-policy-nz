"""Tiny CPU training smoke tests for Track 20."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

from nlp_policy_nz.training.runtime import TrainingExecutionPlan, choose_training_execution_plan

if TYPE_CHECKING:
    from collections.abc import Sequence


DEFAULT_SMOKE_TEXTS: tuple[str, ...] = (
    "The Minister must consult the authority.",
    "A person may apply for a licence.",
    "No agency must disclose protected information.",
    "Te Tiriti principles guide the decision.",
)


@dataclass(frozen=True)
class SmokeTrainingResult:
    """Result from a bounded local Track 20 smoke-training run."""

    backend: str
    device: str
    records_seen: int
    steps_run: int
    initial_loss: float
    final_loss: float
    loss_decreased: bool
    ci_safe: bool

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible result."""
        return asdict(self)


def run_cpu_mlm_smoke_training(
    *,
    plan: TrainingExecutionPlan | None = None,
    texts: Sequence[str] = DEFAULT_SMOKE_TEXTS,
    seed: int = 42,
) -> SmokeTrainingResult:
    """Run a tiny deterministic MLM-style training loop on CPU."""
    selected = plan or choose_training_execution_plan()
    if selected.device != "cpu":
        raise ValueError("CPU smoke training requires a CPU execution plan")
    if not selected.smoke_test:
        raise ValueError("CPU smoke training requires a smoke-test execution plan")
    if selected.blockers:
        raise ValueError(f"Execution plan has blockers: {selected.blockers}")

    import torch

    torch.manual_seed(seed)
    token_ids, vocab_size = _encode_texts(tuple(texts)[: selected.max_records])
    if not token_ids:
        raise ValueError("At least one non-empty smoke-training text is required")

    model = torch.nn.Sequential(
        torch.nn.Embedding(vocab_size, 8),
        torch.nn.Linear(8, vocab_size),
    )
    optimizer = torch.optim.SGD(model.parameters(), lr=0.2)
    losses: list[float] = []
    max_steps = max(1, selected.max_steps)

    input_ids = torch.tensor(
        [token for row in token_ids for token in row[:-1]],
        dtype=torch.long,
    )
    target_ids = torch.tensor(
        [token for row in token_ids for token in row[1:]],
        dtype=torch.long,
    )

    for _ in range(max_steps):
        logits = model(input_ids)
        loss = torch.nn.functional.cross_entropy(logits, target_ids)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach().item()))

    return SmokeTrainingResult(
        backend=selected.backend,
        device=selected.device,
        records_seen=min(len(texts), selected.max_records),
        steps_run=max_steps,
        initial_loss=losses[0],
        final_loss=losses[-1],
        loss_decreased=losses[-1] <= losses[0],
        ci_safe=selected.ci_safe,
    )


def render_smoke_training_json(
    *,
    plan: TrainingExecutionPlan | None = None,
    texts: Sequence[str] = DEFAULT_SMOKE_TEXTS,
) -> str:
    """Render a CPU smoke-training result as JSON."""
    result = run_cpu_mlm_smoke_training(plan=plan, texts=texts)
    return json.dumps(result.to_dict(), indent=2, sort_keys=True)


def main() -> int:
    """Run the environment-selected CPU smoke training path."""
    sys.stdout.write(f"{render_smoke_training_json()}\n")
    return 0


def _encode_texts(texts: Sequence[str]) -> tuple[list[list[int]], int]:
    """Tokenize texts into integer ids for the tiny smoke objective."""
    tokenized = [[token.casefold().strip(".,;:") for token in text.split()] for text in texts]
    vocab = {"<pad>": 0}
    for row in tokenized:
        for token in row:
            if token and token not in vocab:
                vocab[token] = len(vocab)
    encoded = [[vocab[token] for token in row if token] for row in tokenized]
    return [row for row in encoded if len(row) >= 2], len(vocab)


if __name__ == "__main__":
    raise SystemExit(main())
