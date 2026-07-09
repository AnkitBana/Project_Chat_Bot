"""
Tracing & Observability — logs every agent decision, tool call, and outcome.
Provides an auditable trail for every action the agent takes.
"""
import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class EventType(str, Enum):
    USER_INPUT     = "user_input"
    CACHE_HIT      = "cache_hit"
    LLM_CALL       = "llm_call"
    TOOL_CALL      = "tool_call"
    TOOL_RESULT    = "tool_result"
    GUARDRAIL_DENY = "guardrail_deny"
    HITL_PAUSE     = "hitl_pause"       # Human-in-the-loop pause
    HITL_APPROVE   = "hitl_approve"
    HITL_REJECT    = "hitl_reject"
    FINAL_REPLY    = "final_reply"
    ERROR          = "error"


class Trace:
    """Single agent run trace — one trace per user message."""

    def __init__(self, session_id: str, user_input: str):
        self.trace_id   = str(uuid.uuid4())[:8]
        self.session_id = session_id
        self.user_input = user_input
        self.started_at = datetime.now().isoformat()
        self.ended_at: Optional[str] = None
        self.events: List[Dict[str, Any]] = []
        self.final_reply: Optional[str] = None
        self.total_ms: Optional[int] = None
        self._start_ts = datetime.now().timestamp()

        self._log(EventType.USER_INPUT, {"message": user_input})

    def log(self, event_type: EventType, data: Dict[str, Any] = {}):
        self._log(event_type, data)

    def finish(self, reply: str):
        self.final_reply = reply
        self.ended_at    = datetime.now().isoformat()
        self.total_ms    = int((datetime.now().timestamp() - self._start_ts) * 1000)
        self._log(EventType.FINAL_REPLY, {"reply": reply[:200], "total_ms": self.total_ms})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id":   self.trace_id,
            "session_id": self.session_id,
            "user_input": self.user_input,
            "started_at": self.started_at,
            "ended_at":   self.ended_at,
            "total_ms":   self.total_ms,
            "event_count": len(self.events),
            "events":     self.events,
        }

    def _log(self, event_type: EventType, data: Dict[str, Any]):
        self.events.append({
            "ts":   datetime.now().isoformat(),
            "type": event_type.value,
            **data,
        })


class Tracer:
    """
    Collects traces and persists them to disk.
    Keeps last 500 traces in memory for the dashboard.
    """

    MAX_IN_MEMORY = 500
    LOG_PATH      = "./logs/traces.jsonl"

    def __init__(self):
        os.makedirs("./logs", exist_ok=True)
        self._traces: List[Trace] = []

    def start(self, session_id: str, user_input: str) -> Trace:
        t = Trace(session_id, user_input)
        self._traces.append(t)
        if len(self._traces) > self.MAX_IN_MEMORY:
            self._traces.pop(0)
        return t

    def finish(self, trace: Trace, reply: str):
        trace.finish(reply)
        self._persist(trace)

    def get_recent(self, n: int = 20) -> List[Dict]:
        return [t.to_dict() for t in reversed(self._traces[-n:])]

    def get_stats(self) -> Dict[str, Any]:
        finished = [t for t in self._traces if t.total_ms is not None]
        avg_ms   = int(sum(t.total_ms for t in finished) / len(finished)) if finished else 0
        tool_calls = sum(
            sum(1 for e in t.events if e["type"] == EventType.TOOL_CALL)
            for t in self._traces
        )
        cache_hits = sum(
            sum(1 for e in t.events if e["type"] == EventType.CACHE_HIT)
            for t in self._traces
        )
        return {
            "total_traces":  len(self._traces),
            "avg_latency_ms": avg_ms,
            "tool_calls":    tool_calls,
            "cache_hits":    cache_hits,
        }

    def _persist(self, trace: Trace):
        try:
            with open(self.LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(trace.to_dict()) + "\n")
        except Exception:
            pass


# ── Module singleton ──────────────────────────────────────────────────────────
_tracer = Tracer()

def get_tracer() -> Tracer:
    return _tracer
