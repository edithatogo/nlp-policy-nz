import sys
import os
import re
import yaml
import subprocess

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_text(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_next_task(plan_content):
    # Matches lines like: - [ ] Task X: <Description>
    # Or: ### [ ] Task X: <Description>
    match = re.search(r"-\s*\[\s*\]\s*Task(?:\s+\d+\.\d+)?:?\s+(.*)", plan_content, re.IGNORECASE)
    if not match:
        match = re.search(r"-\s*\[\s*\]\s*(.*)", plan_content)
    return match.group(1).strip() if match else None

def mark_task_complete(plan_content, task_description):
    # Replaces - [ ] Task ... with - [x] Task ...
    escaped = re.escape(task_description)
    pattern = rf"-\s*\[\s*\]\s*(Task(?:\s+\d+\.\d+)?:?\s+)?{escaped}"
    replacement = r"- [x] \1" + task_description
    new_content, count = re.subn(pattern, replacement, plan_content, flags=re.IGNORECASE)
    return new_content, count > 0

def run_task_via_cline(task, agent_name, prompt_instructions, model):
    full_prompt = f"Role: {agent_name}\nInstructions:\n{prompt_instructions}\n\nTask:\n{task}"
    print(f"\n[Swarm-Cline] Dispatching Task to {agent_name} using {model}:")
    print(f"  Task: {task}")
    
    cmd = [
        "cline",
        "--model", model,
        "--auto-approve", "true",
        "--json",
        full_prompt
    ]
    
    # Run the command and print live outputs
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', shell=True)
    for line in process.stdout:
        print(line, end="")
    process.wait()
    return process.returncode == 0

def main():
    config_path = "subagents.yaml"
    plan_path = "task_plan.md"
    
    if not os.path.exists(config_path) or not os.path.exists(plan_path):
        print(f"Error: Missing {config_path} or {plan_path} in current directory.")
        sys.exit(1)
        
    config = load_yaml(config_path)
    plan_content = load_text(plan_path)
    
    # Map agents by name for quick lookup
    agents = {a["name"]: a for a in config.get("subagents", [])}
    
    # Find next task in task_plan.md
    next_task = get_next_task(plan_content)
    if not next_task:
        print("[Swarm-Cline] All tasks in task_plan.md are completed!")
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
        print(f"Error: Agent '{owner}' not found in subagents.yaml")
        sys.exit(1)
        
    prompt_instructions = agent.get("prompt", "")
    model = agent.get("model", "auto-gemini-3")
    if model == "auto-gemini-3" or "gemini" in model:
        # Override to user requested SOTA model for Cline
        model = "deepseek-v4-flash"
        
    success = run_task_via_cline(next_task, owner, prompt_instructions, model)
    
    if success:
        print(f"\n[Swarm-Cline] Task successfully completed. Marking complete in task_plan.md...")
        new_plan, updated = mark_task_complete(plan_content, next_task)
        if updated:
            write_text(plan_path, new_plan)
            print("[Swarm-Cline] task_plan.md updated successfully.")
            # Commit the progress
            subprocess.run(["git", "add", "task_plan.md"])
            subprocess.run(["git", "commit", "-m", f"chore(swarm): Mark task '{next_task}' as complete"])
        sys.exit(0)
    else:
        print(f"\n[Swarm-Cline] Error: Cline task execution failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
