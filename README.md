# Nova AI Agent

> A production-ready AI agent chatbot with a modern Next.js UI, FastAPI backend, multi-provider LLM support, streaming SSE, RAG, guardrails, tracing, and multi-agent orchestration. Deployable for **free** on Render + Vercel.

---

## Table of Contents

1. [Features](#features)
2. [Architecture Overview](#architecture-overview)
3. [Project Structure](#project-structure)
4. [Quick Start — Local Dev](#quick-start--local-dev)
5. [Environment Variables](#environment-variables)
6. [Frontend (Next.js)](#frontend-nextjs)
7. [Backend (FastAPI)](#backend-fastapi)
8. [API Reference](#api-reference)
9. [LLM Providers & Models](#llm-providers--models)
10. [Built-in Tools](#built-in-tools)
11. [Enterprise Features](#enterprise-features)
12. [Multi-Agent System](#multi-agent-system)
13. [Python API](#python-api)
14. [How to Add a Custom Tool](#how-to-add-a-custom-tool)
15. [Deployment — Free (Render + Vercel)](#deployment--free-render--vercel)
16. [Docker & Docker Compose](#docker--docker-compose)
17. [Security & Red Team Audit](#security--red-team-audit)
18. [Troubleshooting](#troubleshooting)
19. [Tech Stack](#tech-stack)
20. [Roadmap](#roadmap)

---

## Features

| Category | What's included |
|---|---|
| **UI** | Next.js 16 + React 19, dark/light theme, ChatGPT-style layout |
| **Streaming** | Real-time SSE token streaming with animated cursor |
| **Auth** | JWT signup/login, bcrypt passwords, 24-hour tokens |
| **LLM Providers** | Google Gemini, OpenAI, Anthropic, ICA (4 providers) |
| **Model Switcher** | Switch models live from the sidebar — memory preserved |
| **Tools** | 11 built-in LangChain tools (web search, calculator, file I/O, etc.) |
| **RAG** | BM25 retrieval — no vector DB required |
| **Cache** | LRU response cache — instant answers for repeated questions |
| **Guardrails** | Blocks prompt injection, shell cmds, destructive ops |
| **HITL** | Human-in-the-loop approval for sensitive operations |
| **Tracing** | Full JSONL audit log per request |
| **Multi-Agent** | 7-role orchestration (Researcher, Coder, Writer, Analyst…) |
| **File Upload** | PDF, DOCX, images, CSV, JSON via drag & drop |
| **Export** | Save chat as `.docx` Word document |
| **Docker** | Multi-stage Dockerfiles for both frontend and backend |

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│              Browser — Next.js 16 (port 3000)            │
│  /          Chat page (streaming SSE, markdown render)   │
│  /login     JWT login                                    │
│  /signup    Account creation                             │
└────────────────────────┬─────────────────────────────────┘
                         │  HTTP REST + SSE
                         │  NEXT_PUBLIC_API_URL
┌────────────────────────▼─────────────────────────────────┐
│             FastAPI Backend (port 8000)                   │
│  Auth · Chat · Stream · Models · RAG · Upload · Export   │
└────────────────────────┬─────────────────────────────────┘
                         │
          ┌──────────────▼──────────────┐
          │      AIAgent  (agent.py)    │
          │                             │
          │  1. Guardrails check        │
          │  2. Cache lookup            │
          │  3. RAG context inject      │
          │  4. LangGraph ReAct loop    │
          │  5. Trace & persist         │
          └──────────────┬──────────────┘
                         │
         ┌───────────────▼───────────────────────┐
         │          LLM Providers                │
         │  Google Gemini · OpenAI · Anthropic   │
         └───────────────────────────────────────┘
                         │ tool calls
         ┌───────────────▼───────────────────────┐
         │           11 LangChain Tools          │
         │  web_search · calculate · read_file   │
         │  wikipedia · news · api_call · …      │
         └───────────────────────────────────────┘
```

---

## Project Structure

```
project_Agent/
│
├── 🤖 Backend (Python / FastAPI)
│   ├── server.py              # 24+ REST endpoints, auth, streaming, CORS
│   ├── agent.py               # AIAgent — ReAct loop, guardrails, cache, RAG, tracing
│   ├── agent_optimized.py     # Lightweight single-use agent
│   ├── llm_provider.py        # LLM factory (Google / OpenAI / Anthropic / ICA)
│   ├── config.py              # Pydantic settings loaded from .env
│   ├── memory_manager.py      # Conversation memory with JSON persistence
│   ├── memory_and_planning.py # PersistentAgent + PlanningAgent
│   ├── multi_agent.py         # 7-role multi-agent orchestration
│   ├── tools.py               # Core tools (web search, file ops, API, calc)
│   ├── tools_extra.py         # Extended tools (Wikipedia, news, summarize)
│   ├── cache.py               # LRU response cache (200 entries, disk persist)
│   ├── guardrails.py          # Security policy engine + HITL approvals
│   ├── tracer.py              # JSONL audit log per request
│   ├── rag.py                 # BM25 retrieval — no vector DB needed
│   ├── redteam.py             # Automated attack suite (14 test vectors)
│   ├── benchmark.py           # Model accuracy + latency benchmarking
│   ├── main.py                # CLI entry point (demo / single / multi)
│   ├── Dockerfile             # Python 3.13 slim container
│   ├── docker-compose.yml     # backend + frontend + redis
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # All env vars documented
│
├── 🌐 Frontend (Next.js 16 / TypeScript)
│   └── nova-ui/
│       ├── src/app/
│       │   ├── page.tsx           # Chat page — streaming, suggestions, export
│       │   ├── layout.tsx         # Root layout — ThemeProvider, hljs CDN
│       │   ├── globals.css        # CSS variables, dark/light, markdown, code blocks
│       │   ├── login/page.tsx     # Login form
│       │   └── signup/page.tsx    # Signup form
│       ├── src/components/
│       │   ├── Sidebar.tsx        # Model list, tools, settings, theme toggle, user row
│       │   ├── MessageList.tsx    # User/assistant bubbles, stream cursor, copy
│       │   ├── InputBox.tsx       # Auto-resize textarea, Enter/Shift+Enter
│       │   └── Toast.tsx          # Toast notifications
│       ├── src/lib/
│       │   ├── api.ts             # All API calls + SSE stream reader
│       │   ├── markdown.ts        # Custom markdown renderer with hljs
│       │   └── theme.tsx          # ThemeContext — dark/light + localStorage
│       ├── next.config.ts         # standalone output + dev proxy to :8000
│       ├── Dockerfile             # Multi-stage Node 20 Alpine build
│       └── package.json
│
├── 📂 Data (auto-created)
│   ├── data/users.json            # User accounts (replace with DB for prod)
│   ├── data/agent_settings.json   # Persisted agent config
│   ├── data/last_working_model.txt
│   ├── data/uploads/              # Uploaded files
│   └── logs/traces.jsonl          # Audit log
│
└── 📂 Static (legacy — not served)
    └── static/                    # Old HTML UI — kept but not served
```

---

## Quick Start — Local Dev

### Prerequisites

- Python 3.10+ (3.13 recommended)
- Node.js 18+
- At least one LLM API key (Google Gemini has a [free tier](https://aistudio.google.com))

### 1. Clone & set up Python

```bash
git clone https://github.com/YOUR_USERNAME/nova-agent.git
cd nova-agent

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — add at least one API key (GOOGLE_API_KEY is free)
```

### 3. Start the backend

```bash
python server.py
# FastAPI running on http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

### 4. Start the frontend

```bash
cd nova-ui
npm install
npm run dev
# Next.js running on http://localhost:3000
```

### 5. Open the app

Navigate to **http://localhost:3000**, sign up for an account, and start chatting.

> The dev proxy in `next.config.ts` forwards all `/api/*` requests from port 3000 to port 8000 automatically — no manual CORS config needed in development.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

```env
# ── LLM Providers (add at least one) ──────────────────────
GOOGLE_API_KEY=AIza...          # Free tier at aistudio.google.com
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# ── Default provider & model ───────────────────────────────
DEFAULT_LLM_PROVIDER=google
GOOGLE_MODEL=gemini-2.5-flash-lite
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_MODEL=claude-3-5-haiku-20241022

# ── Generation ─────────────────────────────────────────────
TEMPERATURE=0.3      # 0.0=deterministic, 0.7=creative, 1.0=wild
MAX_TOKENS=2048      # 2048=concise, 4096=long-form, 8192=max

# ── Auth ───────────────────────────────────────────────────
SECRET_KEY=          # Leave empty = auto-generated (set a fixed value in prod)

# ── Production (fill in after deploying) ──────────────────
# FRONTEND_URL=https://your-app.vercel.app   ← add to Render after Vercel deploy

# ── ICA (IBM Consulting Advantage) — non-functional ────────
# ICA_API_KEY=ak_...       # Requires browser SSO — direct API calls blocked
# ICA_BASE_URL=https://agentstudio.servicesessentials.ibm.com/v1
```

---

## Frontend (Next.js)

The frontend lives in `nova-ui/` and is a full Next.js 16 App Router application.

### Pages

| Route | Description |
|---|---|
| `/` | Main chat page — protected by JWT auth guard |
| `/login` | Login form — stores JWT in `localStorage` |
| `/signup` | Signup form — creates account + auto-login |

### Key Components

**`Sidebar.tsx`**
- Model list grouped by provider (Google / OpenAI / Anthropic / ICA)
- 🔒 lock icon on providers without a configured API key
- Active model highlighted; click to switch live (memory preserved)
- Tools list loaded from `/api/status`
- Settings tab: Agent Name, System Prompt, Temperature slider, Max Tokens slider
- Theme toggle (dark ↔ light), user avatar + logout

**`MessageList.tsx`**
- User bubbles (right-aligned) and assistant bubbles (left with N avatar)
- Live streaming bubble with animated `▌` cursor
- Tool-use badges displayed above assistant reply
- Copy button per message
- Auto-scroll to bottom

**`InputBox.tsx`**
- Auto-resize textarea (up to 180px)
- `Enter` to send, `Shift+Enter` for newline
- Send button disables while streaming

**`markdown.ts`**
- Custom renderer — no external markdown lib
- `normalizeStream()` collapses soft-wrap `\n` tokens while preserving code blocks
- Headings, bold/italic, tables, lists, blockquotes, horizontal rules, inline code
- Fenced code blocks with language label + copy button
- Syntax highlighting via `highlight.js` (loaded from CDN)

**`api.ts`**
- All fetch calls go through `apiFetch()` which auto-attaches `Authorization: Bearer` header
- `streamChat()` reads the SSE stream line by line and fires callbacks for `token` / `tool` / `done` / `error` events
- `NEXT_PUBLIC_API_URL` env var sets the backend base URL (falls back to `http://localhost:8000`)

### Theme

CSS variables defined in `globals.css` — just toggle `data-theme="light"` on `<html>`:

```css
:root               { --bg: #212121; --text: #ececec; … }  /* dark (default) */
:root[data-theme="light"] { --bg: #ffffff; --text: #1a1a1a; … }
```

---

## Backend (FastAPI)

`server.py` is the entire backend. It runs on port 8000 with Uvicorn.

### Auth System

- Users stored in `data/users.json` (replace with PostgreSQL for large-scale prod)
- Passwords hashed with **bcrypt**
- **JWT** tokens (HS256, 24-hour expiry)
- All protected endpoints use `Depends(get_current_user)`

### Agent Instance

A single `AIAgent` instance is shared across all requests (thread-safe via asyncio executor). The last working model is cached in `data/last_working_model.txt` — on startup, the server validates the saved model's API key still exists before using it.

### Streaming

`POST /api/chat/stream` returns `text/event-stream`. Each event is:
```json
{"type": "token", "data": "Hello"}
{"type": "tool",  "data": "Using tool: web_search..."}
{"type": "done",  "data": "5"}
{"type": "error", "data": "Rate limit exceeded"}
```

---

## API Reference

### Auth

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/signup` | — | Create account → returns JWT |
| POST | `/api/auth/login` | — | Login → returns JWT |
| GET | `/api/auth/me` | ✓ | Get current user info |

### Chat

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/chat` | — | Non-streaming chat (compatibility) |
| POST | `/api/chat/stream` | — | **SSE streaming** (main endpoint) |
| POST | `/api/clear` | — | Clear memory + cache |
| GET | `/api/history` | — | Full conversation history |

### Models

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/models` | — | List available models + which providers have keys |
| POST | `/api/models/switch` | — | Switch provider/model live |
| GET | `/api/status` | — | Current provider, model, tools, turn count |

### Agent Settings

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/agent/settings` | — | Get current agent config |
| POST | `/api/agent/settings` | — | Update name, temperature, max tokens, system prompt |

### Files

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/upload` | ✓ | Upload file (PDF, DOCX, image, CSV, JSON — max 20MB) |
| GET | `/api/uploads/{filename}` | — | Serve uploaded file |
| POST | `/api/export/docx` | — | Export chat messages as `.docx` |

### RAG

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/rag/ingest` | — | Add text to knowledge base |
| GET | `/api/rag/stats` | — | Document count |

### Observability

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/traces` | — | Last 20 request traces |
| GET | `/api/traces/stats` | — | Latency, tool call counts, cache hit rate |
| GET | `/api/cache` | — | Cache stats |

### Guardrails & HITL

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/guardrails` | — | View security rules |
| GET | `/api/hitl/pending` | — | Requests waiting for human approval |
| POST | `/api/hitl/resolve` | — | Approve or reject a HITL request |
| POST | `/api/redteam/run` | — | Run full red team security audit |

**Interactive docs:** `http://localhost:8000/docs`

---

## LLM Providers & Models

| Provider | Models | Free? |
|---|---|---|
| **Google Gemini** | `gemini-2.5-flash-lite`, `gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-flash-latest`, `gemini-3-flash-preview` | ✅ Free tier (best option) |
| **OpenAI** | `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo` | ❌ Pay-per-token |
| **Anthropic** | `claude-3-5-haiku-20241022`, `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229` | ❌ Pay-per-token |
| **ICA** | `gpt-5.2`, Llama, Granite, Mistral | ⛔ Requires IBM SSO (non-functional) |

**Switching models** — live from the UI sidebar, or via API:
```bash
curl -X POST http://localhost:8000/api/models/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "google", "model": "gemini-2.5-flash"}'
```

**Automatic fallback** — on 429 quota errors the agent retries with exponential backoff and falls back to the next available model automatically.

---

## Built-in Tools

| Tool | Description |
|---|---|
| `web_search` | DuckDuckGo web search |
| `wikipedia_search` | Wikipedia article lookup |
| `news_search` | Latest news on any topic |
| `read_file` | Read TXT / JSON files from disk |
| `write_file` | Write files to disk |
| `scrape_webpage` | Extract plain text from any URL |
| `api_call` | HTTP GET / POST to external APIs |
| `calculate` | Safe math expression evaluator |
| `get_current_time` | Current date and time |
| `summarize_local_file` | Read + word/line stats on a file |
| `list_directory` | List files in a folder |

The agent uses **ReAct reasoning** — it decides which tool to call based on the question, calls it, reads the result, and reasons again until it has a final answer.

---

## Enterprise Features

### Response Cache

- LRU cache (200 entries), persisted to `data/cache.json`
- Normalizes questions so `"What is 2+2?"` and `"what is 2 + 2"` hit the same entry
- Cache hit → instant reply (< 1ms), no LLM call
- Cache stats: `GET /api/cache`

### Guardrails & Human-in-the-Loop (HITL)

The guardrails engine (`guardrails.py`) runs **before** every LLM call:

| Action | Triggers |
|---|---|
| **Block** | Prompt injection attempts, shell commands (`rm`, `del`, `exec`), `/etc/passwd`, system file access |
| **HITL Pause** | Financial transactions, bulk file operations, destructive operations |

Approve or reject paused requests:
```bash
curl -X POST http://localhost:8000/api/hitl/resolve \
  -H "Content-Type: application/json" \
  -d '{"rule_id": "rule_xyz", "approved": true}'
```

### Tracing & Observability

Every request generates a trace with:
- Input message + session ID
- Cache hit / miss
- Tool calls made + their results
- LLM call with model name
- Errors (if any)
- Final reply + total latency

Traces written to `logs/traces.jsonl` and available via `GET /api/traces`.

### Agentic RAG

BM25 keyword retrieval — no external vector database required:

```bash
# Ingest text via API
curl -X POST http://localhost:8000/api/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{"text": "Our refund policy is 30 days.", "source": "policy"}'
```

Retrieved context is automatically injected into the LLM system prompt. Stored in `data/rag_store.json`.

### Automatic Quota Recovery

1. On a `429` rate-limit error → exponential backoff (1s, 2s, 4s, 8s, …)
2. If all retries fail → auto-switch to the next available model
3. Successful model saved to `data/last_working_model.txt` for next startup

---

## Multi-Agent System

`multi_agent.py` provides 7 specialized roles:

| Role | Responsibility |
|---|---|
| **Coordinator** | Plans and orchestrates all other agents |
| **Researcher** | Web search and fact gathering |
| **Analyst** | Data analysis and insights |
| **Writer** | Content creation and documentation |
| **Coder** | Code writing and review |
| **Planner** | Step-by-step planning |
| **Critic** | Quality review and feedback |

**Execution modes:**

```python
from multi_agent import MultiAgentSystem, AgentRole

system = MultiAgentSystem()

# Run agents in sequence
result = system.run_sequential(
    "Research Python 3.13 and write a summary",
    [AgentRole.RESEARCHER, AgentRole.WRITER]
)

# Run agents in parallel
result = system.run_parallel(
    "Analyze this dataset",
    [AgentRole.ANALYST, AgentRole.CRITIC]
)

# Auto-orchestrated by Coordinator
result = system.run_coordinated("Analyze AI market trends and write a report")
```

---

## Python API

### Basic Agent

```python
from agent import AIAgent

agent = AIAgent(name="Nova", provider="google")
response = agent.run("What is the capital of France?")
print(response)
```

### Agent with Custom Settings

```python
agent = AIAgent(
    name="CodeBot",
    provider="google",
    model="gemini-2.5-flash",
    temperature=0.0,       # deterministic for code
    max_tokens=4096,
    system_message="You are an expert Python engineer. Always include type hints.",
)
```

### Persistent Memory Agent

```python
from memory_and_planning import PersistentAgent

agent = PersistentAgent(resume=True)  # loads last session from disk
agent.run("My name is Alice")
agent.run("What's my name?")          # remembers: Alice
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

### RAG — Add Documents

```python
from rag import get_rag
from agent import AIAgent

rag = get_rag()
rag.ingest_text("Our refund policy is 30 days.", source="policy")
rag.ingest_file("docs/company_faq.txt")

agent = AIAgent()
agent.run("What is the refund policy?")  # context injected automatically
```

### Benchmark Models

```bash
python benchmark.py --provider google
python benchmark.py --provider openai
```

---

## How to Add a Custom Tool

No changes to `agent.py` needed — just 3 steps.

### Step 1 — Define the tool

```python
# tools_custom.py
from langchain_core.tools import tool

@tool
def stock_price(ticker: str) -> str:
    """Get the current stock price for a ticker symbol like AAPL or GOOGL."""
    import requests
    resp = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}")
    data = resp.json()
    price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
    return f"{ticker}: ${price:.2f}"
```

> The `@tool` decorator uses the **function name** as the tool name and the **docstring** as the description the LLM reads to decide when to call it. Write clear, specific docstrings.

### Step 2 — Register in `get_tools()`

```python
# tools.py — bottom of file
from tools_custom import stock_price

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
# Agent calls stock_price("AAPL") and returns the result
```

**Tips:**
- Keep each tool **focused on one thing** — they compose well
- Always return a **plain string** — the LLM reads it directly
- Include **units and context** (`"$189.42"` not `189.42`)
- Catch all exceptions and return a human-readable error string

---

## Deployment — Free (Render + Vercel)

Deploy the full stack for **$0/month** using Render (backend) and Vercel (frontend).

```
GitHub
  │
  ├──► Render.com  (FastAPI, free Docker hosting, 750 hrs/month)
  │       URL: https://nova-agent.onrender.com
  │
  └──► Vercel.com  (Next.js, free hobby tier, always on)
          URL: https://nova-ui.vercel.app
```

> ⚠️ Render free tier **sleeps after 15 min of inactivity** — first request takes ~30s. Upgrade to $7/mo to keep it always-on.

### Step 1 — Push to GitHub

```bash
git add -A
git commit -m "ready for deployment"
git remote add origin https://github.com/YOUR_USERNAME/nova-agent.git
git push -u origin main
```

### Step 2 — Deploy backend → Render

1. Go to [render.com](https://render.com) → **Sign up free** with GitHub
2. **New → Web Service** → Connect your repo
3. Settings:
   - **Root Directory:** `.` (repo root)
   - **Runtime:** Docker (auto-detected from `Dockerfile`)
   - **Branch:** `main`
4. Add **Environment Variables:**
   ```
   GOOGLE_API_KEY         = AIza...
   DEFAULT_LLM_PROVIDER   = google
   GOOGLE_MODEL           = gemini-2.5-flash-lite
   SECRET_KEY             = any_random_32_char_string
   FRONTEND_URL           = https://your-app.vercel.app   ← fill after step 3
   ```
5. Click **Deploy**. Your backend URL: `https://nova-agent.onrender.com`

### Step 3 — Deploy frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → **Sign up free** with GitHub
2. **Add New Project** → Import your repo
3. Set **Root Directory** to `nova-ui`
4. Add **Environment Variable:**
   ```
   NEXT_PUBLIC_API_URL = https://nova-agent.onrender.com
   ```
5. Click **Deploy**. Your frontend URL: `https://nova-ui.vercel.app`

### Step 4 — Wire them together

Go back to **Render → Environment** and update:
```
FRONTEND_URL = https://nova-ui.vercel.app
```
Click **Manual Deploy → Deploy latest**.

### Cost summary

| Service | Cost |
|---|---|
| Render free web service | **$0** |
| Vercel hobby plan | **$0** |
| Google Gemini free tier | **$0** |
| GitHub | **$0** |
| **Total** | **$0 / month** |

---

## Docker & Docker Compose

### Backend only

```bash
docker build -t nova-agent .
docker run -p 8000:8000 --env-file .env nova-agent
```

### Full stack (backend + frontend + Redis)

```bash
# Copy and fill in your API keys
cp .env.example .env

docker-compose up -d
```

Services started:
- **backend** — FastAPI on port 8000
- **frontend** — Next.js on port 3000 (`http://localhost:3000`)
- **redis** — Distributed LRU cache (256MB, AOF persistence)

```bash
docker-compose logs -f backend    # watch backend logs
docker-compose down               # stop everything
```

### Cloud — Google Cloud Run

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/nova-agent
gcloud run deploy nova-agent \
  --image gcr.io/PROJECT_ID/nova-agent \
  --platform managed \
  --set-env-vars GOOGLE_API_KEY=AIza...,FRONTEND_URL=https://... \
  --allow-unauthenticated
```

---

## Security & Red Team Audit

Run the automated attack suite to verify all guardrails hold:

```bash
python redteam.py
```

```
Prompt Injection    [###]  3/3  blocked
System File Access  [###]  3/3  blocked
Shell Injection     [##]   2/2  blocked
HITL Trigger        [###]  3/3  paused for approval
Safe Input          [###]  3/3  allowed through
Total: 14/14  (100% pass rate)
```

Or trigger via API (no restart needed):
```bash
curl -X POST http://localhost:8000/api/redteam/run
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `python` not found | Use full path: `C:\Python313\python.exe main.py` |
| `npm` not found | Install Node.js from [nodejs.org](https://nodejs.org) |
| 401 Invalid or expired token | Clear `localStorage` in browser DevTools and log in again |
| 401 Invalid API key | Check `.env` has a valid API key (no trailing spaces) |
| 429 Quota exceeded | Agent auto-retries + falls back to another model automatically |
| CORS errors in browser | Ensure `FRONTEND_URL` is set in backend `.env` and matches your Vercel URL |
| Port 8000 in use | Edit `server.py` → `uvicorn.run(..., port=8001)` |
| Slow first response (Render) | Free tier sleeps — wait 30s for cold start |
| Stale model crash on startup | Delete `data/last_working_model.txt` |
| Import errors | Re-run `pip install -r requirements.txt` inside your venv |
| Next.js hydration error | Clear browser cache or rebuild: `cd nova-ui && npm run build` |
| Export DOCX fails | Ensure `python-docx` is installed: `pip install python-docx` |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Agent Framework** | LangChain 0.3 + LangGraph |
| **LLM Providers** | Google Gemini · OpenAI · Anthropic |
| **Backend** | FastAPI + Uvicorn (async, SSE streaming) |
| **Frontend** | Next.js 16 · React 19 · TypeScript |
| **Auth** | JWT (python-jose) + bcrypt |
| **Markdown** | Custom renderer + highlight.js |
| **RAG / Retrieval** | BM25 (pure Python, no DB) |
| **Cache** | LRU in-memory + JSON persistence (Redis optional) |
| **Tracing** | Custom JSONL audit log |
| **Search** | DuckDuckGo (ddgs) |
| **Containerisation** | Docker + docker-compose |
| **Deployment** | Render (backend) · Vercel (frontend) |

---

## Agent Request Pipeline

Every message follows this path:

```
User Input
    │
    ▼
1. Guardrails ──► Block  (prompt injection / shell cmds / file access)
    │              Pause  (financial / bulk / destructive → HITL queue)
    ▼
2. Cache ────────► Cache hit → instant reply, skip LLM
    │
    ▼
3. RAG ──────────► BM25 retrieve relevant docs → inject into system prompt
    │
    ▼
4. LangGraph ────► ReAct reasoning loop
    │               LLM call → tool calls → observations → final answer
    │               Exponential backoff on 429
    │               Auto model fallback if all retries fail
    ▼
5. Persist ──────► memory.add_message() · cache.set() · tracer.finish()
    │
    ▼
Reply (streamed as SSE tokens to browser)
```

---

## Roadmap

- [x] SSE streaming responses in Next.js UI
- [x] JWT authentication (signup / login)
- [x] Model switcher — live switch without restart
- [x] Dark / light theme
- [x] File upload (PDF, DOCX, images, CSV)
- [x] Export chat as Word document
- [x] Redis distributed cache support
- [x] Red team security audit (100% pass rate)
- [x] Docker + docker-compose
- [x] Free deployment guide (Render + Vercel)
- [ ] Conversation history panel (list past chats)
- [ ] Image input / vision support
- [ ] Observability dashboard (trace viewer in UI)
- [ ] Local models via Ollama
- [ ] Plugin system for custom tools
- [ ] Streaming tool-call progress in UI
- [ ] Multi-user workspace isolation

---

*Built with LangChain, LangGraph, FastAPI, Next.js, and Google Gemini.*
