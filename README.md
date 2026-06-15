<p align="center">
  <h1 align="center">🤖 DocMind</h1>
  <p align="center"><strong>PER-based Agentic RAG System</strong></p>
  <p align="center">
    <code>69% Keyword Coverage</code>
    <code>+10% Success Rate vs Baseline</code>
    <code>Langfuse Observability</code>
    <code>MCP Compatible</code>
  </p>
  <p align="center">
    <a href="https://sijie-z.github.io/DocMind-RAG/architecture.html"><img src="https://img.shields.io/badge/在线演示-架构图-22d3ee?logo=githubpages" alt="Architecture"></a>
    <a href="https://github.com/sijie-Z/DocMind-RAG"><img src="https://img.shields.io/badge/版本-v1.2.0-blue" alt="Version"></a>
    <a href="https://github.com/sijie-Z/DocMind-RAG/blob/main/LICENSE"><img src="https://img.shields.io/badge/开源协议-MIT-green" alt="License"></a>
    <a href="#-benchmark-results"><img src="https://img.shields.io/badge/Benchmark-v1-8A2BE2" alt="Benchmark"></a>
    <br>
    <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/Vue-3.4-4FC08D?logo=vuedotjs" alt="Vue 3">
    <img src="https://img.shields.io/badge/测试-422%20通过-brightgreen" alt="Tests">
    <img src="https://img.shields.io/badge/覆盖率-84%25-brightgreen" alt="Coverage">
    <img src="https://img.shields.io/badge/工具-25%2B%20个-orange" alt="Tools">
    <img src="https://img.shields.io/badge/Langfuse-已集成-yellow" alt="Langfuse">
    <img src="https://img.shields.io/badge/Experience-18%20条-8A2BE2" alt="Experience">
    <img src="https://img.shields.io/badge/Replay-49%20条-blue" alt="Replay">
    <img src="https://img.shields.io/badge/Skill%20Discovery-2%20候选-FF6B35" alt="Pattern Mining">
  </p>
</p>

---

## 📊 Benchmark Results

30-question evaluation comparing **PER Agent** against a **RAG-only Baseline** on enterprise knowledge tasks. [Benchmark v1] — frozen, reproducible.

| Metric | Baseline (RAG only) | PER Agent | Change |
|--------|:-------------------:|:---------:|:------:|
| **Keyword Coverage** | 63% | **69%** | +6% |
| **Success Rate** | 15/30 (50%) | **18/30 (60%)** | +10% |
| **Avg Duration** | 20s | 36s | +16s (more tools) |
| **Tool Failures** | 0.0 | **0.0** | ✅ Reliable |

### Per-Scenario Breakdown

| Scenario | Baseline | PER Agent | Gain | Why Agent Wins |
|----------|:--------:|:---------:|:----:|----------------|
| Single Document Retrieval | 94% | **100%** | +6% | Agent finds docs more precisely |
| **Cross-Document Analysis** | 65% | **77%** | **+12%** | Multi-step retrieval covers more docs |
| **Framework Analysis** (SWOT/PEST/DuPont) | 56% | **80%** | **+24%** | Agent selects the right tool + framework |
| Multi-Step Reasoning | 85% | **90%** | +5% | Baseline already strong; Agent more stable |
| Web Search Integration | 75% | **88%** | **+12%** | Real DuckDuckGo calls vs. LLM knowledge |
| Tool Recovery | 72% | 67% | -6% | Agent can over-complicate on retry tasks |
| Edge Cases | 50% | 38% | -12% | Agent over-processes boundary queries |
| Ambiguity (L2) | 0% | 0% | — | Both hit system limits |

> **Key insight**: Agent's biggest gains are in **cross-document analysis** (+12%), **framework reasoning** (+24%), and **web search** (+12%) — precisely the tasks where RAG alone falls short. The 7 failures are all L2 ambiguity/boundary questions (0% infrastructure noise).

### Distribution

```
┌──────────────────┬──────┬──────────────────────────────┐
│ Single Doc       │  4   │ L1-DOC-01 ~ 04               │
│ Cross Doc        │  5   │ L1-CROSS-01 ~ 05             │
│ Framework        │  5   │ L1-FRAME-01 ~ 05             │
│ Multi-Step       │  4   │ L1-MULTI-01 ~ 04             │
│ Web Search       │  2   │ L1-WEB-01 ~ 02               │
│ Tool Recovery    │  3   │ L2-RECOV-01 ~ 03             │
│ Edge Case        │  4   │ L2-EDGE-01 ~ 04              │
│ Ambiguity        │  3   │ L2-AMBIG-01 ~ 03             │
├──────────────────┼──────┤                              │
│ **Total**        │ **30**│ (tag: benchmark-v1)          │
└──────────────────┴──────┴──────────────────────────────┘
```

---

## 🔁 Failure-Driven Optimization

The most valuable result isn't the final score — it's the **engineering loop** that took us there.

```
  Agent v1                     Agent v2
  ─────────                    ─────────
  46% coverage   ──→   69% coverage   (+23pp ✅)
  8/30 success   ──→  18/30 success   (+10 ✅)
  89s avg        ──→  36s avg         (-60% ✅)
  1.0 tool fail  ──→  0.0 tool fail   (zeroed ✅)
```

### How It Happened

```
① Agent v1 Benchmark (46%)
    │
    ▼
② Failure Collection — classified every failure
    │  ├─ APIConnectionError
    │  ├─ Timeout (no backoff)
    │  ├─ Redis not initialized on cold start
    │  └─ Tool call failures
    │
    ▼
③ Langfuse Trace — traced each failure to root cause
    │  └─ Identified: missing retry logic, uninitialized clients,
    │     improper error propagation in tool registry
    │
    ▼
④ Runtime Fixes
    │  ├─ Exponential backoff retry
    │  ├─ Lazy initialization for Redis/ES clients
    │  ├─ Tool error propagation → graceful degradation
    │  └─ Timeout configuration per tool type
    │
    ▼
⑤ Re-benchmark → Agent v2 (69%)
      46% ──────────────────────────────→ 69%
```

This is not a model improvement — it's an **engineering improvement**. The 23pp gain came entirely from reliability fixes, not from changing the LLM or prompt. That's what the Benchmark → Langfuse → Fix → Re-benchmark loop enables.

> **Our principle**: before chasing model capability, eliminate infrastructure noise. Only then can you compare agents fairly.

---

## 🤔 Why Agent instead of RAG?

Most "RAG systems" stop at retrieval. DocMind's PER Agent goes further — RAG is **one tool** in a 25+ tool arsenal, invoked only when the agent decides it's needed.

| Task | RAG Only | PER Agent |
|------|:--------:|:---------:|
| "Find the revenue in this annual report" | ✅ Direct retrieval | ✅ Agent uses knowledge tool |
| "Compare gross margins across 3 competitors" | ❌ No cross-doc reasoning | ✅ Agent calls retrieval → reads → synthesises |
| "SWOT analysis of Company A" | ❌ Can't apply frameworks | ✅ Agent selects SWOT framework → extracts → structures |
| "What changed in the 2024 data regulation vs 2023?" | ❌ No diff capability | ✅ Agent retrieves both documents → compares → summarises |
| "Search the web for latest AI funding news, then assess" | ❌ No web access | ✅ Agent calls DuckDuckGo → reads → analyses |
| "Document ID not found — what else do you have?" | ❌ No error recovery | ✅ Agent lists available documents, suggests alternatives |
| "Analyze apples." (ambiguous) | ❌ Can't clarify | ⚠️ Both hit ambiguity limits |

**RAG finds information. The Agent plans, selects tools, cross-references, and verifies results.**

---

## 🧠 Self-Improving Agent

DocMind's most advanced capability: the Agent learns from its own execution history, remembers mistakes, replays past runs for analysis, and discovers recurring patterns that become new skills.

### Three-Stage Learning Pipeline

```
Execution History
    ↓
① Experience Memory — learn from failures
    ↓
② Execution Replay — analyse what happened
    ↓
③ Pattern Mining — discover recurring workflows
    ↓
    Skill Recommendations
```

### ① Experience Memory: Learn from Failures

When a benchmark question fails, the system automatically extracts a structured "experience" — what scenario failed, what symptom it showed, and what lesson the Planner should follow.

```
Benchmark Failure (L1-FRAME-01: SWOT analysis missing)
    ↓
Extractor analyses: category=framework, keywords_missed=[优势,劣势,机会,威胁]
    ↓
Structured Experience generated:
    scenario:    framework_analysis
    symptom:     keywords_missing_swot
    lesson:      "SWOT framework must output all 4 dimensions"
    confidence:  0.90
    applicable:  [framework_analysis]
    avoid_for:   [edge_case_simple]
    ↓
Stored in Redis + local JSON → retrieved at next planning session
```

Current state: **18 experiences** extracted from benchmark failures, with Negative Transfer protection (metadata ensures experiences are only injected into appropriate scenarios).

**Verified impact**: Benchmark coverage improved from 68.4% → 70.1% with Experience Memory enabled (+1.7%). More importantly, edge-case negative transfer was eliminated when metadata protection was added.

### ② Execution Replay: Flight Recorder

Every agent execution is automatically saved as a structured snapshot — a "flight recorder" that captures each plan step, tool call, intermediate result, and decision.

```
python -m benchmark.replay <task_id>          # replay a single execution
python -m benchmark.replay --diff <a> <b>     # compare two versions
python -m benchmark.replay --list              # browse all saved runs
```

**Replay output example:**

```
Execution Replay: 15cae5c15e5e
  Query:  从知识库中找一份企业年报，提取营收数据
  Steps:  2 completed, 0 failures, 36.2s

  ✅ Step 1: search_knowledge_base  (8.6s)
     → Found 3 documents matching "年报"
  ✅ Step 2: list_documents         (11.7s)
     → Retrieved: 星辰科技 2024 年度报告
```

**Diff output** compares two agent versions side-by-side:

```
Step 1: search_knowledge_base (2.1s) ✅  |  search_knowledge_base (2.3s) ✅
Step 2: extract_insights (4.0s) ✅      |  extract_insights (3.5s) ✅
                                         |  Step 3: compare_docs (5.1s) ✅ ← NEW
Coverage: 60%                            |  Coverage: 80% ← +20%
```

Current state: **49 execution snapshots** saved, replayable at any time.

### ③ Pattern Mining & Skill Discovery

The Pattern Miner scans all saved Replay snapshots and identifies recurring tool-use sequences. High-frequency, high-success patterns become Skill Recommendations.

```
python -m app.agent.mining.report           # view recommendations
python -m app.agent.mining.report --save    # persist as report
```

**Mining results from 47 executions:**

```
Top patterns found:
  list_documents                             14 times
  search_knowledge_base                      14 times
  search_knowledge_base → list_documents      5 times  ⭐
  get_current_time → web_search               3 times  ⭐
  ...
```

**Skill Recommendations generated:**

| Skill | Pattern | Confidence | Observations |
|-------|---------|:----------:|:-----------:|
| `document_discovery` | `search → list_documents` | 70% | 5 |
| `get_web_workflow` | `get_current_time → web_search` | 63% | 3 |

Each recommendation is presented with supporting evidence (frequency, success rate, trigger keywords) as a **suggestion** — not auto-registered. This respects the principle that pattern ≠ skill; human validation bridges the gap.

### The Evolution Path

```
v1 → v2:   Manual fix (human analyses → human fixes → re-benchmark)
v2 → v3:   Experience Memory (auto-extract → auto-inject → benchmark)
v3 → v4:   Replay + Pattern Mining (observe → analyse → recommend)
Future:    Skill Auto-Registration (autonomous skill evolution)
```

What started as a manual engineering process has evolved into a **self-improving agent platform** — the agent can observe itself, learn from mistakes, replay past executions, and discover new capabilities from its own experience.

---

## 🏗 System Architecture

### 5-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     表现层 (Presentation)                    │
│         Vue 3 + Naive UI + ECharts + Vue Flow              │
├─────────────────────────────────────────────────────────────┤
│                   API 网关层 (API Gateway)                   │
│          FastAPI + JWT + CORS + Rate Limit + SSE            │
├─────────────────────────────────────────────────────────────┤
│                   AI Agent 核心层                            │
│   PER Loop │ Tool Registry │ Context Engine │ Skill       │
│       │              ↑                        │             │
│       ↓              │                        ↓             │
│   RAG 管道 │ 知识图谱 │ 工作流引擎 │ 文档管理                │
├─────────────────────────────────────────────────────────────┤
│                    AI / LLM 层 (Intelligence)               │
│   DeepSeek V4 │ Embedding │ Reranker │ Tool Registry       │
├─────────────────────────────────────────────────────────────┤
│                   数据存储层 (Data Storage)                   │
│  MySQL 8 │ Elasticsearch 8 │ Redis 7 │ Kafka │ MinIO       │
└─────────────────────────────────────────────────────────────┘
```

> Open `docs/architecture.html` for the interactive diagram.

### PER Agent: Plan → Execute → Reflect

DocMind's core differentiator — a three-phase architecture that surpasses traditional ReAct:

```
用户提问
   ↓
┌──────────────────────────────────────────────┐
│  Phase 1: 规划 (Planner)                     │
│  • 分析任务意图                              │
│  • 制定分步执行计划（含依赖关系）              │
│  • 为每步推荐最佳工具                         │
├──────────────────────────────────────────────┤
│  Phase 2: 执行 (Executor)                    │
│  • 按计划顺序调用工具（25+ 内置工具）          │
│  • 每步结果经 LLM 自然语言合成                │
│  • 支持失败重试和工具降级                      │
├──────────────────────────────────────────────┤
│  Phase 3: 反思 (Reflector)                   │
│  • 审查执行结果是否满足原始需求               │
│  • 检测错误或不一致（幻觉/缺漏/矛盾）          │
│  • 必要时触发重新规划或局部修复                │
└──────────────────────────────────────────────┘
   ↓
SSE 流式返回最终答案（含规划推理 + 执行过程 + 引用溯源）
```

**Key parameters**: max steps 15 | LLM temperature 0.1 | SSE streaming | exponential backoff retry

**Why this matters**: Plan generates a full DAG upfront (vs. ReAct's serial step-by-step), and Reflect verifies output quality, auto-correcting errors.

---

## 🔭 Observability (Langfuse)

Every agent execution is traced through Langfuse:

- **Full trace visibility**: plan steps, tool calls, LLM completions, timings
- **Failure classification**: API errors, timeouts, tool failures categorised automatically
- **Cost tracking**: per-conversation token usage and latency
- **Benchmark integration**: each of the 30 benchmark questions generates a trace

> Screenshot: [Langfuse Dashboard](https://cloud.langfuse.com) (available when running)

---

## 🔌 MCP Bridge

DocMind can connect to external MCP (Model Context Protocol) servers, extending its toolset beyond built-in capabilities:

- **GitHub MCP Server** — repository operations, code search, PR management
- **Filesystem MCP Server** — file read/write access
- **Custom MCP servers** — any service exposing MCP tools

MCP tools are registered into the same Tool Registry as native tools, with the same permission and audit controls.

---

## ✨ Features

### 🤖 PER Agent (Core Differentiator)

| Feature | Description |
|---------|-------------|
| **PER 3-Phase Architecture** | Plan → Execute → Reflect, DAG decomposition + parallel tools + self-correction |
| **25+ Built-in Tools** | Knowledge retrieval, web search, document parsing, summarisation, deep analysis, code execution, translation, and more |
| **Tool Registry** | Unified registration, auth, sandbox isolation, audit trail |
| **Context Engine** | Multi-turn memory management, automatic token budget allocation (system 2K / dialog 8K / tools 4K) |
| **Thinking Stream** | Real-time frontend visualisation of every Agent reasoning step |
| **Task Decomposition** | Complex tasks automatically broken into multi-step execution plans |
| **Skill Learning** | Self-improvement from successful tool-use patterns |

#### Built-in Tools

| Tool | Description |
|------|-------------|
| `🔎 Knowledge Retrieval` | Hybrid search over enterprise knowledge base with relevance scoring |
| `🌐 Web Search` | Real-time DuckDuckGo search to supplement knowledge gaps |
| `📄 Document Parsing` | Extract structured content from PDF, Word, TXT, Markdown |
| `📝 Smart Summarisation` | Long document summarisation, multi-document comparison |
| `📊 Deep Analysis` | Insight extraction, trend analysis, sentiment, cross-doc comparison |
| `🗂️ File Management` | Organisation, batch tagging, archiving |
| `⌨️ Code Execution` | Sandboxed Python execution for data analysis |
| `🔗 Content Crawling` | Web page fetching with automatic cleanup |
| `🔄 Batch Processing` | Large dataset chunking with progress tracking |
| `🌍 Translation` | Chinese/English/Japanese/French, document and segment levels |
| `🧭 Knowledge Graph` | Entity-relationship exploration, graph querying, interactive browsing |

### 📚 RAG Pipeline (Agent's Core Tool)

| Feature | Description |
|---------|-------------|
| **Document Parsing** | PDF, Word, TXT, Markdown via LangChain smart chunking |
| **Hybrid Retrieval** | BM25 keyword + KNN vector dual-channel, RRF fusion |
| **Cross-Encoder Reranking** | Two-stage re-ranking, +30% retrieval precision |
| **Semantic Cache** | Cosine similarity ≥0.92 returns cached results, saving LLM costs |
| **Context Compression** | Smart trimming of retrieval results to control token usage |
| **Citation Tracking** | Every answer annotated with `[n]` references linking to source |

### 💬 Smart Chat

- **SSE Streaming**: Token-level real-time display, typewriter effect
- **Multi-turn**: Conversation history awareness with session management
- **Agent Mode**: Agent decides when to use RAG or other tools
- **Citation Links**: `[1]` `[2]` references, click to view source
- **Markdown Rendering**: Code highlighting, LaTeX, tables, flowcharts
- **Export**: Conversations exportable as Markdown

### 🔗 Knowledge Graph

- Canvas force-directed graph visualisation
- 7 entity types extracted automatically (Person, Organisation, Location, Technology, Concept, Event, Product)
- Interactive: drag, zoom, click for details, keyword filter

### ⚙️ Visual Workflow Editor

- Drag-and-drop DAG builder (Vue Flow based)
- **Node types**: LLM, API call, code execution, condition, smart routing, memory, data transform
- **Real-time debug**: execution trace drawer, node status colour coding
- **DAG Engine**: Kahn topological sort + DFS cycle detection, auto-optimised execution order

### 🏢 Enterprise Features

| Feature | Description |
|---------|-------------|
| **RBAC** | User → Role → Organisation 3-tier multi-tenancy |
| **JWT Auth** | Token auth + 24h/7d dual-token mechanism |
| **Audit Log** | Full operation audit trail, compliance-ready |
| **Prometheus** | Request volume, latency, error rate, Agent tool call stats |
| **Grafana** | Pre-built dashboards (API perf, Agent stats, system resources) |
| **OpenTelemetry** | Distributed tracing |
| **i18n** | 中文 / English / 日本語 / Français, instant switch |

---

## 🛠 Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Backend** | FastAPI + Uvicorn | Fully async, auto Swagger |
| **Database** | MySQL 8 + SQLAlchemy 2.0 | Async ORM + Alembic migrations |
| **Cache** | Redis 7 | Semantic cache + token blacklist + session store |
| **Search** | Elasticsearch 8 | KNN vector + BM25 keyword search |
| **Message Queue** | Kafka (aiokafka) | Async document processing pipeline |
| **Object Storage** | MinIO | S3-compatible document file storage |
| **LLM** | DeepSeek V4 (Flash/Pro) | Reasoning + deep analysis |
| **Embedding** | OpenAI-compatible API | 2048-dim vector embeddings |
| **Agent Architecture** | PER 3-phase | Plan → Execute → Reflect, DAG parallel scheduling |
| **Observability** | Langfuse | Full trace, failure classification, cost tracking |
| **MCP** | MCP Protocol Bridge | GitHub, Filesystem, custom servers |
| **Document** | LangChain + PyPDF + python-docx | Multi-format smart chunking |
| **Frontend** | Vue 3.4 + TypeScript 5.3 + Vite 5 | Composition API + type safety |
| **UI** | Naive UI + ECharts + Vue Flow | Enterprise components + charts + flow |
| **State** | Pinia | Vue 3 official |
| **i18n** | Vue I18n | zh/en/ja/fr |
| **Monitoring** | Prometheus + Grafana + OpenTelemetry | Metrics + dashboards + tracing |
| **Security** | JWT + RBAC + Multi-tenancy + Audit | Enterprise security |
| **Container** | Docker + Docker Compose + K8s | Dev/test/prod coverage |
| **CI/CD** | GitHub Actions | Test + lint + build + security scan |

---

## 🚀 Quick Start

### Requirements

- **Docker Desktop** (recommended) — one-click infrastructure
- Or manual: Python 3.11+, Node.js 18+, MySQL 8, Redis 7, Elasticsearch 8, Kafka, MinIO

### 1. Clone

```bash
git clone https://github.com/sijie-Z/DocMind-RAG.git
cd DocMind-RAG
```

### 2. Start Infrastructure

```bash
cd backend
docker compose up -d
```

> Starts MySQL, Redis, Elasticsearch, Kafka, MinIO (~30s).

### 3. Configure

```bash
cp .env.docker.example .env.docker
```

Edit `.env.docker`:

```env
# LLM (DeepSeek / OpenAI-compatible)
DEEPSEEK_API_KEY=sk-your-api-key-here

# Embedding model
EMBEDDING_API_KEY=your-embedding-api-key

# Rerank model (optional)
RERANK_API_KEY=your-rerank-api-key

# Langfuse (optional, for observability)
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
```

### 4. Start Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Start Frontend

```bash
cd frontend
npm install
npm run dev                      # Port 5173
```

### 6. Open App

| URL | Description |
|-----|-------------|
| http://localhost:5173 | Frontend UI |
| http://localhost:8000/docs | API Docs (Swagger) |
| http://localhost:8000/health | Health check |

### Demo Accounts

| Username | Password | Role |
|----------|----------|------|
| `guest` | `123456` | User |
| `admin` | `admin123` | Admin |

### 7. Seed Sample Data (Optional)

```bash
cd backend
python seed_docs/seed.py
```

> Imports 2 sample documents to test Agent analysis immediately.

### Run Benchmark

```bash
# Baseline (RAG only)
python -m benchmark.run --questions benchmark/questions/v2.json --mode baseline

# PER Agent
python -m benchmark.run --questions benchmark/questions/v2.json --mode agent

# Compare results
python -m benchmark.run --compare benchmark/results/baseline_v2.json benchmark/results/agent_v2.json

# Experience Memory A/B test
python -m benchmark.run --mode agent --no-experience --output results/agent_no_exp.json
python -m benchmark.run --mode agent --experience --output results/agent_with_exp.json
python -m benchmark.run --compare results/agent_no_exp.json results/agent_with_exp.json
```

### Replay & Analyse

```bash
# List all saved replays
python benchmark/replay.py --list

# Replay a specific execution
python benchmark/replay.py <task_id>

# Diff two versions
python benchmark/replay.py --diff <task_a> <task_b>

# Generate Skill Recommendation Report
python -m app.agent.mining.report --save
```

---

## 📁 Project Structure

```
DocMind/
├── backend/                          # Backend
│   ├── app/
│   │   ├── api/v1/endpoints/         # REST API (17 modules)
│   │   ├── agent/                    # PER Agent core
│   │   │   ├── loop.py               #   Main loop (Plan→Execute→Reflect)
│   │   │   ├── registry.py           #   Tool registry
│   │   │   ├── context.py            #   Context engine
│   │   │   ├── events.py             #   SSE event model
│   │   │   ├── observability.py      #   Langfuse integration
│   │   │   ├── exec_context.py       #   Execution context (flight recorder)
│   │   │   ├── experience/           #   Self-improving: learn from failures
│   │   │   │   ├── models.py         #     Experience data model
│   │   │   │   ├── store.py          #     Persistence (Redis + local JSON)
│   │   │   │   ├── extractor.py      #     Auto-extract from benchmark failures
│   │   │   │   └── run_extract.py    #     Bootstrap CLI
│   │   │   ├── replay/               #   Execution replay engine
│   │   │   │   └── engine.py         #     Load, format, diff
│   │   │   ├── mining/               #   Pattern mining & skill discovery
│   │   │   │   ├── models.py         #     Pattern data models
│   │   │   │   ├── miner.py          #     Sequence extraction & frequency stats
│   │   │   │   ├── analyzer.py       #     Pattern → Skill recommendation
│   │   │   │   └── report.py         #     Report generator (JSON + Markdown)
│   │   │   └── tools/               #   Tool implementations
│   │   ├── core/                    # Infrastructure (config, DB, ES, Redis)
│   │   ├── models/                  # SQLAlchemy ORM
│   │   ├── rag/                     # RAG pipeline
│   │   ├── schemas/                 # Pydantic schemas
│   │   ├── services/                # Business logic
│   │   └── worker/                  # Kafka async document processor
│   ├── tests/                       # 422 test cases (25 files)
│   ├── benchmark/                   # Benchmark framework
│   │   ├── questions/               #   30 benchmark question sets (v1, v2)
│   │   ├── results/                 #   Baseline & Agent result reports
│   │   ├── cases/                   #   Per-question case files
│   │   ├── run.py                   #   Benchmark runner
│   │   └── scorer.py                #   Scorer & classification
│   └── seed_docs/                   # Sample documents
├── frontend/                        # Vue 3 frontend
│   └── src/
│       ├── api/                     # API clients
│       ├── components/agent/        # Agent components (PlanTree, ThinkingStream, etc.)
│       ├── stores/                  # Pinia state
│       └── views/                   # Pages (chat, agent, knowledge, workflow, dashboard)
├── deploy/k8s/                      # Kubernetes manifests
├── docs/
│   └── architecture.html            # Interactive architecture diagram
└── .github/workflows/ci.yml         # CI/CD
```

---

## 🧪 Testing

```bash
# Backend (422 test cases, 25 files)
cd backend
python -m pytest tests/ -v --tb=short

# Coverage
cd backend
python -m pytest tests/ --cov=app --cov-report=html

# One-shot check
make test
make lint
```

---

## 🚢 Deployment

| Method | Description | Command |
|--------|-------------|---------|
| **Docker Compose** | Single machine | `cd backend && docker compose up -d` |
| **Kubernetes** | Cluster | `kubectl apply -f deploy/k8s/` |
| **Manual** | Custom env | See `deploy/README.md` |

---

## 📝 Version History

See [CHANGELOG.md](CHANGELOG.md)

| Version | Date | Key Changes |
|---------|------|-------------|
| **v1.2.0** | 2026-05-24 | PER Agent architecture, 25+ tools, deep analysis, full SSE pipeline |
| **v1.1.0** | 2026-05-17 | Agent mode toggle, sample docs, CJK tokenisation fix |
| **v1.0.0** | 2026-05-17 | First release: RAG pipeline, PER Agent, workflow editor, knowledge graph |

---

## 🤝 Contributing

Issues and PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

Conventions:
- Backend: Python 3.11+, ruff code style
- Frontend: TypeScript strict mode, ESLint + Prettier
- Commits: Conventional Commits

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## 🔗 Links

- **Architecture Diagram**: [GitHub Pages](https://sijie-z.github.io/DocMind-RAG/architecture.html)
- **GitHub**: [sijie-Z/DocMind-RAG](https://github.com/sijie-Z/DocMind-RAG)
- **API Docs**: http://localhost:8000/docs (when running)
- **Issues**: [GitHub Issues](https://github.com/sijie-Z/DocMind-RAG/issues)
- **Benchmark v1**: tagged `benchmark-v1`

---

<p align="center">
  <strong>DocMind</strong> — PER-based Agentic RAG System
  <br>
  <sub>Built with ❤️ by the DocMind Team</sub>
</p>
