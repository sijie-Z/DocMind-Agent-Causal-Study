<p align="center">
  <strong>🇺🇸 English</strong> · <a href="README.md">🇨🇳 中文</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-v1.2.1-blue?logo=semver" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Vue_3-3.4-4FC08D?logo=vuedotjs" alt="Vue 3">
  <img src="https://img.shields.io/badge/DeepSeek-V4-8A2BE2" alt="DeepSeek">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="PRs Welcome">
</p>

<div align="center">
  <h1>🤖 DocMind</h1>
  <p><strong>PER-based Agentic RAG System</strong></p>
  <p>25+ Built-in Tools · Self-Improving · Observable · MCP Compatible</p>
  <p>
    <a href="https://sijie-z.github.io/DocMind-RAG/architecture.html">📊 Interactive Architecture</a> ·
    <a href="#-benchmark">📈 Benchmark</a> ·
    <a href="#-quick-start">🚀 Quick Start</a>
  </p>
</div>

---

## 📌 What's New (v1.2)

DocMind has been upgraded from ReAct to **PER (Plan-Execute-Reflect) architecture** — the biggest leap yet.

| Feature | Before (v1.0) | Now (v1.2) |
|---------|:-------------:|:----------:|
| Agent Architecture | ReAct (think-as-you-go) | **PER (Plan → Execute → Reflect)** |
| Built-in Tools | 11 | **25+** |
| Execution | Sequential | **Parallel (asyncio.gather)** |
| SSE Events | 4 types | **12 types (thinking/plan/reflection)** |
| Output | Raw tool result | **LLM-synthesized natural language** |
| Self-Improving | ❌ None | ✅ Experience Memory + Replay + Pattern Mining |
| Deep Analysis | ❌ None | ✅ Insight Extraction / Cross-Doc / Reports |
| Observability | ❌ None | ✅ Langfuse full-trace |
| MCP Protocol | ❌ None | ✅ MCP Bridge |
| Feishu Integration | ❌ None | ✅ Feishu Bitable access |

---

## 🆕 New Capabilities

### 1. PER Agent Architecture

Upgraded from ReAct to a three-phase PER loop:

```
User Query
   ↓
┌─ Phase 1: Planner ─────────────────────────┐
│  Analyze task → Decompose into DAG steps   │
│  Recommend optimal tool per step           │
└────────────────────────────────────────────┘
   ↓
┌─ Phase 2: Executor ────────────────────────┐
│  Dependency-aware scheduling               │
│  Independent steps run in parallel          │
│  Tool call → LLM synthesis → auto-retry    │
└────────────────────────────────────────────┘
   ↓
┌─ Phase 3: Reflector ───────────────────────┐
│  Verify output quality                     │
│  Detect hallucination/gaps/contradictions  │
│  Trigger re-plan or partial fix if needed  │
└────────────────────────────────────────────┘
   ↓
SSE streaming (plan reasoning + execution steps + citations)
```

Unlike ReAct's "think-as-you-go," PER plans before executing and reflects after — dramatically improving accuracy on complex multi-step tasks.

### 2. 25+ Built-in Tools

Expanded from 11 to 25+ tools:

| Category | Tool | Description |
|----------|------|-------------|
| 🔎 **Knowledge** | `search_knowledge_base` | Hybrid search (BM25 + vector) |
| | `vector_search` | Semantic search |
| 📄 **Analysis (🆕)** | `extract_insights` | Entity/metric/claim/structure extraction |
| | `cross_document_analysis` | Multi-document pattern analysis |
| | `generate_report` | Structured markdown reports |
| | `summarize_document` | Document summarization |
| | `extract_keywords` | Keyword extraction |
| 🌐 **Web** | `web_search` | DuckDuckGo real-time search |
| | `content_crawling` | Page fetch & clean |
| ⌨️ **Code** | `code_execution` | Sandboxed Python |
| 📊 **Data** | `data_analysis` | Data analysis |
| 🌍 **Translation** | `translation` | zh/en/ja/fr |
| 🧭 **Knowledge Graph** | `knowledge_graph` | Entity-relationship exploration |
| 🔌 **MCP (🆕)** | `mcp_call` | External MCP Server calls |
| 📋 **Feishu (🆕)** | `feishu/*` | Feishu document access |
| 🗂️ **Management** | `list_documents` / `get_document_info` | Document management |
| 💬 **Conversation** | `list_conversations` / `get_conversation_history` | Session history |

### 3. Self-Improving System

The Agent learns from its own execution history:

```
Execution History → ① Experience Memory → ② Execution Replay → ③ Pattern Mining → Skill Recommendations
```

**① Experience Memory**: When a benchmark question fails, the system automatically extracts structured "experiences" — what failed, what symptom, what lesson. These are injected into the Planner on matching scenarios.
- **18 experiences** accumulated, coverage improved 68.4% → 70.1% (+1.7%)
- Negative transfer protection ensures experiences only apply to appropriate scenarios

**② Execution Replay**: Every execution is saved as a "flight recorder" — supports replay and side-by-side diff.
- **49 execution snapshots** saved
- `python -m benchmark.replay <task_id>` to replay
- `python -m benchmark.replay --diff <a> <b>` to compare versions

**③ Pattern Mining**: Scans replays for high-frequency tool sequences. Discovered patterns become Skill Recommendations.
- 2 candidate skills found (document_discovery, get_web_workflow)

### 4. Deep Analysis Tools

| Tool | What it does |
|------|-------------|
| `extract_insights` | Extract entities, metrics, claims, structure from documents |
| `cross_document_analysis` | Multi-document pattern analysis (themes, differences, trends) |
| `generate_report` | Generate structured Markdown reports from analysis data |

### 5. SSE Streaming

Upgraded to 12 SSE event types across frontend and backend:

`thinking` → `plan_start` → `plan_step` → `plan_complete` → `tool_call` → `tool_result` → `reflection` → `chunk` → `message` → `done`

The frontend visualizes the Agent's planning, tool calls, and reflection in real-time.

### 6. Langfuse Observability

Full-trace observability via Langfuse with 5 observation points:

| Location | File | Traces |
|----------|------|--------|
| Planner | `planner.py` | Planning process |
| Executor | `executor.py` | Per-step execution |
| Tool Registry | `registry.py` | Tool calls |
| Reflector | `reflector.py` | Reflection assessment |
| Memory Bridge | `memory_bridge.py` | Memory recall |

### 7. MCP Bridge

Compatible with the [Model Context Protocol](https://modelcontextprotocol.io) — connect external MCP servers:

```python
@register_tool(name="mcp_call")
async def mcp_call(server_name: str, tool_name: str, arguments: dict) -> str:
    # Call external MCP Server via MCP SDK
```

Verified with GitHub MCP Server.

### 8. Feishu Integration

Access Feishu Bitable (多维表格) documents as an enterprise knowledge source.

---

## 📊 30-Question Benchmark

Comparing PER Agent against a RAG-only baseline on enterprise knowledge tasks:

| Metric | RAG Only | PER Agent | Change |
|--------|:--------:|:---------:|:------:|
| **Keyword Coverage** | 63% | **69%** | +6% |
| **Success Rate** | 50% (15/30) | **60% (18/30)** | +10% |
| **Avg Duration** | 20s | 36s | +16s (more tools) |
| **Tool Failures** | 0.0 | **0.0** | ✅ Rock-solid |

**Where the Agent shines:**

| Scenario | Gain | Why |
|----------|:----:|-----|
| Single Document Retrieval | +6% | More precise document targeting |
| **Cross-Document Analysis** | **+12%** | Multi-step retrieval covers more docs |
| **Framework Analysis (SWOT/PEST)** | **+24%** | Right tool + framework selection |
| Multi-Step Reasoning | +5% | Baseline already strong |
| **Web Search Integration** | **+12%** | Real DuckDuckGo calls |

> Biggest wins come from tasks where RAG alone falls short: cross-document analysis, framework reasoning, and web search. All 7 failures are L2 ambiguity/boundary questions — zero infrastructure noise.

### Optimization Journey

```
v1: 46% coverage · 8/30 success · 89s avg · 1.0 tool failures
                              ↓
        All 23pp improvement came from engineering fixes,
        NOT from changing the model or prompts
                              ↓
v2: 69% coverage · 18/30 success · 36s avg · 0.0 tool failures
```

---

## 🏗 Architecture at a Glance

```
┌─ Presentation ─────────────────────────────────┐
│  Vue 3 + Naive UI + ECharts + Vue Flow         │
├─ API Gateway ───────────────────────────────────┤
│  FastAPI + JWT + CORS + SSE                    │
├─ AI Agent Core ─────────────────────────────────┤
│  PER Loop | Tool Registry | Context Engine      │
│  RAG Pipeline | Knowledge Graph | Workflow      │
├─ AI / LLM ──────────────────────────────────────┤
│  DeepSeek V4 | Embedding | Reranker | Langfuse  │
├─ Data Storage ──────────────────────────────────┤
│  MySQL 8 | ES 8 | Redis 7 | Kafka | MinIO      │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (recommended) or Python 3.11+ / Node.js 18+ / MySQL 8 / Redis 7 / ES 8 / Kafka / MinIO

### 1. Clone
```bash
git clone https://github.com/sijie-Z/DocMind-RAG.git
cd DocMind-RAG
```

### 2. Start Infrastructure
```bash
cd backend && docker compose up -d
```

### 3. Configure
```bash
cp .env.docker.example .env.docker
# Edit .env.docker with your API keys
```

### 4. Start Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Start Frontend
```bash
cd frontend && npm install && npm run dev  # Port 5173
```

### 6. Access
| URL | Description |
|-----|-------------|
| http://localhost:5173 | Frontend UI |
| http://localhost:8000/docs | Swagger API Docs |
| http://localhost:8000/health | Health check |

### Demo Accounts
| Username | Password | Role |
|----------|----------|------|
| `guest` | `123456` | User |
| `admin` | `admin123` | Admin |

### Run Benchmark
```bash
python -m benchmark.run --questions benchmark/questions/v2.json --mode baseline   # RAG only
python -m benchmark.run --questions benchmark/questions/v2.json --mode agent      # PER Agent
python -m benchmark.run --compare benchmark/results/baseline_v2.json benchmark/results/agent_v2.json
```

---

## 📁 Project Structure

```
DocMind/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # REST API (17 modules)
│   │   ├── agent/                # PER Agent core
│   │   │   ├── loop.py           #   PER main loop
│   │   │   ├── planner.py        #   Planner
│   │   │   ├── executor.py       #   Executor
│   │   │   ├── reflector.py      #   Reflector
│   │   │   ├── registry.py       #   Tool registry
│   │   │   ├── experience/       #   Experience memory (🆕)
│   │   │   ├── replay/           #   Execution replay (🆕)
│   │   │   ├── mining/           #   Pattern mining (🆕)
│   │   │   └── tools/            #   25+ tool implementations
│   │   ├── core/                 # Infrastructure
│   │   ├── rag/                  # RAG pipeline
│   │   └── worker/               # Kafka async processor
│   ├── tests/                    # 422+ test cases
│   └── benchmark/                # 30-question benchmark (🆕)
├── frontend/src/                 # Vue 3 frontend
└── docs/
    ├── architecture.html         # Interactive architecture diagram
    └── product-definition.md     # Product definition
```

---

## 🧪 Testing

```bash
cd backend
python -m pytest tests/ -v --tb=short
python -m pytest tests/ --cov=app --cov-report=html
make test && make lint
```

## 🚢 Deployment

- **Docker Compose**: `cd backend && docker compose up -d`
- **Kubernetes**: `kubectl apply -f deploy/k8s/`
- **Manual**: See `deploy/README.md`

---

## 📝 Version History

| Version | Date | Highlights |
|---------|------|-----------|
| **v1.2.1** | 2026-05 | Stability fixes, parallel execution, page transitions |
| **v1.2.0** | 2026-05 | PER architecture, 25+ tools, self-improving, deep analysis |
| **v1.1.0** | 2026-05 | Agent mode, sample docs, CJK tokenization |
| **v1.0.0** | 2026-05 | Initial: RAG pipeline, workflow editor, knowledge graph |

---

## 🔗 Links

- **Architecture**: https://sijie-z.github.io/DocMind-RAG/architecture.html
- **GitHub**: https://github.com/sijie-Z/DocMind-RAG
- **API Docs**: http://localhost:8000/docs
- **Issues**: https://github.com/sijie-Z/DocMind-RAG/issues

---

<p align="center">
  <strong>DocMind</strong> — PER-based Agentic RAG System
  <br>
  <sub>Built with ❤️ by the DocMind Team</sub>
</p>
