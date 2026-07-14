"""
Core AI Agent using LangGraph's create_react_agent (LangChain v1.x).
Enterprise features: ReAct reasoning, RAG, tracing, guardrails, HITL, caching.
"""
import time
import random
from typing import Optional, List, Dict, Any
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from llm_provider import LLMProvider
from memory_manager import MemoryManager
from tools import get_tools
from config import setup_directories
from cache import get_cache
from tracer import get_tracer, EventType
from guardrails import get_guardrails, GuardrailViolation
from rag import get_rag

# Models to try in order if quota is exceeded
GOOGLE_FALLBACK_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
]


class AIAgent:
    """
    AI Agent with tool use and conversation memory.
    Uses LangGraph's create_react_agent under the hood.
    """

    def __init__(
        self,
        name: str = "Assistant",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        system_message: Optional[str] = None,
        tools: Optional[List] = None,
        verbose: bool = True,
    ):
        setup_directories()

        self.name = name
        self.verbose = verbose

        # LLM
        self.llm = LLMProvider.get_llm(
            provider=provider, model=model, temperature=temperature
        )

        # Memory
        self.memory = MemoryManager()

        # Tools
        self.tools = tools if tools is not None else get_tools()

        # System prompt
        self.system_message = system_message or (
            f"You are {self.name}, a highly capable AI assistant.\n"
            "You can help with ANY task — including but not limited to:\n"
            "  • Writing, editing, summarising, and translating text\n"
            "  • Answering questions on any topic (science, history, math, law, medicine, etc.)\n"
            "  • Writing and reviewing code in ANY programming language "
            "(Python, C#, Java, JavaScript, C++, Go, Rust, SQL, TypeScript, etc.)\n"
            "  • Data analysis, statistics, and calculations\n"
            "  • Creative writing, brainstorming, and ideation\n"
            "  • Planning, task breakdown, and project management\n"
            "  • Web search, file operations, API calls, and web scraping (via tools)\n"
            "\n"
            "## Formatting rules (always follow these)\n"
            "- Use clear markdown: headings (##), bullet points, numbered lists, bold for key terms.\n"
            "- When writing CODE always use a fenced code block with the correct language tag, e.g.\n"
            "  ```csharp\n"
            "  // code here\n"
            "  ```\n"
            "- For multiple code examples, number each one with a heading (### 1. Title) and put the code block directly below it.\n"
            "- Keep each code example focused and under 40 lines — do not pad with boilerplate.\n"
            "- Add a SHORT one-sentence description above each example; never write long paragraphs of explanation unless the user asks.\n"
            "- When the user asks for N examples, return exactly N — no more, no less.\n"
            "- Never output raw triple-backticks without a language tag.\n"
            "- Never refuse a task because of language, framework, or subject matter.\n"
            "\n"
            "Think step-by-step. Use tools when real-time data or file access is needed."
        )

        # Create the agent graph (stateless — we pass history manually)
        self._graph = create_react_agent(self.llm, self.tools)

    @staticmethod
    def _extract_text(content) -> str:
        """Extract plain text from a message content (handles list or string)."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = [c.get("text", "") if isinstance(c, dict) else str(c) for c in content]
            return " ".join(p for p in parts if p).strip()
        return str(content)

    def _best_response(self, messages: list) -> str:
        """
        Return the best text response from the message list.
        Some lite models return an empty final AIMessage after tool calls —
        in that case fall back to the last non-empty message content.
        """
        for msg in reversed(messages):
            text = self._extract_text(msg.content).strip()
            if text:
                return text
        return ""

    def _is_quota_error(self, e: Exception) -> bool:
        """Check if exception is a rate limit / quota error."""
        msg = str(e).lower()
        return "429" in msg or "resource_exhausted" in msg or "rate limit" in msg or "quota" in msg

    def _invoke_with_backoff(self, messages: list, max_retries: int = 4) -> dict:
        """
        Invoke the agent graph with exponential backoff on 429 errors.
        Also tries fallback Google models if all retries fail.
        """
        from config import settings

        for attempt in range(max_retries):
            try:
                return self._graph.invoke({"messages": messages})
            except Exception as e:
                if not self._is_quota_error(e):
                    raise  # Non-quota errors bubble up immediately

                if attempt < max_retries - 1:
                    wait = (2 ** attempt) + random.uniform(0, 1)
                    print(f"  [Rate limit] Waiting {wait:.1f}s before retry {attempt + 1}/{max_retries - 1}...")
                    time.sleep(wait)
                else:
                    # All retries exhausted — try fallback models if using Google
                    if settings.default_llm_provider == "google":
                        return self._invoke_with_fallback_models(messages)
                    raise

        raise RuntimeError("All retries exhausted")

    def _invoke_with_fallback_models(self, messages: list) -> dict:
        """Try each Google fallback model in order."""
        from config import settings
        current = settings.google_model
        for model in GOOGLE_FALLBACK_MODELS:
            if model == current:
                continue  # already tried this one
            try:
                print(f"  [Fallback] Trying model: {model}")
                self.llm = LLMProvider.get_llm(provider="google", model=model)
                self._graph = create_react_agent(self.llm, self.tools)
                return self._graph.invoke({"messages": messages})
            except Exception as e:
                if self._is_quota_error(e):
                    print(f"  [Fallback] {model} also quota-exceeded, trying next...")
                    continue
                raise
        raise RuntimeError(
            "All Google models are quota-exceeded. "
            "Please wait until tomorrow or add billing at https://aistudio.google.com"
        )

    def run(self, user_input: str) -> str:
        """
        Enterprise agent run():
        1. Guardrails check  (block/HITL)
        2. Cache lookup      (instant reply if hit)
        3. RAG context       (augment prompt with retrieved docs)
        4. LLM call          (with backoff + fallback)
        5. Tracing           (full audit log)
        """
        tracer     = get_tracer()
        guardrails = get_guardrails()
        cache      = get_cache()
        rag        = get_rag()
        trace      = tracer.start(self.memory.session_id, user_input)

        try:
            # ── Step 1: Guardrails ───────────────────────────────────────────
            try:
                hitl_req = guardrails.check(user_input)
                if hitl_req:
                    trace.log(EventType.HITL_PAUSE, {"rule_id": hitl_req.rule_id, "reason": hitl_req.reason})
                    reply = (
                        f"This request requires human approval before proceeding.\n\n"
                        f"**Reason:** {hitl_req.reason}\n\n"
                        f"An administrator has been notified. "
                        f"Please confirm via the `/api/hitl/approve` endpoint."
                    )
                    tracer.finish(trace, reply)
                    return reply
            except GuardrailViolation as gv:
                trace.log(EventType.GUARDRAIL_DENY, {"rule_id": gv.rule_id, "reason": gv.reason, "severity": gv.severity})
                reply = f"Request blocked by security policy.\n\n**Reason:** {gv.reason}"
                tracer.finish(trace, reply)
                return reply

            # ── Step 2: Cache lookup (use as reference, not exact reply) ─────
            cached = cache.get(user_input)

            # ── Step 3: RAG context augmentation ────────────────────────────
            rag_context = rag.format_context(user_input)
            system = self.system_message
            if rag_context:
                system = f"{self.system_message}\n\n{rag_context}"
                trace.log(EventType.LLM_CALL, {"rag_context_chars": len(rag_context)})
            if cached:
                trace.log(EventType.CACHE_HIT, {"preview": cached[:80]})
                if self.verbose:
                    print("  [Cache] Hit — using as reference context")
                system = (
                    f"{system}\n\n"
                    f"[Previous answer for reference — rephrase naturally, do not repeat verbatim]:\n{cached}"
                )

            # ── Step 4: LLM call ─────────────────────────────────────────────
            trace.log(EventType.LLM_CALL, {"model": getattr(self.llm, "model", "?")})
            messages = [SystemMessage(content=system)]
            messages.extend(self.memory.get_messages())
            messages.append(HumanMessage(content=user_input))

            result = self._invoke_with_backoff(messages)
            output = self._best_response(result["messages"])

            # Count tool calls from the graph messages
            tool_calls = sum(
                1 for m in result["messages"]
                if m.__class__.__name__ == "ToolMessage"
            )
            if tool_calls:
                trace.log(EventType.TOOL_CALL, {"count": tool_calls})

            self.memory.add_message(user_input, output)
            cache.set(user_input, output)

            tracer.finish(trace, output)
            return output

        except Exception as e:
            trace.log(EventType.ERROR, {"error": str(e)[:200]})
            tracer.finish(trace, f"Error: {e}")
            error_msg = f"Error: {e}"
            if self.verbose:
                print(error_msg)
            return error_msg

    async def arun(self, user_input: str) -> str:
        """Async version of run."""
        messages = [SystemMessage(content=self.system_message)]
        messages.extend(self.memory.get_messages())
        messages.append(HumanMessage(content=user_input))

        try:
            result = await self._graph.ainvoke({"messages": messages})
            output = self._best_response(result["messages"])
            self.memory.add_message(user_input, output)
            return output
        except Exception as e:
            error_msg = f"Error: {e}"
            if self.verbose:
                print(error_msg)
            return error_msg

    def chat(self):
        """Start an interactive chat session."""
        print(f"\n{self.name}: Hello! How can I help you today?")
        print("(Type 'exit' to end)\n")
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print(f"\n{self.name}: Goodbye!")
                    break
                response = self.run(user_input)
                print(f"\n{self.name}: {response}\n")
            except KeyboardInterrupt:
                print(f"\n\n{self.name}: Goodbye!")
                break

    def clear_memory(self):
        self.memory.clear()

    def save_memory(self, filepath: Optional[str] = None):
        return self.memory.save(filepath)

    def load_memory(self, filepath: str):
        self.memory.load(filepath)

    def get_info(self) -> Dict[str, Any]:
        provider_info = LLMProvider.get_provider_info()
        return {
            "name": self.name,
            "provider": provider_info["provider"],
            "model": provider_info["model"],
            "memory_stats": self.memory.get_stats(),
            "tools": [t.name for t in self.tools],
        }
