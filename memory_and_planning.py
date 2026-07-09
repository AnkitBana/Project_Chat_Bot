"""
Task 2: Persistent conversation memory + agent planning.

- PersistentMemory: saves/loads conversation across sessions
- PlanningAgent: breaks complex tasks into steps before executing
"""
import os
import json
from typing import Optional, List
from datetime import datetime
from agent import AIAgent
from tools import get_tools
from tools_extra import get_extra_tools


# ─── Persistent Memory ────────────────────────────────────────────────────────

MEMORY_DIR = "./data/memory"


def list_sessions() -> List[str]:
    """List all saved session files."""
    os.makedirs(MEMORY_DIR, exist_ok=True)
    return [f for f in os.listdir(MEMORY_DIR) if f.endswith(".json")]


def load_latest_session() -> Optional[str]:
    """Return path to the most recently modified session file, or None."""
    sessions = list_sessions()
    if not sessions:
        return None
    full_paths = [os.path.join(MEMORY_DIR, s) for s in sessions]
    return max(full_paths, key=os.path.getmtime)


class PersistentAgent(AIAgent):
    """
    AIAgent that automatically saves memory to disk after every turn
    and can reload a previous session on startup.
    """

    def __init__(self, session_id: Optional[str] = None, resume: bool = True, **kwargs):
        super().__init__(**kwargs)
        if resume:
            latest = load_latest_session()
            if latest:
                try:
                    self.memory.load(latest)
                    print(f"  [Memory] Resumed session: {os.path.basename(latest)} "
                          f"({self.memory.get_stats()['turns']} previous turns)")
                except Exception as e:
                    print(f"  [Memory] Could not load session: {e}")

    def run(self, user_input: str) -> str:
        output = super().run(user_input)
        # Auto-save after every turn
        try:
            self.memory.save()
        except Exception:
            pass
        return output


# ─── Planning Agent ───────────────────────────────────────────────────────────

class PlanningAgent:
    """
    Agent that:
    1. Breaks a complex task into numbered steps using the LLM
    2. Executes each step with a worker agent
    3. Returns a synthesized final answer
    """

    PLANNER_PROMPT = """You are a Planning agent. When given a complex task:
1. Break it into clear, numbered sub-steps (max 5 steps)
2. Each step should be a concrete, actionable instruction
3. Output ONLY the numbered list — no preamble or explanation

Example output:
1. Search the web for current data on X
2. Calculate Y from the data
3. Write a summary to output.txt"""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None, verbose: bool = True):
        self.verbose = verbose
        all_tools = get_tools() + get_extra_tools()

        self.planner = AIAgent(
            name="Planner",
            provider=provider,
            model=model,
            system_message=self.PLANNER_PROMPT,
            tools=[],          # planner only reasons, no tools
            verbose=False,
        )
        self.worker = AIAgent(
            name="Worker",
            provider=provider,
            model=model,
            tools=all_tools,   # worker has all tools
            verbose=verbose,
        )

    def run(self, task: str) -> str:
        """Plan then execute."""
        # Step 1: generate plan
        print(f"\n[Planner] Breaking down task...")
        plan_text = self.planner.run(
            f"Break this task into numbered steps:\n{task}"
        )
        print(f"\n[Plan]\n{plan_text}\n")

        # Step 2: execute each step
        steps = [
            line.strip()
            for line in plan_text.splitlines()
            if line.strip() and line.strip()[0].isdigit()
        ]

        if not steps:
            # No steps parsed — just run the task directly
            return self.worker.run(task)

        results = []
        for step in steps:
            if self.verbose:
                print(f"\n[Worker] Executing: {step}")
            result = self.worker.run(step)
            results.append(f"{step}\n-> {result}")

        # Step 3: synthesize
        synthesis_input = (
            f"Original task: {task}\n\nStep results:\n" +
            "\n\n".join(results) +
            "\n\nProvide a clear final answer summarizing all results."
        )
        final = self.worker.run(synthesis_input)
        return final
