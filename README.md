# Nova AI Agent System

A production-ready, enterprise-grade AI agent framework with a modern web interface, multi-provider LLM support, RAG, guardrails, tracing, and multi-agent orchestration.

---

## Quick Start

### 1. Set Up a Virtual Environment (Recommended)

Using a virtual environment keeps your dependencies isolated and avoids conflicts with other Python projects.

```bash
# Create virtual environment (Python 3.13)
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

> **Why?** Without a venv, `pip install` writes packages globally, which causes version conflicts across projects. Always use a venv for production-grade work.

### 2. Install & Configure

```bash
# Install dependencies
pip install -r requirements.txt

# Add your API key to .env
cp .env.example .env
# Edit .env → add GOOGLE_API_KEY or OPENAI_API_KEY
```

### 3. Run

```bash
# CLI modes
python main.py demo       # quick demo
python main.py single     # interactive chat
python main.py multi      # multi-agent mode

# Web UI
python server.py
# Open http://localhost:8000
```

---

## Project Structure

```
project_Agent/
│
├── 🤖 Core Agent
│   ├── agent.py               # Main AI agent (ReAct, RAG, cache, guardrails, tracing)
│   ├── agent_optimized.py     # Lightweight single-use agent
│   ├── multi_agent.py         # Multi-agent orchestration (7 roles)
│   ├── llm_provider.py        # Multi-provider LLM factory
│   ├── memory_manager.py      # Conversation memory (persist + load)
│   ├── memory_and_planning.py # PersistentAgent + PlanningAgent
│   └── config.py              # Settings from .env
│
├── 🛠️ Tools
│   ├── tools.py               # Core tools (web search, file ops, API, calc)
│   └── tools_extra.py         # Extended tools (Wikipedia, news, file summary)
│
├── 🏢 Enterprise Features
│   ├── cache.py               # LRU response cache (instant repeat answers)
│   ├── guardrails.py          # Security policy engine + HITL approvals
│   ├── tracer.py              # Full observability — audit log per request
│   └── rag.py                 # Agentic RAG — BM25 retrieval over documents
│
├── 🌐 Web Interface
│   ├── server.py              # FastAPI backend (19 endpoints)
│   └── static/index.html      # Dark UI — chat, model switcher, status sidebar
│
├── 📊 Utilities
│   ├── benchmark.py           # Model accuracy + latency benchmarking
│   ├── examples.py            # 10 usage examples
│   └── main.py                # CLI entry point
│
└── ⚙️ Config
    ├── .env.example           # Environment template
    ├── requirements.txt       # Python dependencies
    └── .gitignore
```

---

## Features

### Multi-Provider LLM Support
Switch between providers from the web UI or `.env`:

| Provider  | Models |
|-----------|--------|
| **Google**    | gemini-2.5-flash-lite, gemini-2.5-flash, gemini-2.0-flash, gemini-flash-latest |
| **OpenAI**    | gpt-4o-mini, gpt-4o, gpt-3.5-turbo |
| **Anthropic** | claude-3-5-haiku, claude-3-5-sonnet, claude-3-opus |

### Built-in Tools (11 total)

| Tool | Description |
|------|-------------|
| `web_search` | DuckDuckGo web search |
| `wikipedia_search` | Wikipedia lookup |
| `news_search` | Latest news on any topic |
| `read_file` | Read TXT / JSON files |
| `write_file` | Write files to disk |
| `scrape_webpage` | Extract text from URLs |
| `api_call` | HTTP GET / POST requests |
| `calculate` | Safe math expression evaluator |
| `get_current_time` | Current date and time |
| `summarize_local_file` | Read + stats on any local file |
| `list_directory` | List files in a folder |

### Enterprise Features

#### Response Cache
- LRU cache (200 entries, persists to disk)
- Normalizes questions — `"What is 2+2?"` and `"what is 2+2"` hit the same entry
- Instant replies for repeated questions
- Cache stats visible in the web UI sidebar

#### Guardrails & Human-in-the-Loop
- **Blocks** prompt injection, shell commands, system file access
- **Pauses** financial transactions, bulk operations, destructive file ops
- HITL approval via `/api/hitl/resolve`
- All violations logged to the tracer

#### Tracing & Observability
- Every request produces a trace with: user input, cache hit/miss, tool calls, LLM calls, errors, final reply, latency
- Traces persisted to `logs/traces.jsonl`
- REST endpoint: `GET /api/traces`

#### Agentic RAG
- BM25 retrieval — no external vector DB required
- Ingest any text or file via `POST /api/rag/ingest`
- Retrieved context automatically injected into LLM prompt
- Persists to `data/rag_store.json`

#### Automatic Quota Recovery
- Exponential backoff on 429 rate-limit errors
- Auto-fallback through all available models
- Last working model saved and reused on next startup

### Multi-Agent System

7 specialized agent roles that can be composed:

| Role | Responsibility |
|------|----------------|
| Coordinator | Plans and orchestrates other agents |
| Researcher | Web search and fact gathering |
| Analyst | Data analysis and insights |
| Writer | Content creation and documentation |
| Coder | Code writing and review |
| Planner | Step-by-step planning |
| Critic | Quality review and feedback |

**Execution modes:**
```python
system.run_sequential(task, [AgentRole.RESEARCHER, AgentRole.WRITER])
system.run_parallel(task, [AgentRole.ANALYST, AgentRole.CRITIC])
system.run_coordinated(task)   # auto-orchestrated
```

---

## Web Interface

Run `python server.py` and open `http://localhost:8000`.

**Features:**
- Dark modern UI
- Click suggestion chips to send example questions
- Model switcher — change provider/model without restarting
- Sidebar shows: provider, model, cached replies, cache hits, available tools
- Animated progress bar + status messages while agent is thinking
- Markdown rendering (bold, code blocks, lists)
- Clear conversation button

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web UI |
| GET | `/api/status` | Provider, model, tools, turns |
| POST | `/api/chat` | Send a message |
| POST | `/api/clear` | Clear memory + cache |
| GET | `/api/history` | Full conversation history |
| GET | `/api/models` | Available models |
| POST | `/api/models/switch` | Switch provider/model |
| GET | `/api/cache` | Cache stats |
| GET | `/api/traces` | Recent traces |
| GET | `/api/traces/stats` | Latency, tool calls, cache hits |
| POST | `/api/rag/ingest` | Add document to knowledge base |
| GET | `/api/rag/stats` | RAG document count |
| GET | `/api/guardrails` | View security rules |
| GET | `/api/hitl/pending` | Pending human approvals |
| POST | `/api/hitl/resolve` | Approve or reject HITL request |
| GET | `/docs` | Interactive Swagger API docs |

---

## Configuration

Edit `.env` to configure the agent:

```env
# Provider (openai | anthropic | google)
DEFAULT_LLM_PROVIDER=google

# API Keys — add at least one
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...

# Models
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_MODEL=claude-3-5-haiku-20241022
GOOGLE_MODEL=gemini-2.5-flash-lite

# Generation
TEMPERATURE=0.7
MAX_TOKENS=4096
```

---

## Python API

### Basic Agent
```python
from agent import AIAgent

agent = AIAgent(name="MyAgent", provider="google")
response = agent.run("What is the capital of France?")
print(response)
```

### Agent with Persistent Memory
```python
from memory_and_planning import PersistentAgent

agent = PersistentAgent(resume=True)   # loads last session
agent.run("My name is Alice")
agent.run("What's my name?")           # remembers Alice
```

### Planning Agent
```python
from memory_and_planning import PlanningAgent

agent = PlanningAgent()
result = agent.run("""
    Research Python 3.13 features,
    pick the top 3 for developers,
    and write a blog post to output.txt
""")
```

### Multi-Agent
```python
from multi_agent import MultiAgentSystem, AgentRole

system = MultiAgentSystem()
result = system.run_coordinated("Analyze AI market trends and write a report")
print(result)
```

### RAG — Add Documents
```python
from rag import get_rag

rag = get_rag()
rag.ingest_file("docs/company_policy.pdf")
rag.ingest_text("Our refund policy is 30 days.", source="policy")

# Agent automatically uses retrieved context
agent = AIAgent()
agent.run("What is the refund policy?")
```

### Benchmark Models
```bash
python benchmark.py --provider google
```

---

## Agent Request Pipeline

Every message goes through this pipeline:

```
User Input
    │
    ▼
1. Guardrails ──► Block (prompt injection / shell cmds)
    │              Pause (financial / bulk / destructive)
    ▼
2. Cache ────────► Instant reply if seen before (<1ms)
    │
    ▼
3. RAG ──────────► Retrieve relevant docs → inject into prompt
    │
    ▼
4. LLM Call ─────► ReAct reasoning + tool use
    │               Exponential backoff on 429
    │               Auto model fallback
    ▼
5. Tracer ───────► Log full audit trail to logs/traces.jsonl
    │
    ▼
Reply
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `python` not found | Use full path: `C:\Users\...\Python313\python.exe` |
| 401 Invalid API key | Check `.env` has a real API key |
| 429 Quota exceeded | Agent auto-retries + falls back to another model |
| Import errors | Run `pip install -r requirements.txt` |
| Port 8000 in use | Change port in `server.py` → `uvicorn.run(..., port=8001)` |
| Slow responses | Quota exhausted — agent retries automatically, or switch model in UI |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Agent Framework | LangChain 1.x + LangGraph |
| LLM Providers | OpenAI, Anthropic, Google Gemini |
| Web Backend | FastAPI + Uvicorn |
| Web Frontend | Vanilla HTML/CSS/JS (zero dependencies) |
| Vector Retrieval | BM25 (pure Python, no DB needed) |
| Cache | LRU in-memory + JSON persistence |
| Tracing | Custom JSONL audit log |
| Search | DuckDuckGo (ddgs) |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Browser                              │
│              http://localhost:8000  (index.html)                │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP REST
┌──────────────────────▼──────────────────────────────────────────┐
│                   FastAPI Server  (server.py)                   │
│  /api/chat  /api/models  /api/traces  /api/rag  /api/hitl  ...  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
          ┌────────────▼────────────┐
          │    AIAgent  (agent.py)  │
          │                        │
          │  1. Guardrails  ───────►│ guardrails.py
          │  2. Cache       ───────►│ cache.py
          │  3. RAG         ───────►│ rag.py
          │  4. LLM call    ───────►│ llm_provider.py
          │  5. Trace       ───────►│ tracer.py
          └────────┬───────────────┘
                   │
     ┌─────────────▼──────────────────────────────────┐
     │          LangGraph ReAct Loop                  │
     │                                                │
     │  LLM (Google / OpenAI / Anthropic)             │
     │      ▲               │                         │
     │      │    tool call  ▼                         │
     │      │   Tool Executor                         │
     │      │   web_search  wikipedia_search          │
     │      │   read_file   write_file   api_call     │
     │      │   calculate   news_search  + more       │
     │      └─── tool result ──────────────────────── │
     └────────────────────────────────────────────────┘
                   │
     ┌─────────────▼──────────────┐
     │     Memory Manager         │
     │     (memory_manager.py)    │
     │     JSON persistence       │
     └────────────────────────────┘
```

**Multi-Agent topology** (`multi_agent.py`):
```
         Coordinator
        /    |    \    \    \
Researcher Analyst Writer Coder Critic
```

---

## How to Add a Custom Tool

Adding a new tool takes 3 steps. No changes needed to `agent.py`.

### Step 1 — Define the function

```python
# In tools.py or a new file e.g. tools_custom.py
from langchain_core.tools import tool

@tool
def stock_price(ticker: str) -> str:
    """Get the current stock price for a ticker symbol like AAPL or GOOGL."""
    import requests
    resp = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}")
    data = resp.json()
    price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
    return f"{ticker}: ${price}"
```

> The `@tool` decorator uses the **function name** as the tool name and the **docstring** as the description the LLM reads to decide when to call it. Write clear, specific docstrings.

### Step 2 — Register it in `get_tools()`

```python
# tools.py — bottom of file
from tools_custom import stock_price   # import your tool

def get_tools() -> list:
    return [
        web_search, read_file, write_file, scrape_webpage,
        api_call, calculate, get_current_time,
        stock_price,   # ← add here
    ]
```

### Step 3 — Test it

```python
from agent import AIAgent

agent = AIAgent()
print(agent.run("What is the current stock price of AAPL?"))
# Agent automatically calls stock_price("AAPL") and returns the result
```

**Tips for writing good tools:**
- Keep each tool **focused on one thing** — they compose well
- Always return a **plain string** — the LLM reads the output directly
- Include **units and context** in the return value (`"$189.42"` not `189.42`)
- Catch exceptions and return a human-readable error string

---

## Deployment

### Docker (single container)
```bash
docker build -t nova-agent .
docker run -p 8000:8000 --env-file .env nova-agent
```

### Docker Compose (with Redis)
```bash
docker-compose up -d
# Opens http://localhost:8000 with Redis distributed cache
```

The Compose stack runs:
- **nova-agent** — FastAPI server on port 8000
- **redis** — Distributed LRU cache (256MB, LRU eviction, persistent AOF)

### Cloud (Google Cloud Run)
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/nova-agent
gcloud run deploy nova-agent \
  --image gcr.io/PROJECT_ID/nova-agent \
  --platform managed \
  --set-env-vars GOOGLE_API_KEY=... \
  --allow-unauthenticated
```

---

## Security — Red Team Audit

Run the automated attack suite to verify guardrails:

```bash
python redteam.py
```

Current results (14/14 — 100%):
```
Prompt Injection    [###]  3/3  blocked
System File Access  [###]  3/3  blocked
Shell Injection     [##]   2/2  blocked
HITL Trigger        [###]  3/3  paused for approval
Safe Input          [###]  3/3  allowed through
```

Or via API:
```bash
curl -X POST http://localhost:8000/api/redteam/run
```

---

## Tech Stack (Updated)

| Layer | Technology |
|-------|------------|
| Agent Framework | LangChain 1.x + LangGraph |
| LLM Providers | OpenAI, Anthropic, Google Gemini |
| Web Backend | FastAPI + Uvicorn (SSE streaming) |
| Web Frontend | Vanilla HTML/CSS/JS |
| Semantic Search | ChromaDB (hybrid BM25 + vector) |
| Cache | Redis (prod) / Local LRU (dev) |
| Tracing | Custom JSONL audit log |
| Security | Guardrails + Red Team test suite |
| Search | DuckDuckGo (ddgs) |
| Deployment | Docker + docker-compose |

---

## Roadmap

- [x] Streaming responses in the web UI
- [x] Redis distributed cache (with local LRU fallback)
- [x] Semantic vector search (ChromaDB hybrid RAG)
- [x] Red team security audit tool (100% pass rate)
- [x] Docker + docker-compose deployment
- [ ] File upload for RAG ingestion via UI
- [ ] Observability dashboard (trace viewer in UI)
- [ ] OAuth / login for multi-user support
- [ ] Support for local models via Ollama
- [ ] Plugin system for custom tools
- [ ] Multi-modal support (image input)

---

*Built with LangChain, LangGraph, FastAPI, and Google Gemini.*
