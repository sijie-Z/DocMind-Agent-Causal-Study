<p align="center">
  <a href="README_EN.md">🇺🇸 English</a> · <strong>🇨🇳 中文</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/版本-v1.2.1-blue?logo=semver" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Vue_3-3.4-4FC08D?logo=vuedotjs" alt="Vue 3">
  <img src="https://img.shields.io/badge/DeepSeek-V4-8A2BE2" alt="DeepSeek">
  <img src="https://img.shields.io/badge/开源协议-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="PRs Welcome">
</p>

<div align="center">
  <h1>🤖 DocMind</h1>
  <p><strong>基于 PER 架构的企业级 AI Agent 系统</strong></p>
  <p>25+ 内置工具 · 自我进化 · 可观测 · MCP 兼容</p>
  <p>
    <a href="https://sijie-z.github.io/DocMind-RAG/architecture.html">📊 交互式架构图</a> ·
    <a href="#-benchmark">📈 评测数据</a> ·
    <a href="#-quick-start">🚀 快速开始</a>
  </p>
</div>

---

## 📌 版本亮点 (v1.2)

这是 DocMind 的一次重大升级——从 ReAct 升级为 **PER（Plan-Execute-Reflect）架构**，Agent 能力全面提升。

| 特性 | 之前 (v1.0) | 现在 (v1.2) |
|------|:----------:|:----------:|
| Agent 架构 | ReAct（边想边做） | **PER（先规划→再执行→再反思）** |
| 内置工具 | 11 个 | **25+ 个** |
| 工具执行 | 串行 | **支持并行 (asyncio.gather)** |
| SSE 事件 | 4 种 | **12 种（含 thinking/plan/reflection）** |
| 反馈方式 | 原始工具输出 | **LLM 自然语言合成** |
| 自我进化 | ❌ 无 | ✅ 经验记忆 + 执行回放 + 模式挖掘 |
| 深度分析 | ❌ 无 | ✅ 洞察提取 / 跨文档分析 / 报告生成 |
| 可观测性 | ❌ 无 | ✅ Langfuse 全链路追踪 |
| MCP 协议 | ❌ 无 | ✅ MCP Bridge |
| 飞书集成 | ❌ 无 | ✅ 飞书文档接入 |

---

## 🆕 新增能力一览

### 1. PER Agent 架构

从 ReAct 升级为三阶段 PER 循环：

```
用户提问
   ↓
┌─ Phase 1: 规划 (Planner) ─────────────────┐
│  分析任务 → 拆解为多步 DAG → 每步推荐工具  │
└────────────────────────────────────────────┘
   ↓
┌─ Phase 2: 执行 (Executor) ────────────────┐
│  依赖图调度 → 独立步骤并行执行              │
│  工具调用 → LLM 合成 → 失败自动重试        │
└────────────────────────────────────────────┘
   ↓
┌─ Phase 3: 反思 (Reflector) ───────────────┐
│  审查结果 → 检测幻觉/缺漏/矛盾              │
│  不满意 → 触发重规划或局部修复              │
└────────────────────────────────────────────┘
   ↓
SSE 流式返回（规划过程 + 执行步骤 + 引用溯源）
```

相比 ReAct 的"边想边做"，PER 先规划再执行，且执行完整体反思，大幅提升复杂任务的准确性。

### 2. 25+ 内置工具

从 11 个扩展到 25+ 个，按功能分为：

| 类别 | 工具 | 说明 |
|------|------|------|
| 🔎 **知识检索** | `search_knowledge_base` | 混合检索（BM25 + 向量） |
| | `vector_search` | 语义搜索 |
| 📄 **文档分析** (🆕) | `extract_insights` | 实体/指标/主张/结构提取 |
| | `cross_document_analysis` | 多文档对比分析 |
| | `generate_report` | 结构化报告生成 |
| | `summarize_document` | 文档摘要 |
| | `extract_keywords` | 关键词提取 |
| 🌐 **网络** | `web_search` | DuckDuckGo 联网搜索 |
| | `content_crawling` | 页面抓取与清洗 |
| ⌨️ **代码** | `code_execution` | 沙箱 Python 执行 |
| 📊 **数据** | `data_analysis` | 数据分析 |
| 🌍 **翻译** | `translation` | 中/英/日/法 |
| 🧭 **知识图谱** | `knowledge_graph` | 实体关系探索 |
| 🔌 **MCP (🆕)** | `mcp_call` | 外部 MCP Server 调用 |
| 📋 **飞书 (🆕)** | `feishu/*` | 飞书文档接入 |
| 🗂️ **管理** | `list_documents` / `get_document_info` | 文档管理 |
| 💬 **对话** | `list_conversations` / `get_conversation_history` | 对话管理 |

### 3. 自我进化系统

Agent 能从自身执行历史中学习，持续进步：

```
执行历史 → ① 经验记忆 → ② 执行回放 → ③ 模式挖掘 → 技能推荐
```

**① 经验记忆**：评测失败时自动提取结构化的"经验教训"，下次类似场景自动注入规划器。
- 已积累 **18 条经验**，使覆盖率提升 68.4% → 70.1%（+1.7%）
- 含负迁移保护（经验只在适用场景注入）

**② 执行回放**：每次执行保存为"黑匣子"，支持回放和版本对比。
- 已保存 **49 条执行记录**
- `python -m benchmark.replay <task_id>` 回放
- `python -m benchmark.replay --diff <a> <b>` 对比两版本

**③ 模式挖掘**：扫描执行记录，发现高频工具调用序列，推荐为 Skill。
- 已发现 2 个候选 Skill（document_discovery, get_web_workflow）

### 4. 深度分析工具

| 工具 | 功能 |
|------|------|
| `extract_insights` | 从文档提取实体、指标、主张、结构 |
| `cross_document_analysis` | 多文档模式分析（共同主题、差异、趋势） |
| `generate_report` | 从分析数据生成结构化 Markdown 报告 |

### 5. SSE 流式事件

从前端到后端全面升级为 12 种 SSE 事件类型：

`thinking` → `plan_start` → `plan_step` → `plan_complete` → `tool_call` → `tool_result` → `reflection` → `chunk` → `message` → `done`

前端实时展示 Agent 的规划过程、工具调用、反思结果。

### 6. Langfuse 可观测性

全链路追踪通过 Langfuse 实现，5 个埋点位置：

| 位置 | 文件 | 追踪内容 |
|------|------|---------|
| Planner | `planner.py` | 规划过程 |
| Executor | `executor.py` | 每步执行 |
| Tool Registry | `registry.py` | 工具调用 |
| Reflector | `reflector.py` | 反思评估 |
| Memory Bridge | `memory_bridge.py` | 记忆召回 |

### 7. MCP Bridge

兼容 [MCP 协议](https://modelcontextprotocol.io)，可接入外部 MCP Server：

```python
@register_tool(name="mcp_call")
async def mcp_call(server_name: str, tool_name: str, arguments: dict) -> str:
    # 通过 MCP SDK 调用外部 Server
```

已在 GitHub MCP Server 上验证。

### 8. 飞书集成

支持接入飞书多维表格（Bitable）文档，扩展企业内部知识源。

---

## 📊 30 题评测

30 道企业知识任务的对比评测，PER Agent vs 纯 RAG 基线：

| 指标 | 纯 RAG | PER Agent | 变化 |
|------|:------:|:---------:|:----:|
| **关键词覆盖率** | 63% | **69%** | +6% |
| **完成率** | 50% (15/30) | **60% (18/30)** | +10% |
| **平均用时** | 20s | 36s | +16s (工具更多) |
| **工具失败率** | 0.0 | **0.0** | ✅ 稳定 |

**分场景看，Agent 的优势场景：**

| 场景 | 提升 | 原因 |
|------|:----:|------|
| 单文档检索 | +6% | 找文档更精准 |
| **跨文档分析** | **+12%** | 多步检索覆盖更多文档 |
| **框架分析 (SWOT/PEST)** | **+24%** | 正确选工具 + 框架 |
| 多步推理 | +5% | 基线已强，Agent 更稳定 |
| **联网搜索** | **+12%** | 真实 DuckDuckGo 调用 |

> 最大提升在"纯 RAG 做不到"的任务：跨文档分析、框架推理、联网搜索。
> 7 个失败案例均为 L2 歧义/边界问题（基础设施噪声为 0）。

### 优化历程

```
v1: 46% 覆盖率 · 8/30 完成 · 89s 平均 · 1.0 工具失败
                              ↓
        23 个百分点的提升全部来自工程修复，
        不是换模型、不是改提示词
                              ↓
v2: 69% 覆盖率 · 18/30 完成 · 36s 平均 · 0.0 工具失败
```

---

## 🏗 系统架构速览

```
┌─ 表现层 ──────────────────────────────────────┐
│  Vue 3 + Naive UI + ECharts + Vue Flow        │
├─ API 网关 ─────────────────────────────────────┤
│  FastAPI + JWT + CORS + SSE                   │
├─ AI Agent 核心 ────────────────────────────────┤
│  PER Loop | Tool Registry | Context Engine     │
│  RAG Pipeline | Knowledge Graph | Workflow     │
├─ AI / LLM ─────────────────────────────────────┤
│  DeepSeek V4 | Embedding | Reranker | Langfuse │
├─ 数据存储 ──────────────────────────────────────┤
│  MySQL 8 | ES 8 | Redis 7 | Kafka | MinIO     │
└────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 前置要求
- Docker Desktop（推荐）或 Python 3.11+ / Node.js 18+ / MySQL 8 / Redis 7 / ES 8 / Kafka / MinIO

### 1. 克隆
```bash
git clone https://github.com/sijie-Z/DocMind-RAG.git
cd DocMind-RAG
```

### 2. 启动基础设施
```bash
cd backend && docker compose up -d
```

### 3. 配置
```bash
cp .env.docker.example .env.docker
# 编辑 .env.docker，填入 API Key
```

### 4. 启动后端
```bash
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 启动前端
```bash
cd frontend && npm install && npm run dev  # 端口 5173
```

### 6. 访问
| 地址 | 说明 |
|------|------|
| http://localhost:5173 | 前端界面 |
| http://localhost:8000/docs | Swagger API 文档 |
| http://localhost:8000/health | 健康检查 |

### 演示账号
| 用户名 | 密码 | 角色 |
|--------|------|------|
| `guest` | `123456` | 普通用户 |
| `admin` | `admin123` | 管理员 |

### 运行评测
```bash
python -m benchmark.run --questions benchmark/questions/v2.json --mode baseline   # 纯 RAG
python -m benchmark.run --questions benchmark/questions/v2.json --mode agent      # PER Agent
python -m benchmark.run --compare benchmark/results/baseline_v2.json benchmark/results/agent_v2.json
```

---

## 📁 项目结构

```
DocMind/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # REST API (17 模块)
│   │   ├── agent/                # PER Agent 核心
│   │   │   ├── loop.py           #   PER 主循环
│   │   │   ├── planner.py        #   规划器
│   │   │   ├── executor.py       #   执行器
│   │   │   ├── reflector.py      #   反思器
│   │   │   ├── registry.py       #   工具注册表
│   │   │   ├── experience/       #   经验记忆 (🆕)
│   │   │   ├── replay/           #   执行回放 (🆕)
│   │   │   ├── mining/           #   模式挖掘 (🆕)
│   │   │   └── tools/            #   25+ 工具实现
│   │   ├── core/                 # 基础设施
│   │   ├── rag/                  # RAG 管道
│   │   └── worker/               # Kafka 异步处理
│   ├── tests/                    # 422+ 测试用例
│   └── benchmark/                # 30 题评测框架 (🆕)
├── frontend/src/                 # Vue 3 前端
└── docs/
    ├── architecture.html         # 交互式架构图
    └── product-definition.md     # 产品定义
```

---

## 🧪 测试

```bash
cd backend
python -m pytest tests/ -v --tb=short
python -m pytest tests/ --cov=app --cov-report=html
make test && make lint
```

## 🚢 部署

- **Docker Compose**：`cd backend && docker compose up -d`
- **Kubernetes**：`kubectl apply -f deploy/k8s/`
- **手动**：见 `deploy/README.md`

---

## 📝 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| **v1.2.1** | 2026-05 | 稳定性修复、并行执行、页面过渡动画 |
| **v1.2.0** | 2026-05 | PER 架构、25+ 工具、自我进化、深度分析 |
| **v1.1.0** | 2026-05 | Agent 模式、示例文档、CJK 分词修复 |
| **v1.0.0** | 2026-05 | 初版：RAG 管道、工作流编辑器、知识图谱 |

---

## 🔗 链接

- **架构图**：https://sijie-z.github.io/DocMind-RAG/architecture.html
- **GitHub**：https://github.com/sijie-Z/DocMind-RAG
- **API 文档**：http://localhost:8000/docs
- **Issue**：https://github.com/sijie-Z/DocMind-RAG/issues

---

<p align="center">
  <strong>DocMind</strong> — 基于 PER 架构的企业级 AI Agent 系统
  <br>
  <sub>Built with ❤️ by the DocMind Team</sub>
</p>
