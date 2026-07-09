"""
FastAPI backend for the AI Agent web interface.
Run with: python server.py
"""
import sys
import os
import asyncio
sys.stdout.reconfigure(encoding="utf-8")

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from agent import AIAgent
from config import setup_directories, settings

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(title="AI Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_directories()
os.makedirs("static", exist_ok=True)

# ── Agent instance (one per server, shared) ──────────────────────────────────
_agent: Optional[AIAgent] = None

def get_agent() -> AIAgent:
    global _agent
    if _agent is None:
        # Use the last known working model if saved
        model = _load_working_model()
        _agent = AIAgent(name="Nova", verbose=False, model=model)
    return _agent

# ── Persist the last working model across requests ───────────────────────────
_WORKING_MODEL_FILE = "./data/last_working_model.txt"

def _save_working_model(model: str):
    try:
        with open(_WORKING_MODEL_FILE, "w") as f:
            f.write(model)
    except Exception:
        pass

def _load_working_model() -> Optional[str]:
    try:
        if os.path.exists(_WORKING_MODEL_FILE):
            return open(_WORKING_MODEL_FILE).read().strip() or None
    except Exception:
        pass
    return None

# ── Request / Response models ─────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    turns: int

class StatusResponse(BaseModel):
    provider: str
    model: str
    tools: list
    turns: int

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/api/status", response_model=StatusResponse)
async def status():
    agent = get_agent()
    info = agent.get_info()
    return {
        "provider": info["provider"],
        "model":    agent.llm.model_name if hasattr(agent.llm, "model_name") else info["model"],
        "tools":    info["tools"],
        "turns":    info["memory_stats"]["turns"],
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Non-streaming fallback — kept for compatibility."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    agent = get_agent()
    loop = asyncio.get_event_loop()
    reply = await loop.run_in_executor(None, agent.run, req.message.strip())
    current_model = agent.llm.model if hasattr(agent.llm, "model") else None
    if current_model:
        _save_working_model(current_model)
    return {"reply": reply, "turns": agent.memory.get_stats()["turns"]}


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    Server-Sent Events streaming endpoint.
    Runs guardrails + cache synchronously, then streams LLM tokens.
    Each SSE event is JSON: {"type": "token"|"done"|"error", "data": "..."}
    """
    import json as _json
    from guardrails import get_guardrails, GuardrailViolation
    from cache import get_cache
    from tracer import get_tracer, EventType

    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    msg = req.message.strip()
    agent = get_agent()

    async def event_generator():
        tracer     = get_tracer()
        guardrails = get_guardrails()
        cache      = get_cache()
        trace      = tracer.start(agent.memory.session_id, msg)

        def sse(event_type: str, data: str) -> str:
            return f"data: {_json.dumps({'type': event_type, 'data': data})}\n\n"

        try:
            # ── Guardrails (instant, no streaming needed) ──────────────────
            try:
                hitl_req = guardrails.check(msg)
                if hitl_req:
                    trace.log(EventType.HITL_PAUSE, {"rule_id": hitl_req.rule_id})
                    reply = (
                        f"This request requires human approval.\n\n"
                        f"**Reason:** {hitl_req.reason}"
                    )
                    yield sse("token", reply)
                    yield sse("done", str(agent.memory.get_stats()["turns"]))
                    tracer.finish(trace, reply)
                    return
            except GuardrailViolation as gv:
                trace.log(EventType.GUARDRAIL_DENY, {"rule_id": gv.rule_id})
                reply = f"Blocked: {gv.reason}"
                yield sse("token", reply)
                yield sse("done", str(agent.memory.get_stats()["turns"]))
                tracer.finish(trace, reply)
                return

            # ── Cache hit (instant, stream as single token) ────────────────
            cached = cache.get(msg)
            if cached:
                trace.log(EventType.CACHE_HIT, {"preview": cached[:60]})
                reply = f"{cached}\n\n*(instant reply from cache)*"
                # Stream word-by-word for a nicer effect
                for word in reply.split(" "):
                    yield sse("token", word + " ")
                    await asyncio.sleep(0.01)
                yield sse("done", str(agent.memory.get_stats()["turns"]))
                tracer.finish(trace, reply)
                return

            # ── LLM streaming ──────────────────────────────────────────────
            from rag import get_rag
            rag = get_rag()
            rag_context = rag.format_context(msg)
            from langchain_core.messages import HumanMessage, SystemMessage
            system = agent.system_message
            if rag_context:
                system = f"{agent.system_message}\n\n{rag_context}"

            messages = [SystemMessage(content=system)]
            messages.extend(agent.memory.get_messages())
            messages.append(HumanMessage(content=msg))

            trace.log(EventType.LLM_CALL, {"model": getattr(agent.llm, "model", "?")})

            full_reply = ""
            # Stream tokens via astream_events
            async for event in agent._graph.astream_events(
                {"messages": messages}, version="v2"
            ):
                kind = event.get("event", "")
                # Chat model streaming token
                if kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk:
                        token = ""
                        if hasattr(chunk, "content"):
                            c = chunk.content
                            if isinstance(c, str):
                                token = c
                            elif isinstance(c, list):
                                token = " ".join(
                                    p.get("text", "") for p in c if isinstance(p, dict)
                                )
                        if token:
                            full_reply += token
                            yield sse("token", token)
                # Tool call notification
                elif kind == "on_tool_start":
                    tool_name = event.get("name", "tool")
                    yield sse("tool", f"Using tool: {tool_name}...")

            # Persist to memory + cache
            if full_reply:
                agent.memory.add_message(msg, full_reply)
                cache.set(msg, full_reply)
                tracer.finish(trace, full_reply)
                model = getattr(agent.llm, "model", None)
                if model:
                    _save_working_model(model)

            yield sse("done", str(agent.memory.get_stats()["turns"]))

        except Exception as e:
            trace.log(EventType.ERROR, {"error": str(e)[:200]})
            tracer.finish(trace, f"Error: {e}")
            yield sse("error", str(e)[:300])
            yield sse("done", "0")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

# ── Model switcher ────────────────────────────────────────────────────────────
class SwitchModelRequest(BaseModel):
    provider: str
    model: str

AVAILABLE_MODELS = {
    "google": [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-flash-latest",
        "gemini-3-flash-preview",
    ],
    "openai": [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-3.5-turbo",
    ],
    "anthropic": [
        "claude-3-5-haiku-20241022",
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
    ],
}

@app.get("/api/models")
def list_models():
    from config import settings
    return {
        "current_provider": settings.default_llm_provider,
        "current_model": _load_working_model() or settings.google_model,
        "available": AVAILABLE_MODELS,
    }

@app.post("/api/models/switch")
def switch_model(req: SwitchModelRequest):
    global _agent
    if req.provider not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {req.provider}")
    if req.model not in AVAILABLE_MODELS[req.provider]:
        raise HTTPException(status_code=400, detail=f"Unknown model: {req.model}")
    try:
        # Rebuild agent with new provider/model, keep existing memory
        old_memory = _agent.memory if _agent else None
        _agent = AIAgent(name="Nova", verbose=False, provider=req.provider, model=req.model)
        if old_memory:
            _agent.memory = old_memory   # preserve conversation history
        _save_working_model(req.model)
        return {"message": f"Switched to {req.provider} / {req.model}", "provider": req.provider, "model": req.model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear")
def clear():
    agent = get_agent()
    agent.clear_memory()
    from cache import get_cache
    get_cache().clear()
    return {"message": "Memory and cache cleared"}

@app.get("/api/cache")
def cache_stats():
    from cache import get_cache
    return get_cache().stats()

@app.get("/api/history")
def history():
    agent = get_agent()
    msgs = agent.memory.get_messages()
    result = []
    for m in msgs:
        role = "user" if m.__class__.__name__ == "HumanMessage" else "assistant"
        result.append({"role": role, "content": m.content})
    return {"history": result}

# ── Tracing ───────────────────────────────────────────────────────────────────
@app.get("/api/traces")
def traces():
    from tracer import get_tracer
    return {"traces": get_tracer().get_recent(20)}

@app.get("/api/traces/stats")
def trace_stats():
    from tracer import get_tracer
    return get_tracer().get_stats()

# ── RAG ───────────────────────────────────────────────────────────────────────
class IngestRequest(BaseModel):
    text: str
    source: str = "manual"

@app.post("/api/rag/ingest")
def rag_ingest(req: IngestRequest):
    from rag import get_rag
    result = get_rag().ingest_text(req.text, req.source)
    return {"message": result}

@app.get("/api/rag/stats")
def rag_stats():
    from rag import get_rag
    return get_rag().get_stats()

# ── Guardrails & HITL ─────────────────────────────────────────────────────────
@app.get("/api/guardrails")
def guardrail_rules():
    from guardrails import get_guardrails
    return get_guardrails().get_all_rules()

@app.get("/api/hitl/pending")
def hitl_pending():
    from guardrails import get_guardrails
    return {"pending": get_guardrails().get_pending_hitl()}

class HITLResolve(BaseModel):
    rule_id: str
    approved: bool

@app.post("/api/hitl/resolve")
def hitl_resolve(req: HITLResolve):
    from guardrails import get_guardrails
    ok = get_guardrails().resolve_hitl(req.rule_id, req.approved)
    return {"resolved": ok, "approved": req.approved}

# ── Red Team ──────────────────────────────────────────────────────────────────
@app.post("/api/redteam/run")
async def redteam_run():
    """Run full red team security audit and return the report."""
    loop = asyncio.get_event_loop()
    from redteam import run_redteam
    report = await loop.run_in_executor(None, lambda: run_redteam(verbose=False))
    return report

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*50)
    print("  AI Agent Web Interface")
    print("="*50)
    print("  Open: http://localhost:8000")
    print("  Stop: Ctrl+C")
    print("="*50 + "\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
