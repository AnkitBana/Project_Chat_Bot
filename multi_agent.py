"""
Multi-agent orchestration system (LangChain v1.x / LangGraph).
"""
from typing import Dict, Any, List, Optional
from enum import Enum
from agent import AIAgent


class AgentRole(Enum):
    RESEARCHER  = "researcher"
    ANALYST     = "analyst"
    WRITER      = "writer"
    CODER       = "coder"
    PLANNER     = "planner"
    CRITIC      = "critic"
    COORDINATOR = "coordinator"


_ROLE_PROMPTS: Dict[AgentRole, str] = {
    AgentRole.RESEARCHER: (
        "You are a Research agent. Search the web, verify facts, and compile "
        "thorough research reports. Cite your sources."
    ),
    AgentRole.ANALYST: (
        "You are an Analyst agent. Analyze data, identify patterns, provide "
        "data-driven insights and recommendations."
    ),
    AgentRole.WRITER: (
        "You are a Writer agent. Write clear, engaging, well-structured content. "
        "Adapt tone and style to the audience."
    ),
    AgentRole.CODER: (
        "You are a Coder agent. Write clean, efficient, well-documented code. "
        "Follow best practices and suggest improvements."
    ),
    AgentRole.PLANNER: (
        "You are a Planner agent. Create detailed plans, break down complex tasks, "
        "identify dependencies and risks."
    ),
    AgentRole.CRITIC: (
        "You are a Critic agent. Review work critically but constructively. "
        "Identify issues and provide actionable feedback."
    ),
    AgentRole.COORDINATOR: (
        "You are a Coordinator agent. Analyze complex tasks, break them into "
        "subtasks, assign to appropriate agents, and synthesize results."
    ),
}


class MultiAgentSystem:
    """Orchestrates multiple specialized AI agents."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None, verbose: bool = True):
        self.provider = provider
        self.model = model
        self.verbose = verbose
        self.agents: Dict[str, AIAgent] = {}
        self.coordinator = self._make_agent(AgentRole.COORDINATOR)

    def _make_agent(self, role: AgentRole, name: Optional[str] = None) -> AIAgent:
        return AIAgent(
            name=name or role.value.capitalize(),
            provider=self.provider,
            model=self.model,
            system_message=_ROLE_PROMPTS[role],
            verbose=self.verbose,
        )

    def get_agent(self, role: AgentRole) -> AIAgent:
        """Return (or lazily create) the agent for a given role."""
        if role.value not in self.agents:
            self.agents[role.value] = self._make_agent(role)
        return self.agents[role.value]

    def run_sequential(self, task: str, agent_sequence: List[AgentRole]) -> Dict[str, Any]:
        """Chain agents: each agent receives the previous agent's output as context."""
        outputs: Dict[str, str] = {}
        current_input = task
        for role in agent_sequence:
            agent = self.get_agent(role)
            if self.verbose:
                print(f"\n{'='*50}\nAgent: {agent.name}\n{'='*50}")
            output = agent.run(current_input)
            outputs[role.value] = output
            current_input = f"Previous agent ({role.value}) output:\n{output}\n\nOriginal task: {task}"
        return {"task": task, "sequence": [r.value for r in agent_sequence], "outputs": outputs}

    def run_parallel(self, task: str, agent_roles: List[AgentRole]) -> Dict[str, Any]:
        """Run all agents on the same task independently."""
        outputs: Dict[str, str] = {}
        for role in agent_roles:
            agent = self.get_agent(role)
            if self.verbose:
                print(f"\n{'='*50}\nAgent: {agent.name}\n{'='*50}")
            outputs[role.value] = agent.run(task)
        return {"task": task, "agents": [r.value for r in agent_roles], "outputs": outputs}

    def run_coordinated(self, task: str) -> str:
        """Coordinator orchestrates Researcher → Analyst → Writer, then synthesizes."""
        # Default pipeline
        results = self.run_sequential(
            task,
            [AgentRole.RESEARCHER, AgentRole.ANALYST, AgentRole.WRITER],
        )
        formatted = "\n".join(
            f"\n{role.upper()}:\n{out}" for role, out in results["outputs"].items()
        )
        synthesis_prompt = (
            f"Synthesize the following agent outputs into a final, comprehensive answer.\n\n"
            f"Original task: {task}\n\nAgent outputs:{formatted}"
        )
        return self.coordinator.run(synthesis_prompt)
