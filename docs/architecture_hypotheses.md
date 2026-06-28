# DocMind 架构决策验证表

> 基于 2026 年 6 月的六轮架构讨论生成。
> 
> 核心原则：**所有架构决策必须基于数据，而非直觉。**
> 在收集数据之前，停止新增 Agent 能力，停止架构重构，先验证现有组件是否创造价值。

---

## 一、Planner 的价值验证

### 假设

> Planner（LLM 规划 + 规则模板）比直接调用 Executor 能提升任务成功率。

### 验证指标

| 指标 | 当前状态 | 验证方法 |
|------|----------|----------|
| `planner_success_rate = planner_success_total / planner_runs_total` | ❌ 缺失 | 新增 `planner_success_total`，在 planner 完成后标记成功/失败 |
| `task_success_with_planner` | ❌ 缺失 | 追踪一次完整 PER 循环的最终状态 |
| `avg_steps_per_plan` | ✅ 有（`planner_plan_steps` histogram 可加） | 已有 `AGENT_PLANNING_TOTAL` 但无步骤数统计 |
| `planner_duration_p50/p95/p99` | ✅ 部分有（`AGENT_PLANNING_LATENCY` Histogram） | 已存在，确认 buckets 覆盖范围合适 |

### 成功标准

- **保留 Planner**：启用 Planner 时任务成功率 ≥ 未启用时 +10%
- **简化为 Router**：成功率差距 < 5%，且 Planner 耗时占总耗时 > 15%
- **模板 vs LLM**：规则模板（`_try_structured_planning`）和 LLM Planner 的成功率需分开统计——可能模板有效而 LLM 无效（或反之）

### 需要的代码改动
1. `AGENT_PLANNING_SUCCESS` counter → `planner.py` 中新增
2. `AGENT_PLANNING_MODE` counter with label `mode=structured|llm|none` → `planner.py`
3. `AGENT_PLAN_STEPS` histogram → `planner.py` 记录 steps len
4. **任务级别的 outcome label** 关联 planner 是否启用

---

## 二、Reflector 的价值验证

### 假设

> Reflector 的 retry 决策能修复执行错误，且修复的成功率足够高（>50%）。

### 验证指标

| 指标 | 当前状态 | 验证方法 |
|------|----------|----------|
| `reflector_fix_rate = reflector_fix_success_total / reflector_retry_triggered_total` | ❌ 缺失 | 核心指标。需追踪 retry 后步骤是否成功 |
| `reflector_decision_distribution` | ✅ 部分有（`AGENT_REFLECTION_DECISIONS` label=decision） | 已有 pass/retry/replan 的计数 |
| `reflector_retry_success` | ❌ 缺失 | 需要知道 retry 之后该步骤是否变成了 completed |
| `avg_retries_per_trigger` | ❌ 缺失 | 一次 retry 决策平均导致多少次重试 |
| `reflector_pass_rate_on_all_completed` | ❌ 缺失 | 当所有步骤已完成时，Reflector 结论是 pass 还是 retry（用于检测误判） |

### 成功标准

- **保留 Reflector**：fix_rate ≥ 60%，且 reflector 本身耗时 < 总耗时 10%
- **降级为轻量检查**：fix_rate 在 30%-60% 之间，保留 quick_pass 检查，去掉 LLM reflection
- **删除**：fix_rate < 30%，或 reflector 耗时 > 总耗时 20%

### 需要的代码改动
1. `AGENT_REFLECTION_FIX_SUCCESS` counter → `loop.py` 中 retry 成功后 inc
2. `AGENT_REFLECTION_FIX_FAILED` counter → 同上失败时 inc
3. `AGENT_REFLECTION_LATENCY` histogram → `reflector.py`
4. 需要将 reflector 的决策 ID 与 executor 的步骤完成事件关联

---

## 三、Reviewer 的价值验证

### 假设

> Reviewer（抗辩审查）能发现 Reflector 和 QualityGate 遗漏的真实问题。

### 验证指标

| 指标 | 当前状态 | 验证方法 |
|------|----------|----------|
| `reviewer_reject_rate = reviewer_reject_total / reviewer_runs_total` | ❌ 缺失 | 新增 counter |
| `reviewer_true_positive_rate` | ❌ 缺失 | 需要人工标注或用户反馈确认 |
| `reviewer_false_positive_rate` | ❌ 缺失 | 用户标记 "这不是问题" 或忽略的审查意见 |
| `reviewer_severity_distribution` | ❌ 缺失 | 高/中/低严重度的分布 |
| `reviewer_duration` | ❌ 缺失 | LLM 调用耗时 |

### 成功标准

- **保留**：true_positive_rate ≥ 40%，且平均每周发现至少 1 个高严重度真实问题
- **删/合**：true_positive_rate < 20%，或 100% 误报

### 需要的代码改动
1. `AGENT_REVIEW_RUNS_TOTAL` counter → `reviewer.py`
2. `AGENT_REVIEW_FINDINGS_TOTAL` counter with label `severity=high|medium|low` → `reviewer.py`
3. `AGENT_REVIEW_LATENCY` histogram → `reviewer.py`
4. 用户反馈机制标记 true/false positive（可通过 AgentFeedback API）

---

## 四、QualityGate 的价值验证

### 假设

> Quality gate 能拦截低质量结果，且误报率可控。

### 验证指标

| 指标 | 当前状态 | 验证方法 |
|------|----------|----------|
| `quality_gate_reject_rate = quality_gate_reject_total / quality_gate_runs_total` | ❌ 缺失 | 已有 quality_gate 逻辑但无 metrics |
| `quality_gate_issue_distribution` | ❌ 缺失 | A/B/C/F 等级的分布 |
| `quality_gate_correlation_with_user_satisfaction` | ❌ 缺失 | quality_gate 拦截后，用户反馈是否正面 |
| `quality_gate_duration` | ❌ 缺失 | 检查耗时 |

### 成功标准

- **保留**：reject_rate 在 5%-20% 之间，且用户反馈中与 QG 相关的不满 < 1%

### 需要的代码改动
1. `AGENT_QUALITY_GATE_RUNS_TOTAL` counter → `quality_gate.py`
2. `AGENT_QUALITY_GATE_REJECTED_TOTAL` counter with label `grade=A|B|C|F` → `quality_gate.py`
3. `AGENT_QUALITY_GATE_FATAL_TOTAL` counter → `quality_gate.py`

---

## 五、Agent as Tool 的价值验证（Phase 2）

### 假设

> 将子代理注册为工具，比硬编码 API 调用（`subagent.delegate_task`），能降低未来扩展一个子代理的平均成本。

### 验证指标

| 指标 | 当前状态 | 验证方法 |
|------|----------|----------|
| `subagent_addition_cost_hours` (新增一个子代理的人力成本) | ❌ 无基线 | 记录第一次硬编码和第一次注册式的耗时 |
| `subagent_invocation_pattern` | ❌ 缺失 | 子代理何时、为何被调用 |
| `parent_agent_awareness_rate` | ❌ 缺失 | 父代理在什么情况下自主决定调用子代理 vs 人类安排 |

---

## 六、现有 Metrics 仓位的诊断

### 已有（可以支撑部分验证）

| 指标 | 类型 | 用于验证 |
|------|------|----------|
| `AGENT_PLANNING_TOTAL` | Counter | Planner 使用频率（但缺少 outcome label） |
| `AGENT_PLANNING_LATENCY` | Histogram | Planner 耗时 |
| `AGENT_EXECUTION_STEPS` | Counter | 执行步骤数（但缺少与 planner 的关联） |
| `AGENT_TOOL_CALLS` | Counter | 工具调用次数/成功率（已有 tool + result labels） |
| `AGENT_TOOL_LATENCY` | Histogram | 工具调用耗时 |
| `AGENT_REFLECTION_DECISIONS` | Counter | 反射决策分布 |
| `AGENT_MEMORY_RECALLS` | Counter | 记忆召回尝试/结果 |
| `AGENT_FEEDBACK_TOTAL` | Counter | 用户反馈量 |

### 缺失（必须新增才能回答核心假设）

| 指标 | 缺失的影响 |
|------|-----------|
| Planner success/failure outcome | 无法计算 planner success_rate |
| Reflection fix success/failure | 无法计算 reflector fix_rate |
| QualityGate pass/reject/fatal | QualityGate 完全不可观测 |
| Reviewer runs/findings/latency | Reviewer 完全不可观测 |
| **Task-level success/failure** | 无法将 planner、executor、reflector 的指标关联到同一个任务 |

### 核心缺失：无对照组 = 无法验证因果

最大的问题不是缺少 trace_id，而是**缺少对照组**。

当前所有任务都走 PER 路径。即使给所有指标加上 trace_id，也只能知道"PER 任务的成功率 = X%"，无法知道"没有 Planner 时成功率是多少"。

trace_id 解决的是"同一个任务内组件如何关联"，但它回答不了"这个组件是否创造了增量价值"。后者需要实验设计，不是 tracing 能解决的问题。

所以修复顺序是：
1. **先定义 TaskOutcome** — 确定观测的目标函数
2. **再关联组件** — trace_id 传播到 Langfuse（不是 Prometheus！）
3. **最后设计 A/B 实验** — 创造对照组来验证因果

---

## 七、第一阶段四个 Dashboard

### Dashboard 1：Agent Cost
- **每个调用的 LLM Token 消耗**（Plan + Execute + Reflect + Review 各自占比）
- **每个调用的端到端延迟**（分位数 P50/P95/P99）
- **工具调用分布**（哪个工具被调最多、哪个最慢、哪个最容易失败）

### Dashboard 2：Agent Value
- **按组件拆分的成功率**
  - `Planner`: plan 后的 task success_rate vs 未 plan
  - `Reflector`: fix_rate
  - `Reviewer`: findings_per_run, true_positive_rate（人工标注后）
- **组件耗时占比**（Planning 时间 / 总时间，Reflection 时间 / 总时间）

### Dashboard 3：Guarantee
- **权限拒绝次数**（按工具、按用户）
- **QualityGate pass/reject/fatal 分布**
- **重试次数分布**（哪些工具最常重试）
- **审批等待时间**（如果有审批环节）

### Dashboard 4：Failure
- **失败原因 Top 10**
- **工具错误 Top 10**
- **重试原因 Top 10**
- **任务失败率趋势**

---

## 八、实施路线

### 关键前提：实验设计的挑战

在开始实施前，需要认识到一个根本问题：

> **所有任务目前都走 PER。没有自然形成的对照组。**

当前没有"只走 Executor 不走 Planner"的任务。这意味着即使加了所有指标，也只能知道"PER 路径下的成功率 = X%"，不能知道"去掉 Planner 后的成功率 = X - Y%"。

需要设计实验来创造对照组：
- **方案 A**：随机采样 10% 的任务走 Direct Route（跳过 Planner/Reflector）。缺点是影响用户体验。
- **方案 B**：在测试环境对历史任务重放（Replay），用不同配置跑同一批任务做对比。缺点是重放不能反映真实 LLM 的随机性。
- **方案 C**：用 `AGENT_FEEDBACK_TOTAL` + `TaskOutcome` 做相关性分析（非因果）。缺点是只能做相关性，不是因果。

**建议**：先用方案 C（低成本）跑 2 周收集基线，再方案 A（高风险）跑 1 周做因果验证。

### Phase A：TaskOutcome 模型（1-2 天）

**不在代码里加一行指标代码。先定义什么是"任务成功"。**

创建 `task_outcome.py`，包含：

```python
class TaskOutcome:
    task_id: str
    query: str
    status: TaskStatus         # SUCCESS / PARTIAL / FAILURE / REJECTED / INTERRUPTED / TIMEOUT
    failure_stage: FailureStage  # INPUT / PLANNING / EXECUTION / REFLECTION / REVIEW / QUALITY_GATE
    failure_reason: str
    planner_enabled: bool
    reflector_enabled: bool
    reviewer_enabled: bool
    quality_gate_enabled: bool
    total_tokens: int
    total_duration_ms: float
    tool_call_count: int
    tool_error_count: int
    retry_count: int
```

这个模型统一了所有组件的输出格式。后面的所有分析都基于它。

**TaskOutcome 已经存在**（刚刚写入 `backend/app/agent/task_outcome.py`）。

### Phase B：TaskOutcome 接入 Loop（1 天）

在 `PERAgentLoop.run()` 结尾创建 TaskOutcome 并保存：

```python
outcome = TaskOutcome.from_context(ctx)
outcome.record_component("planner", enabled=config.enable_planning, invoked=True, ...)
outcome.record_component("reflector", enabled=config.enable_reflection, invoked=True, ...)
if outcome.failures:
    outcome.mark_failure(...)
else:
    outcome.mark_success()
await outcome.save()
```

### Phase C：低基数 Prometheus 指标（1 天）

在 `prometheus.py` 新增**聚合指标**（不是 trace_id！）：

```python
AGENT_TASK_OUTCOME = Counter("agent_task_outcome_total",
    "Task final status", ["status", "failure_stage", "planner", "reflector", "reviewer"])
```

这个 label 集最多 5 (status) × 10 (stage) × 2 × 2 × 2 = **400 个组合**，Prometheus 可以承受。

### Phase D：高基数 Trace 走 Langfuse（1 天）

trace_id / session_id / task_id 这些高基数标签不进 Prometheus，进 Langfuse：

```python
# PERAgentLoop.run() 开头
span = langfuse.span(name="agent_task", trace_id=trace_id, ...)
# 各组件作为子 span
planner_span = langfuse.span(name="planner", parent=span, ...)
executor_span = langfuse.span(name="executor", parent=span, ...)
```

### Phase E：A/B 测试（第 3-4 周）

基于 TaskOutcome 做实验：

```
Group A: PER (current)     — 当前配置
Group B: Direct            — 跳过 Planner，Executor 直接调用工具
Group C: PER + Review      — 完整 PER + Reviewer
```

对比三个组的 TaskOutcome.status 分布、平均延迟、Token 消耗。

### 总结

```
Phase A → TaskOutcome 模型（已完成）
Phase B → TaskOutcome 接入 Loop（1 天）
Phase C → 低基数 Prometheus 指标（1 天）
Phase D → Langfuse root trace（1 天）
Phase E → A/B 实验设计（第 3-4 周，需真实流量）
```

---

## 附录：为什么不先做 XYZ

### 为什么不先做 Intent Router？

因为 Intent Router 的前提是知道各执行模式（Router / PER / High-Risk）的收益差异。当前没有数据支持这种分类。

### 为什么不先做 Governance Engine？

因为 Governance 的前提是有规则、有流量、有数据。当前规则在代码里零散分布，流量未知，数据缺失。

### 为什么不先删 PER？

PER 的价值未知 ≠ PER 没有价值。删除一个无数据支撑的功能和新增一个功能一样危险。

### 为什么 Agent as Tool 可以提前做（在 Phase 1 之后）？

因为 Agent as Tool 与现有架构不冲突，且影响的是未来扩展成本，不影响当前组件的价值评估。
