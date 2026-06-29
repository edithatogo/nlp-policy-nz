"""Dispatch the next Conductor task to Cline and mark it complete on success."""

from __future__ import annotations

import re
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

import yaml


def load_yaml(path: str | Path) -> object | None:
    """Load a YAML file from `path`."""
    with Path(path).open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_text(path: str | Path) -> str:
    """Load UTF-8 text from `path`."""
    with Path(path).open(encoding="utf-8") as f:
        return f.read()


def write_text(path: str | Path, content: str) -> None:
    """Write UTF-8 text to `path`."""
    with Path(path).open("w", encoding="utf-8") as f:
        f.write(content)


def get_next_task(plan_content: str) -> str | None:
    """Return the description of the next incomplete task in the plan."""
    # Matches lines like: - [ ] Task X: <Description>
    # Or: ### [ ] Task X: <Description>
    match = re.search(r"-\s*\[\s*\]\s*Task(?:\s+\d+\.\d+)?:?\s+(.*)", plan_content, re.IGNORECASE)
    if not match:
        match = re.search(r"-\s*\[\s*\]\s*(.*)", plan_content)
    return match.group(1).strip() if match else None


def mark_task_complete(plan_content: str, task_description: str) -> tuple[str, bool]:
    """Mark `task_description` complete in `plan_content`."""
    # Replaces - [ ] Task ... with - [x] Task ...
    escaped = re.escape(task_description)
    pattern = rf"-\s*\[\s*\]\s*(Task(?:\s+\d+\.\d+)?:?\s+)?{escaped}"
    replacement = r"- [x] \1" + task_description
    new_content, count = re.subn(pattern, replacement, plan_content, flags=re.IGNORECASE)
    return new_content, count > 0


def run_task_via_cline(
    task: str,
    agent_name: str,
    prompt_instructions: str,
    model: str,
) -> bool:
    """Run the next task through Cline and stream its output."""
    full_prompt = f"Role: {agent_name}\nInstructions:\n{prompt_instructions}\n\nTask:\n{task}"

    cmd = [
        "cline",
        "--model", model,
        "--auto-approve", "true",
        "--json",
        full_prompt
    ]

    # Run the command and print live outputs
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )
    if process.stdout is None:
        raise RuntimeError("Cline did not provide a stdout stream")
    for _line in process.stdout:
        pass
    process.wait()
    return process.returncode == 0


def main() -> None:
    """Run the swarm dispatcher workflow."""
    config_path = Path("subagents.yaml")
    plan_path = Path("task_plan.md")

    if not config_path.exists() or not plan_path.exists():
        sys.exit(1)

    config = load_yaml(config_path)
    plan_content = load_text(plan_path)

    # Map agents by name for quick lookup
    agents: dict[str, Mapping[str, object]] = {}
    if isinstance(config, Mapping):
        subagents = config.get("subagents")
        if isinstance(subagents, list):
            for agent in subagents:
                if isinstance(agent, Mapping):
                    name = agent.get("name")
                    if isinstance(name, str):
                        agents[name] = agent

    # Find next task in task_plan.md
    next_task = get_next_task(plan_content)
    if not next_task:
        sys.exit(0)

    # Infer owner/agent name from the task context
    # Standard format: Track X has Owner: <name>
    # We parse the section header in task_plan.md
    task_idx = plan_content.find(next_task)
    header_section = plan_content[:task_idx]
    owner_match = re.findall(r"Owner\s*:\s*`([^`]+)`", header_section)
    owner = owner_match[-1] if owner_match else "Env_Architect"

    agent = agents.get(owner)
    if not agent:
        sys.exit(1)

    prompt_instructions_obj = agent.get("prompt")
    prompt_instructions = prompt_instructions_obj if isinstance(prompt_instructions_obj, str) else ""
    model_obj = agent.get("model", "auto-gemini-3")
    model = model_obj if isinstance(model_obj, str) else "auto-gemini-3"
    if model == "auto-gemini-3" or "gemini" in model:
        # Override to user requested SOTA model for Cline
        model = "deepseek-v4-flash"

    success = run_task_via_cline(next_task, owner, prompt_instructions, model)

    if success:
        new_plan, updated = mark_task_complete(plan_content, next_task)
        if updated:
            write_text(plan_path, new_plan)
            # Commit the progress
            subprocess.run(["git", "add", "task_plan.md"], check=False)
            subprocess.run(
                ["git", "commit", "-m", f"chore(swarm): Mark task '{next_task}' as complete"],
                check=False,
            )
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
