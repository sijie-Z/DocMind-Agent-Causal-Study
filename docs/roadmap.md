# DocMind: 面试就绪路线图

> 目标：一个可部署、可观测、可验证的 PER Agent 项目。
>
> 面试官能访问、能截图、能讲出 trade-off。

---

## 路线图概览

```
S1  部署上线            Week 1    服务器 + Docker + 域名
S2  Langfuse            Week 2    全链路 Trace             ✅ 代码完成
S3  Benchmark           Week 3    10 题基线 → 逐步扩到 30+  ✅ 代码完成
S4  ExecutionContext    Week 4    状态收拢，仅记录不注入      ✅ 代码完成
S5  Skill Layer         Week 5    Skill 作为 Tool          ✅ 代码完成
S6  Failure Collection    Week 6    案例分类 + Langfuse 链接   ✅ 代码完成
S7  MCP Bridge          Week 7    官方 SDK，轻量接入       ✅ 代码完成
```

---

## S1 · 部署上线

**目标**：`https://docmind.xxx.com` 可访问，Agent 对话可用。

**待办**：
- [ ] 注册云服务器（阿里云/腾讯云学生机）
- [ ] 域名 + ICP 备案（或境外服务器免备案）
- [ ] Docker Compose 一键启动
- [ ] 前端配置 API 地址指向后端
- [ ] HTTPS（Let's Encrypt / Cloudflare）
- [ ] README 添加线上链接

---

## S2 · Langfuse Tracing

**目标**：每轮 Agent 请求在 Langfuse Dashboard 上呈现完整 trace。

**做法**：
- 装 `langfuse` Python SDK
- 在 5 个位置加 `@observe()` 埋点：

| 位置 | 文件 | as_type |
|---|---|---|
| `planner.plan()` | `planner.py` | `"planning"` span |
| `executor._execute_step_once()` | `executor.py:326` | `"execute_step"` span |
| `tool_registry.execute()` | `registry.py:95` | `"tool_call"` tool |
| `reflector.reflect()` | `reflector.py` | `"reflection"` span |
| `memory_bridge.get_context_for_query()` | `memory_bridge.py:78` | `"memory_recall"` tool |

**交付**：README 放入 Langfuse Trace 截图

**待办**：
- [x] `pip install langfuse` + 初始化
- [x] 5 个埋点（registry / memory / planner / executor / reflector）
- [ ] 验证 trace 树完整（需部署后测试）
- [ ] 截图（需部署后测试）

---

## S3 · Benchmark（10 题基线）

**目标**：先跑通评测流水线，得到完成率 + 关键词覆盖率。

**类别分布**（第一版）：

| 类别 | 题数 |
|---|---|
| 单文档检索 | 3 |
| 跨文档分析 | 2 |
| 框架分析 | 2 |
| 多步推理 | 2 |
| 外部搜索 | 1 |

**每条问题格式**：

```json
{
    "id": "B001",
    "category": "single_doc",
    "question": "...",
    "source_docs": ["doc_id"],
    "expected_keywords": ["毛利率", "成本"],
    "difficulty": "easy"
}
```

**指标**：
- 完成率 = count(非空回答) / total
- 关键词覆盖率 = count(匹配关键词) / count(总关键词)
- 平均步骤数
- 工具失败率

**用法**：

```bash
python -m app.agent.benchmark --questions benchmark/v1.json --output benchmark/results/v1.json
```

**阶段性目标**：

```
Phase 1 (S3):  10 题，跑通流水线
Phase 2 (S6):  30 题，加入 Skill 后对比
Phase 3 (未来): 50+ 题，覆盖全场景
```

**待办**：
- [x] 设计 10 条测试问题（`benchmark/questions/v1.json`）
- [x] 实现评测运行器 + 评分器（`benchmark/run.py` + `benchmark/scorer.py`）
- [ ] 跑出基线数据（需部署后测试）
- [ ] 写入 README（需部署后测试）

---

## S4 · ExecutionContext

**目标**：把散落在各模块的状态收拢到一个对象。

**新文件**：`app/agent/exec_context.py`

```python
@dataclass
class ExecutionContext:
    task_id: str
    query: str
    goal: str = ""
    current_step_id: str | None = None
    completed_steps: list[StepRecord] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)
    progress: float = 0.0
    total_tokens: int = 0
    start_time: float = ...
    duration_ms: float = 0.0
```

**流经管道**：`loop.py` 创建 → 传入 planner → 传入 executor → 传入 reflector

**原则**：第一阶段 **只记录，不注入 prompt**。
- 先验证状态收拢成功
- Langfuse 能看到 ctx 内容
- Benchmark 能统计 ctx 数据
- 稳定后再考虑 `ctx.format_prompt() → system prompt`

**待办**：
- [ ] 实现 `ExecutionContext` dataclass
- [ ] `loop.py` 创建 ctx 并向下传递
- [ ] `executor._execute_step_once()` 写入 findings / failures / decisions
- [ ] `reflector.reflect()` 写入 decisions
- [ ] Langfuse 观察 ctx 数据

---

## S5 · Skill Layer

**目标**：Tool 之上加一层 Skill 编排。

**原则**：V1 不做自动匹配，Skill 本身作为 Tool 注册。

```python
@register_tool(name="deep_research", ...)
async def deep_research(query: str, ...) -> str:
    # 内部编排 search_kb + extract_insights + generate_report
```

这样 Planner 完全不需要修改——LLM 看到 "deep_research" 在工具列表里，想用就会用。

**三个 Skill**：

| Skill | 编排链路 |
|---|---|
| `deep_research` | web_search → search_kb → extract_insights → 结构化摘要 |
| `document_comparison` | 分别 search_kb → extract_insights → cross_document_analysis |
| `knowledge_analysis` | search_kb → extract_insights(framework) → generate_report |

**待办**：
- [ ] 实现 `deep_research` 工具
- [ ] 实现 `document_comparison` 工具
- [ ] 实现 `knowledge_analysis` 工具
- [ ] Benchmark 对比：有无 Skill 的完成率/准确率变化

---

## S6 · 扩 Benchmark

**目标**：10 → 30 题。

**新增类别**（按优先级）：
- 多轮追问
- 含外部搜索的复杂推理
- 含失败恢复的场景
- 边界情况（空文档、无结果）

**交付**：生成 Skill Layer 前后的对比报告，写入 README。

**待办**：
- [ ] 扩到 30 题
- [ ] 跑 Skill Layer 前后的对比数据
- [ ] 写入 README

---

## S7 · MCP Bridge

**目标**：简历能写"兼容 MCP 协议"，面试能回答 MCP 相关问题。

**做法**：使用官方 `mcp` Python SDK，不要手写 JSON-RPC。

```python
@register_tool(name="mcp_call", ...)
async def mcp_call(server_name: str, tool_name: str, arguments: dict) -> str:
    # 通过 mcp SDK 的 stdio client 调用外部 MCP Server
```

**验证**：接入 GitHub MCP Server，能调 `search_repositories` 等工具。

**不做的范围**：
- ❌ MCP Server 注册中心（硬编码 2-3 个）
- ❌ 热加载（配置在 `.env` 里）
- ❌ 流式传输

**待办**：
- [ ] 调研 `mcp` Python SDK 的 stdio client 用法
- [ ] 实现 `mcp_call` 工具
- [ ] 配置 GitHub MCP Server 验证
- [ ] 写入 README

---

## 面试叙事

### 为什么不做 MCP？（面试高频问题）

> MCP 解决的是工具标准化接入问题。我当前的工具主要是内部知识库和分析能力，工具数量有限，因此优先投入了 Skill Layer（工作流编排）、Observability（Langfuse 全链路追踪）、Benchmark（效果评测）这些直接提升 Agent 能力和可维护性的方向。当工具生态扩展到大量外部系统时，MCP 会是自然演进方向——架构中已经预留了 mcp_call 桥接工具。

### 为什么不做长期 Runtime？

> 我的场景是知识问答，任务生命周期通常在 30 秒以内，请求-响应模型已经足够。Claude Code 那种持续运行的 Runtime 更适合代码执行场景——两者的问题域不同，不是代际差距，是 trade-off。

### 如何证明 Agent 比 RAG 好？

> 我建了一个 30 题的评测集，覆盖单文档检索、跨文档对比、框架分析、多步推理等场景。PER Agent 相比纯 RAG 的完成率提升 X%，关键词覆盖率提升 X%。每加一个模块我都重新跑评测，用数据验证有效。

---

## 修改历史

| 日期 | 版本 | 修改 |
|---|---|---|
| 2026-06-11 | v1 | 初稿 |
