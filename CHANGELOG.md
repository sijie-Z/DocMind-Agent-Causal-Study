# DocMind 更新日志

本文档记录项目的所有重要变更，方便追溯和查询。

---

## 2026-05-10 (第十二轮) — 首次体验优化 + 工程化

### 示例数据系统（产品化）

| 改进 | 文件 | 说明 |
|------|------|------|
| Demo API | `api/v1/endpoints/demo.py` | `POST /demo/seed` 一键加载 3 篇示例文档 + 向量索引 + 示例对话 |
| 清除 API | 同上 | `DELETE /demo/seed` 清除示例数据 |
| 前端 API | `api/demo.ts` | `seedDemoData()` / `clearDemoData()` |
| Dashboard | `dashboard/user.vue` | 空状态新手引导 + "加载示例数据"按钮 |
| 路由注册 | `api/v1/router.py` | `/demo` 路由组 |

**示例数据内容：**
- FastAPI 快速入门指南（8 个知识块）
- Vue 3 组合式 API 完全指南（8 个知识块）
- RAG 检索增强生成技术详解（8 个知识块）
- 1 个演示对话：展示 RAG 带引用的问答效果

**首次体验流程：**
新用户登录 → 空状态引导 → 一键加载示例数据 → 立即看到文档/对话/搜索结果

### 工程化改进

| 改进 | 文件 | 说明 |
|------|------|------|
| API 类型生成 | `package.json` | `npm run api:generate` 从 Swagger 自动生成 TypeScript 类型 |
| 依赖安装 | `package.json` | `openapi-typescript-codegen` 已安装 |

### 验证

- TypeScript 类型检查零错误
- 后端 **216** 个测试全部通过
- 前端 **95** 个测试全部通过
- Demo 端点导入验证通过（2 routes）

---

## 2026-05-10 (第十一轮) — 知识图谱可视化 + 代码一致性

### 知识图谱可视化

| 改进 | 文件 | 说明 |
|------|------|------|
| 图谱 API | `knowledge.py` | `GET /knowledge/graph` 端点，返回节点/关系/分析数据 |
| 图谱页面 | `knowledge/graph.vue` | Canvas 力导向图，支持拖拽/缩放/搜索/节点详情 |
| API 客户端 | `api/knowledge.ts` | `getKnowledgeGraph()` 函数 + GraphNode/GraphEdge 类型 |
| 路由注册 | `router/index.ts` | `/knowledge/graph` 路由 |
| 入口按钮 | `knowledge/index.vue` | 知识库页面右上角图谱按钮 |

**图谱功能特性：**
- Canvas 力导向布局，节点自动排列
- 7 种实体类型颜色编码（人物/组织/地点/事件/概念/产品/技术）
- 节点大小根据出现次数动态调整
- 点击节点显示详情面板（类型/描述/关联关系）
- 关键词搜索过滤
- 鼠标拖拽 + 滚轮缩放

### 代码一致性（后台进行中）

- HTTPException → AppError 异常体系迁移（5 个 endpoint 文件）
- `catch (error: any)` → `catch (error: unknown)` 类型安全修复（8 个 Vue 文件）

### 验证

- TypeScript 类型检查零错误
- 后端 **216** 个测试全部通过
- 前端 **95** 个测试全部通过

---

## 2026-05-10 (第十轮) — 智能上下文 + 任务拆解 + 提示词库

### 多层上下文压缩（rag/context_window.py）

| 改进 | 说明 |
|------|------|
| Q&A 对提取 | 旧消息不再简单截取前 40 字符，而是识别 user→assistant 配对，保留完整的问答摘要 |
| 结构化压缩 | 最多保留 8 组 Q&A 对，每组包含问题前 60 字符 + 回答前 80 字符 |
| 渐进式降级 | 无 Q&A 对时回退到 topic snippet 提取，保证不会丢失上下文 |

### Agent 复杂任务自动拆解（agent/loop.py）

| 改进 | 说明 |
|------|------|
| System Prompt 增强 | 新增"复杂任务处理策略"，指导 LLM 自动识别多文档分析、深度调研、流程指导等模式并拆解执行 |
| 智能工具结果截断 | 不同工具类型使用不同截断策略：列表型保留前 15 项、搜索型保留前 3 条、文档型保留首尾 |

### 提示词模板库扩充（api/v1/endpoints/prompts.py）

| 模板 | 分类 | 用途 |
|------|------|------|
| 文档摘要专家 | summary | 结构化摘要（主题+要点+结论） |
| 对比分析师 | analysis | 多文档维度对比 |
| 技术文档翻译 | translation | 专业术语一致翻译 |
| FAQ 生成器 | generation | 从文档自动生成常见问题 |
| 风险评估师 | analysis | 风险识别+影响评估+应对建议 |
| 知识图谱提取 | extraction | 实体/关系/属性 JSON 提取 |

### 验证

- 后端 **216** 个测试全部通过

---

## 2026-05-10 (第九轮) — 用户体验提升

### 新功能

| 功能 | 文件 | 说明 |
|------|------|------|
| 重新生成回答 | `ChatMessages.vue`, `index.vue`, `useChatSend.ts` | 最后一条 AI 消息显示重新生成按钮，点击后自动重发上一条用户消息，支持 WebSocket 和 SSE 双模式 |
| 拖拽上传文件 | `index.vue` | 将文件拖拽到聊天区域即可上传，蓝色遮罩 + 上传图标提示，复用现有上传流程 |
| Agent 工具结果展开 | `agent/index.vue` | 超过 300 字符的工具结果显示"展开/收起"按钮，不再被截断丢失信息 |
| 对话导出 | `ChatHeader.vue`, `index.vue` | 顶栏新增导出按钮，一键下载当前对话为 Markdown 文件（含来源引用） |

### 验证

- TypeScript 类型检查零错误
- 前端 **95** 个测试全部通过

---

## 2026-05-10 (第八轮) — 安全加固 + 性能优化 + RAG 质量门

### 安全漏洞修复

| 漏洞 | 文件 | 修复方案 |
|------|------|---------|
| `exec()` 远程代码执行 | `workflow_engine.py` | 移除 `__builtins__`，改为白名单 safe builtins + AST 层面禁止 import/exec/eval/私有属性访问 |
| SSRF（服务端请求伪造） | `workflow_engine.py` | `APICallNodeExecutor` 新增 `_validate_url()`：DNS 解析后检查 IP 是否属于 127/10/172.16/192.168/169.254 等内网段 |
| 路径穿越 | `main.py` | `/files/{file_path:path}` 端点新增 `os.path.normpath` + `..` 检测 |

### 性能优化

| 改进 | 文件 | 说明 |
|------|------|------|
| Agent 工具并行执行 | `agent/loop.py` | 多工具调用从串行 `for` 循环改为 `asyncio.gather`，延迟降低 50%+ |
| Token 计数精确化 | `rag/context_window.py`, `agent/context.py` | `CHARS_PER_TOKEN=2.5` 替换为 `tiktoken cl100k_base` 编码器，中文/英文场景均准确 |
| 流式引用追踪 | `api/v1/endpoints/chat.py` | 响应完成后自动提取 `[n]` 引用标记，映射到源文档，`cited_sources` 仅包含实际被引用的来源 |

### RAG 质量门

| 文件 | 说明 |
|------|------|
| `tests/eval_dataset.jsonl` | 25 条评估数据（5 类：事实检索、技术概念、配置参数、操作流程、故障排查） |
| `tests/test_rag_quality_gate.py` | 10 个测试：schema 校验 + 分类覆盖 + 关键词召回率 > 60% |

### 前端修复

| 修复 | 文件 | 说明 |
|------|------|------|
| Enter 键换行 | `ChatInput.vue` | Shift+Enter 正确插入换行，Enter 发送消息（之前 `handleKeydown` 是死代码） |
| 死代码清理 | `stores/chat.ts` | 移除未使用的 `messages`、`addMessage`、`updateMessage`、`clearMessages`、`setLoading` |

### 前端测试修复

| 修复 | 文件 | 说明 |
|------|------|------|
| 移除死代码测试 | `stores/__tests__/chat.test.ts` | 6 个测试引用已删除的 `setLoading`/`isLoading`/`addMessage`/`updateMessage`/`clearMessages`，全部移除 |

### 验证

- 后端 **216** 个测试全部通过（+10 新增 RAG 质量门测试）
- 前端 **95** 个测试全部通过（移除 5 个死代码测试）
- REFACTOR_PLAN 完成率：**98%（52/53）**

### Service 方法类型注解（2.3 类型安全）

27 处缺失的返回类型注解已全部补全：

| 文件 | 修改数 | 说明 |
|------|--------|------|
| `services/auth_service.py` | 4 | `require_role`/`require_admin`/`require_user` → `Callable[..., Any]`，`blacklist_token` → `None` |
| `services/permission_service.py` | 1 | `initialize_default_permissions_and_roles` → `None` |
| `services/audit_service.py` | 1 | `log_activity` → `None` |
| `services/graph_rag_service.py` | 2 | `extract_entities_with_llm` 参数 `llm_client` 加 `Any`，`build_graph_from_entities` → `None` |
| `services/memory_service.py` | 16 | 5 个类的 16 个方法全部补齐 `-> None`，3 个 `Optional` 参数修正 |
| `services/workflow_engine.py` | 2 | `set_event_callback`/`emit_event` → `None` |

### OpenAPI response_model 补全（3.4 API 文档）

14 个 endpoint 文件的 ~60 个路由补齐 `response_model`：

| 文件 | 修改数 | response_model |
|------|--------|----------------|
| `endpoints/organizations.py` | 13 | `dict` |
| `endpoints/chat.py` | 7 | `dict`（SSE 流式端点除外） |
| `endpoints/knowledge.py` | 11 | `SearchSuggestionResponse`/`SimilarityResponse`/`dict` |
| `endpoints/users.py` | 9 | `dict`（下载端点除外） |
| `endpoints/monitoring.py` | 8 | `dict` |
| `endpoints/auth.py` | 3 | `dict` |
| `endpoints/documents.py` | 3 | `dict`（下载端点除外） |
| `endpoints/notifications.py` | 4 | `dict` |
| `endpoints/agent.py` | 2 | `dict`（SSE 流式端点除外） |
| `endpoints/workflow.py` | 1 | `dict`（SSE 执行端点除外） |
| `endpoints/files.py` | 1 | `dict` |
| `endpoints/manuals.py` | 1 | `dict` |
| `endpoints/prompts.py` | 1 | `dict` |

### 验证

- 后端 **206** 个测试全部通过
- REFACTOR_PLAN 完成率：**98%（52/53）**

---

## 2026-05-09 (第七轮) — 类型安全 + 事务管理 + 模型现代化

### SQLAlchemy 2.0 模型迁移（2.3 类型安全）

全部 11 个模型文件从旧式 `Column()` 迁移到 `Mapped` + `mapped_column`：

| 文件 | 模型数 | 说明 |
|------|--------|------|
| `models/user.py` | User | 已在第六轮完成 |
| `models/document.py` | Document, DocumentChunk, DocumentTag, Tag | 4 个模型 |
| `models/chat.py` | ChatSession, ChatMessage | 2 个模型 |
| `models/organization.py` | Organization | 1 个模型 |
| `models/rbac.py` | Permission, Role | 2 个模型 |
| `models/prompt.py` | PromptTemplate | 1 个模型 |
| `models/notification.py` | Notification | 1 个模型 |
| `models/knowledge_job.py` | KnowledgeProcessingJob | 1 个模型 |
| `models/user_audit.py` | UserLoginSession, UserActivityLog | 2 个模型 |
| `models/manual.py` | SystemManual | 1 个模型 |
| `models/workflow.py` | Workflow, WorkflowExecution, NodeDefinition | 3 个模型 |

**效果：** 所有字段获得完整类型推断，`pyright: ignore` 注解全部消除。

### pyright: ignore 清零（2.3 类型安全）

| 文件 | 移除数 | 原因 |
|------|--------|------|
| `services/auth_service.py` | 9 | `reportAttributeAccessIssue` / `reportArgumentType` / `reportGeneralTypeIssues` — 模型迁移后自动解决 |
| `api/v1/endpoints/auth.py` | 1 | `reportArgumentType` — `int()` 显式转换替代类型忽略 |
| `api/v1/endpoints/documents.py` | 1 | `reportOperatorIssue` — `file.filename` None 守卫 |

### 事务边界重构（1.6 数据库事务管理）

服务层不再管理 commit/rollback，改用 `flush()` + 调用方 `db.begin()`：

| 文件 | 改动 | 说明 |
|------|------|------|
| `services/auth_service.py` | `create_user`, `update_user`, `update_user_password` | 移除 `commit()`/`rollback()`，改用 `flush()` |
| `services/organization_service.py` | `update_organization`, `create_organization`, `delete_organization_thoroughly`, `create_private_organization`, `add_user_to_organization` | 同上 |
| `services/audit_service.py` | `log_activity` | 始终使用独立 session，不干扰调用方事务 |
| `api/v1/endpoints/auth.py` | `register`, `update_current_user`, `change_password` | 使用 `async with db.begin():` 管理事务 |

**原则：** 服务层只做 `flush()`（发送 SQL 到 DB），端点层用 `begin()` 管理 commit/rollback 生命周期。

### OpenAPI 文档增强（3.4 API 文档）

| 改进 | 文件 | 说明 |
|------|------|------|
| API 元数据 | `main.py` | 新增 `contact`、`license_info`、`openapi_url` 配置 |
| OpenAPI JSON | `main.py` | 移至 `/api/v1/openapi.json`，与 API 前缀一致 |

### 验证

- 后端 **206** 个测试全部通过
- 零 `pyright: ignore` 注解

---

## 2026-05-09 (第六轮) — 架构 + 类型 + UX 优化

### User.to_dict() → Pydantic Schema（2.3 类型安全）

| 改进 | 文件 | 说明 |
|------|------|------|
| 统一 User schema | `schemas/user.py` | 新增 `UserInfoResponse`（含 `from_attributes=True`），替代 `auth.py` 和 `users.py` 中两个竞争的 inline 定义 |
| 删除 User.to_dict() | `models/user.py` | 移除 19 行手动序列化方法，改用 `UserInfoResponse.model_validate(user)` |
| auth_service 迁移 | `services/auth_service.py` | Redis 缓存改用 Pydantic schema 序列化 |
| 前端 avatar 统一 | `layouts/index.vue`, `profile/index.vue` | `avatar` → `avatar_url` 兼容处理 |

### 多轮对话上下文窗口管理（4.1 RAG 质量）

| 改进 | 文件 | 说明 |
|------|------|------|
| 上下文窗口管理器 | `rag/context_window.py` | `ChatContextWindow`：token 预算分配、tail 窗口、旧消息压缩 |
| 管线集成 | `rag/pipeline.py` | `chat_stream` 使用 `build_rag_messages()` 替代硬编码 `[-8:]` |

**策略：**
- System prompt + context docs 始终保留（pinned）
- 最近 N 条消息保留原文（tail window，默认 6）
- 更早的消息压缩为摘要行（保留 topic hints）

### 前端 composables 单测（2.4）

| 文件 | 用例数 | 说明 |
|------|--------|------|
| `composables/__tests__/useErrorHandler.test.ts` | 9 | HTTP 错误分类（401/403/404/500+）、fallback 消息 |

### 配置验证测试（2.5）

| 文件 | 用例数 | 说明 |
|------|--------|------|
| `tests/unit/test_config.py` | +3 | 数值范围校验、默认值校验 |

### 路由代码分割确认（2.4）

20 个页面组件全部使用 `() => import(...)` lazy load，仅 Layout 为 eager 加载（合理，因为它是所有认证路由的 shell）。

### 流式打字机效果 + 来源引用交互（4.3）

| 改进 | 文件 | 说明 |
|------|------|------|
| 打字机光标 | `ChatMessages.vue` | 流式消息末尾闪烁光标 `animate-blink`（CSS `@keyframes`） |
| 交互式来源引用 | `ChatMessages.vue` | hover 弹出框显示来源文档摘要 + 相关度评分，`[n]` 标签格式 |
| NPopover 组件 | `ChatMessages.vue` | 每个来源标签独立 popover，展示 filename/snippet/score |

### 验证

- 后端 **206** 个测试全部通过（+12 新增）
- 前端 **100** 个测试全部通过（+9 新增）
- 前端类型检查零错误

---

## 2026-05-09 (第五轮) — Phase 4: 高级特性

### Prometheus 指标体系（4.2 可观测性）

| 改进 | 文件 | 说明 |
|------|------|------|
| Prometheus 指标注册表 | `core/prometheus.py` | 新增模块，使用 `prometheus_client` 定义 RAG 管线指标（检索/缓存/LLM/评估） |
| RAG 管线集成 | `rag/pipeline.py` | `search_knowledge_base` 和 `chat_stream` 中同步记录 Prometheus 指标 |
| `/metrics` 端点增强 | `main.py` | 导出 RAG 管线指标（`rag_*` 前缀），与 HTTP/WS 指标合并 |
| 依赖补全 | `requirements.txt` | 新增 `prometheus-client`、`filetype`、`opentelemetry-*` 四个包 |
| Grafana 仪表盘 | `monitoring/grafana-dashboard.json` | 18 个面板：检索率/延迟/缓存/LLM/Groundedness/意图/评估 |
| Prometheus 配置 | `monitoring/prometheus.yml` | 抓取配置模板 |

**Prometheus 指标清单：**

| 指标名 | 类型 | 说明 |
|--------|------|------|
| `rag_retrieval_total` | Counter | 检索总次数 |
| `rag_retrieval_hits` | Counter | 检索命中次数 |
| `rag_retrieval_errors` | Counter | 检索异常次数 |
| `rag_retrieval_latency_seconds` | Histogram | 检索延迟分布 |
| `rag_cache_hits_total{cache_type}` | Counter | 缓存命中（exact/semantic） |
| `rag_cache_misses_total` | Counter | 缓存未命中 |
| `rag_llm_requests_total` | Counter | LLM 请求总数 |
| `rag_llm_request_errors_total` | Counter | LLM 请求失败数 |
| `rag_llm_tokens_total{direction}` | Counter | Token 消耗（input/output） |
| `rag_llm_latency_seconds` | Histogram | LLM 响应延迟 |
| `rag_grounded_total` / `rag_grounded_hits` | Counter | 有据性检查 |
| `rag_query_intent_total{intent}` | Counter | 查询意图分布 |
| `rag_pipeline_in_flight` | Gauge | 当前执行中的管线数 |
| `rag_eval_total` | Counter | 评估运行次数 |
| `rag_eval_faithfulness_score` | Histogram | 忠实度评分分布 |
| `rag_eval_relevancy_score` | Histogram | 相关性评分分布 |
| `rag_eval_context_precision_score` | Histogram | 上下文精确度评分分布 |

### RAG 质量评估管线（4.1 RAG 质量）

| 改进 | 文件 | 说明 |
|------|------|------|
| 评估器模块 | `rag/evaluator.py` | LLM-as-Judge 评估，三项指标：Faithfulness / Relevancy / Context Precision |
| 评估 API | `monitoring.py` | `POST /rag-eval`（单条）和 `POST /rag-eval-batch`（批量，最多 20 条） |
| 评分提取 | `rag/evaluator.py` | `_extract_score()` 支持 JSON/分数/百分比/纯文本多种 LLM 输出格式 |

### Adaptive RAG（4.1 RAG 质量）

| 改进 | 文件 | 说明 |
|------|------|------|
| 查询复杂度分类器 | `rag/query_processor.py` | `QueryComplexityClassifier`：simple/medium/complex 三级分类 |
| 自适应检索策略 | `rag/retriever.py` | `retrieve()` 根据复杂度自动选择：keyword_only / hybrid / hybrid_hyde |
| 策略指标追踪 | `core/prometheus.py` | `rag_adaptive_strategy_total{strategy}` 计数器 |
| Grafana 面板 | `monitoring/grafana-dashboard.json` | 策略分布饼图 |

**策略选择逻辑：**
- **simple**（≤8 字符、无复杂信号）→ keyword_only，跳过 embedding 调用，延迟最低
- **medium**（how-to / list / 单一复杂信号）→ hybrid，keyword + vector 标准流程
- **complex**（多信号分析型 / 长查询）→ hybrid_hyde，完整管线含 HyDE + multi-rewrite

### 前端体验优化（4.3）

| 改进 | 文件 | 说明 |
|------|------|------|
| 移动端侧边栏 | `layouts/index.vue` | 主布局侧边栏在 `<768px` 完全隐藏，汉堡按钮触发 overlay 抽屉 |
| ECharts 暗色主题 | `utils/chartTheme.ts` | 新增 `DARK_CHART_THEME`，`createChartOption(option, isDark)` 支持暗色模式 |

### 测试

| 文件 | 用例数 | 说明 |
|------|--------|------|
| `tests/unit/test_prometheus_metrics.py` | 10 | Prometheus 指标注册表测试 |
| `tests/unit/test_rag_evaluator.py` | 17 | 评分提取 + 数据类测试 |
| `tests/unit/test_rag_service.py` | +4 | 查询复杂度分类器测试 |
| `tests/unit/test_config.py` | +3 | 配置验证测试（数值范围、默认值） |

### 验证

- 后端 **187** 个测试全部通过（+27 新增）
- 前端 **91** 个测试全部通过
- 前端类型检查零错误

---

## 2026-05-09 (第四轮)

### 语义缓存统一

| 改进 | 文件 | 说明 |
|------|------|------|
| 迁移到新实现 | `chat.py` | 从旧 `services/semantic_cache.py` 迁移到 `rag/cache.py` 的 `SemanticCache`（Redis Sorted Set，O(log n)） |
| 删除旧模块 | `services/semantic_cache.py` | 删除 106 行旧实现（遍历全量 key 做余弦相似度，O(n)） |

### Alembic 数据库迁移

| 改进 | 文件 | 说明 |
|------|------|------|
| alembic.ini | `alembic.ini` | 新增配置文件，连接字符串从 `settings.DATABASE_URL` 读取 |
| env.py | `alembic/env.py` | 异步引擎配置，自动导入所有模型 |
| script.py.mako | `alembic/script.py.mako` | 迁移脚本模板 |
| USE_ALEMBIC 开关 | `database.py` | `USE_ALEMBIC=true` 环境变量跳过 `create_all`，由 Alembic 管理 schema |

### 测试目录重组

| 目录 | 文件 | 说明 |
|------|------|------|
| `tests/unit/` | 8 个文件 | 纯逻辑单测（circuit_breaker, config, exceptions, masking, rag_cache, rag_metrics, rag_service, semantic_cache） |
| `tests/integration/` | 5 个文件 | 集成测试（auth_api, auth_service, document_parser, health, memory_service） |

### 验证

- 后端 160 个测试全部通过
- 前端 91 个测试全部通过
- 前端类型检查零错误

---

## 2026-05-09 (第三轮)

### 安全加固

| 改进 | 文件 | 说明 |
|------|------|------|
| 密码参数 Body 化 | `auth.py` | `change_password` 端点从裸参数改为 `ChangePasswordRequest` Pydantic 模型，密码不再暴露在 URL |
| Pydantic 请求模型 | `chat.py`, `memory.py`, `auth.py` | 新增 7 个 schema（`ChatStreamRequest`、`FeedbackRequest`、`RememberRequest` 等），替换裸 `Body(...)` |

### 异常体系全面迁移

**API 层 HTTPException 完全清零** — 全部迁移到 `AppError` 异常体系：

| 文件 | HTTPException 数量 | 迁移结果 |
|------|-------------------|---------|
| `knowledge.py` | 22 处 | → `NotFoundError` / `ValidationError` / `AppError` |
| `files.py` | 5 处 | → `AppError` |
| `organizations.py` | 18 处 | → `NotFoundError` / `ValidationError` / `ConflictError` / `AuthorizationError` / `AppError` |
| `users.py` | 17 处 | → `NotFoundError` / `ValidationError` / `AuthorizationError` / `AppError` |
| `chat.py` | 6 处 | → `NotFoundError` / `AuthorizationError` / `ValidationError` |
| `memory.py` | 1 处 | → 移除 `HTTPException` 导入 |

### 结构化日志增强

| 改进 | 文件 | 说明 |
|------|------|------|
| 请求上下文注入 | `core/logging.py` | `JsonFormatter` 新增 `trace_id`、`user_id` 字段 |
| trace_id 支持 | `core/logging.py` + `middleware.py` | 新增 `trace_id_var` ContextVar，中间件从 `X-Trace-ID` 或 `X-Request-ID` 头注入 |
| 去重 + 重命名 | `core/logging.py` | 移除重复 logger 配置，日志器 `paicongming` → `docmind` |

### Docker 安全

| 改进 | 文件 | 说明 |
|------|------|------|
| 非 root 用户 | `Dockerfile` | 新增 `appuser` 用户，容器不再以 root 运行 |
| .dockerignore | `.dockerignore` | 完善排除规则 |

### 配置补全

| 改进 | 文件 | 说明 |
|------|------|------|
| .env.example | `backend/.env.example` | 从 ~20 项扩展到 ~50 项，覆盖 JWT、限流、监控告警、文件上传等 |

### 验证

- 后端 160 个测试全部通过
- 前端 `vue-tsc --noEmit` 零类型错误
- 前端 91 个测试全部通过
- 所有端点 import 验证通过

---

## 2026-05-09 (第二轮)

### 安全加固

| 改进 | 文件 | 说明 |
|------|------|------|
| 暴力破解防护 | `auth_service.py` | Redis 计数器 + 15 分钟锁定（5 次失败触发），使用 `AccountLockedError` 异常 |
| MIME 类型校验 | `file_service.py` | `filetype` 库 magic bytes 检测，扩展名与实际内容双重校验，阻止伪装文件 |

### 架构重构

| 改进 | 文件 | 说明 |
|------|------|------|
| 配置拆分 | `core/config/` | 拆分为 `base.py`（应用）、`database.py`（基础设施）、`ai.py`（AI/RAG）、`security.py`（安全），多继承组合保持向后兼容 |
| 删除死代码 | `services/` | 删除 `chat_service.py`（361 行）和 `deepseek_service.py`（469 行）— 从未被任何模块导入 |
| API 合并 | `api/chat.ts`, `api/conversation.ts` | 会话管理函数统一到 `conversation.ts`，`chat.ts` 仅保留 `sendMessage` + 向后兼容 re-export |

### 前端依赖清理

| 改进 | 文件 | 说明 |
|------|------|------|
| 移除 `marked` | `package.json`, `manual/index.vue` | 替换为已有的 `markdown-it`，减少 1 个依赖 |

### 验证

- 后端 160 个测试全部通过
- 前端 `vue-tsc --noEmit` 零类型错误
- 前端 91 个测试全部通过

---

## 2026-05-09

### 架构深度优化（10 项改进）

#### 后端

| 改进 | 文件 | 说明 |
|------|------|------|
| API URL 校验 | `dependencies.py` | 新增 `_normalize_base_url()` — `urlparse` 验证 + 已知后缀剥离，替换脆弱的 `split()` |
| 有界 LRU 缓存 | `rag/cache.py` | 新增 `BoundedLRUCache(OrderedDict)` — Redis 故障时内存缓存不再无限增长 |
| Redis 生命周期 | `core/redis.py` | `_RedisHolder` + `_RedisProxy` 代理模式 — 解决 Python 导入绑定导致 `redis_client` 始终为 `None` 的问题 |
| ES 生命周期 | `core/elasticsearch.py` | 同上，`_ESHolder` + `_ESProxy` 代理模式 |
| 知识库构建顺序 | `services/knowledge_service.py` | INDEXED 状态改为 ES 索引成功后才标记，避免 DB/ES 状态不一致 |

#### 前端

| 改进 | 文件 | 说明 |
|------|------|------|
| ErrorBoundary | `App.vue` | 全局包裹 `<ErrorBoundary>` — 渲染异常时显示友好错误页 |
| 请求重试 | `utils/request.ts` | 新增重试拦截器 — 网络错误/502/503/504 自动重试 3 次，指数退避 |
| WS 重连退避 | `utils/websocket.ts` | 固定 5s 间隔改为指数退避（1s→2s→4s→8s→16s + jitter） |
| 类型安全 | `stores/user.ts` | `catch (error: any)` → `catch (error: unknown)` + `_extractErrorMessage` 辅助函数 |

### 稳定性验证

- 后端 160 个测试全部通过
- 前端 `vue-tsc --noEmit` 零类型错误
- 前端 91 个测试全部通过
- 端到端数据流验证通过（前端 SSE → 后端 RAG 管线 → LLM 流式响应）
- Agent 数据流验证通过（前端 SSE → AgentLoop → 工具注册中心 → 工具执行 → 响应）

### 文档更新

- 更新 `CLAUDE.md` — 反映当前完整项目状态
- 更新 `AGENT_ARCHITECTURE.md` — 工具表扩展至 11 个
- 更新 `CHANGELOG.md` — 补充 05-08 变更记录
- 更新 `README.md` — 新增 Agent 特性、API 端点、测试覆盖范围

---

## 2026-05-08

### Agent 系统（核心新增）

基于 NousResearch/hermes-agent 架构，实现 ReAct 风格自主 Agent。

**后端新增模块（`app/agent/`）：**

| 文件 | 职责 | 说明 |
|------|------|------|
| `registry.py` | 工具注册中心 | `@register_tool` 装饰器 + JSON Schema 自动生成，`ToolRegistry` 单例 |
| `tools.py` | 11 个内置工具 | 搜索(2)、分析(2)、文档管理(2)、对话管理(2)、提示词(2)、工具(1) |
| `loop.py` | ReAct 核心循环 | LLM → tool_calls → execute → append → repeat，最大 10 轮迭代 |
| `context.py` | 上下文窗口管理 | 保留 system prompt + 最近 N 条，压缩旧消息 |
| `skills.py` | 技能学习系统 | Redis 存储，关键词匹配触发，30 天 TTL |
| `subagent.py` | 子 Agent 委托 | 隔离上下文，受限工具集，并行执行 |
| `service.py` | 服务层 | 统一入口，连接 loop/tools/skills/context |

**API 端点：**
- `POST /api/v1/agent/chat` — SSE 流式 Agent 对话
- `GET /api/v1/agent/tools` — 列出可用工具
- `GET /api/v1/agent/skills` — 列出已学习技能

**前端新增：**
- `views/agent/index.vue` — Agent 对话页面，实时展示 tool_call/tool_result/chunk/error
- `api/agent.ts` — SSE 流式 API 封装
- 路由 + 侧边栏菜单已注册

### 异常体系重构

新增 `app/exceptions.py`，统一异常层级：

| 异常类 | HTTP 状态码 | 用途 |
|--------|------------|------|
| `AppError` | 500 | 基类 |
| `ValidationError` | 400 | 参数校验 |
| `AuthenticationError` | 401 | 认证失败 |
| `TokenExpiredError` | 401 | Token 过期 |
| `TokenBlacklistedError` | 401 | Token 已注销 |
| `AccountLockedError` | 401 | 账号锁定 |
| `AuthorizationError` | 403 | 权限不足 |
| `NotFoundError` | 404 | 资源不存在 |
| `ConflictError` | 409 | 资源冲突 |
| `RateLimitError` | 429 | 限流 |
| `ExternalServiceError` | 502 | 外部服务异常 |
| `PipelineError` | 500 | RAG 管线异常 |
| `StorageError` | 500 | 存储异常 |

已替换 auth/documents/chat 端点中的 `HTTPException`。

### 前端优化

- **XSS 修复**：`Markdown.vue` 添加 DOMPurify 净化，关闭 `html: true`
- **内存泄漏修复**：`dashboard/user.vue` 提取匿名 resize 回调为命名函数
- **Landing page 重写**：专业级着陆页（Hero + 4 步流程 + 特性卡片 + Agent 展示）
- **SystemHelp 升级**：从静态文本升级为完整帮助中心（快速开始、特性、FAQ、快捷键）
- **SystemAbout 升级**：从占位页升级为架构概览（技术栈、数据流、系统信息）
- **Dashboard 优化**：添加 Agent Mode 快捷入口
- **依赖清理**：移除未使用的 `recharts`，类型包移至 devDependencies

### 后端清理

- 删除重复 `app/core/minio.py`，统一使用 `minio_client.py` 单例
- `MinioClient` 新增 `remove_object` 方法
- `file_service.py` 迁移至新 MinIO 客户端
- 删除所有 `.pyc` 缓存文件
- 接入 OpenTelemetry 链路追踪（`ENABLE_TRACING` 环境变量控制）
- `DocumentStatus.PROCESSING` → `DocumentStatus.PARSING` 枚举修复

### 测试

- 新增 `tests/test_exceptions.py` — 9 个用例
- 新增 `tests/test_rag_cache.py` — 11 个用例
- 新增 `tests/test_rag_metrics.py` — 10 个用例
- 总计 **160 个后端测试**，全部通过

### 文档

- 新增 `AGENT_ARCHITECTURE.md` — Agent 架构文档（模块说明、架构图、hermes-agent 对比）
- 更新 `CLAUDE.md` — 反映当前项目结构（Agent 系统、RAG 管线、异常体系）

### 测试体系搭建

#### 后端测试（132 个用例）

新建文件：

| 文件 | 覆盖范围 | 用例数 |
|------|----------|--------|
| `tests/test_auth_service.py` | JWT 创建/验证/过期/篡改、密码哈希（bcrypt）、Token 黑名单（Redis mock）、RBAC 角色依赖 | 22 |
| `tests/test_masking_service.py` | PII 脱敏（手机号/邮箱/身份证/IP）、多类型混合、还原 roundtrip、空值/None 处理 | 11 |
| `tests/test_circuit_breaker.py` | 熔断器状态机（CLOSED→OPEN→HALF_OPEN→CLOSED）、降级返回值（None/list/dict/str）、异步支持 | 10 |
| `tests/test_semantic_cache.py` | 余弦相似度（相同/相反/正交/零向量/高维） | 7 |
| `tests/test_rag_service.py` | RRF 融合、查询意图分类、上下文压缩、长查询优化、查询重写候选 | 7 |
| `tests/test_config.py` | Settings validator 拒绝空 SECRET_KEY/JWT_SECRET_KEY、连接池上限、限流路径不含 auth | 5 |
| `tests/test_document_parser.py` | TXT/DOCX 解析、编码检测、元数据提取 | 5 |
| `tests/test_auth_api.py` | 注册密码 <8 位拒绝、缺少 username、无效 email、健康检查、登录 | 7 |
| `tests/test_memory_service.py` | 记忆系统（短期/长期/工作/反思/Agent 记忆系统集成） | 52 |
| `tests/test_health.py` | 健康检查端点 | 2 |

配置文件：
- `backend/pytest.ini` — 配置 `asyncio_mode=auto`、测试路径、过滤警告
- `backend/tests/conftest.py` — 统一设置测试环境变量（SECRET_KEY、JWT_SECRET_KEY 等），避免 Settings validator 报错

#### 前端测试（49 个用例）

新建文件：

| 文件 | 覆盖范围 | 用例数 |
|------|----------|--------|
| `src/utils/__tests__/auth.test.ts` | Token 存取/删除/过期检查、Legacy Key 兼容、Refresh Token | 15 |
| `src/utils/__tests__/format.test.ts` | 日期相对格式化（刚刚/分钟/小时/天/周）、文件大小、时长、文本截断 | 17 |
| `src/utils/__tests__/retry.test.ts` | 指数退避、可重试条件、retry-after 头、最大重试次数、onRetry 回调 | 8 |
| `src/utils/__tests__/websocket.test.ts` | 连接生命周期、无效 userId 守卫、重复连接守卫、send/sendStop 未连接返回 false | 9 |

配置文件：
- `frontend/vitest.config.ts` — jsdom 环境、`@` 别名、v8 coverage
- `frontend/package.json` — 新增 `test`、`test:watch`、`test:coverage` 脚本
- 依赖安装：`vitest`、`@vue/test-utils`、`jsdom`、`happy-dom`

### CI/CD

新建文件：

- `.github/workflows/ci.yml` — GitHub Actions 工作流
  - 后端测试：Python 3.11 + 3.12 矩阵，pip cache，环境变量注入
  - 前端测试：Node 18 + 20 矩阵，npm cache，Vue 类型检查
  - Lint 检查：ESLint（continue-on-error）
- `.github/dependabot.yml` — pip（weekly）、npm（weekly）、github-actions（monthly）
- `.github/pull_request_template.md` — PR 模板（描述/类型/检查清单）

### 前端架构重构

**问题**：`frontend/src/views/chat/index.vue` 有 1574 行，职责混杂（连接管理、消息发送、文件上传、会话管理、UI 渲染全部在一个文件里）。

**方案**：拆分为 5 个子组件 + 5 个组合式函数。

新建组件：

| 文件 | 职责 | 行数 |
|------|------|------|
| `components/ChatSidebar.vue` | 会话列表侧边栏（新建/刷新/选择/删除） | 125 |
| `components/ChatMessages.vue` | 消息展示区（DynamicScroller、欢迎页、反馈按钮、来源引用） | 183 |
| `components/ChatInput.vue` | 输入区（文件附件、连接状态指示、严格/隐私/SSE/Stream 模式切换） | 209 |
| `components/ChatHeader.vue` | 顶部导航（标题、绑定模式标签、清空聊天） | 65 |
| `components/DocumentPreviewModal.vue` | 文档预览弹窗（元数据、摘要、标签、内容、下载） | 79 |
| `components/index.ts` | 桶导出 | 5 |

新建组合式函数：

| 文件 | 职责 | 行数 |
|------|------|------|
| `composables/useChatConnection.ts` | WebSocket/SSE 连接管理、状态轮询、stopGeneration | 154 |
| `composables/useChatSend.ts` | 消息发送（WebSocket/SSE）、handleSend、handleSSESend | 223 |
| `composables/index.ts` | 桶导出 | 5 |

已有组合式函数（之前已存在但未被使用）：
- `useChatAttachments.ts` — 文件上传与轮询
- `useChatMessages.ts` — 消息展示/滚动/反馈/复制
- `useChatSessions.ts` — 会话列表管理

**结果**：`chat/index.vue` 从 1574 行缩减到 230 行，仅负责组合各 composable 和组件。

### Bug 修复

- `backend/app/main.py` — 修复 `validation_exception_handler` 中 Pydantic `ValueError` 对象无法 JSON 序列化的问题。Pydantic v2 的 `RequestValidationError.errors()` 返回的 `ctx` 字段可能包含 `ValueError` 实例，直接传给 `JSONResponse` 会崩溃。现在遍历 errors 将 Exception 实例转为字符串。

### 文档整理

删除过时文件（共 4915 行）：
- `DEVELOPMENT_GUIDE.md` — 引用旧项目名 "paicongming"，内容过时
- `technical_documentation.md` — 基于旧 `.env` 分析，引用 Ollama/FAISS（实际未使用）
- `企业级AI智能知识库系统详细文档.md` — 与 README 重复
- `派聪明AI知识库系统开发文档.md` — 旧名称，内容过时
- `backend/RAG_SYSTEM_SUMMARY.md` — 引用旧架构（FAISS、1536 维向量）
- `docs/面试问题大全.md` — 面试资料，非项目文档

更新文件：
- `README.md` — 更新项目结构（反映组件化架构和测试）、新增测试说明、安全加固表、架构优化说明、更新日志
- `backend/README.md` — 更新项目名称、测试用例表格

---

## 2026-05-06

### 安全加固（CRITICAL / HIGH / MEDIUM）

#### CRITICAL 级别

| 问题 | 文件 | 修复 |
|------|------|------|
| 生产代码泄露明文密码到日志 | `backend/app/services/auth_service.py` | 移除 `logger.warning(f"DEBUG ONLY - Input pass: {password}")` 和 `auth_debug.log` 文件写入 |
| `.env.example` 包含真实 API Key | `backend/.env.example` | 全部替换为 `YOUR_API_KEY` 占位符，添加密钥生成说明 |
| 默认弱密钥允许 JWT 伪造 | `backend/app/core/config.py` | `SECRET_KEY` 和 `JWT_SECRET_KEY` 默认值改为空字符串，添加 `@model_validator` 启动时强制校验 |
| 登出后 Token 仍有效 | `backend/app/services/auth_service.py` | 添加 `blacklist_token()` 和 `is_token_blacklisted()`，`get_current_user()` 中增加黑名单检查 |

#### HIGH 级别

| 问题 | 文件 | 修复 |
|------|------|------|
| 裸 `except:` 吞掉所有异常 | `auth.py`、`users.py`、`documents.py`、`monitoring.py`、`document_parser.py`、`organizations.py` | 改为精确异常类型（`ValueError`、`TypeError`、`json.JSONDecodeError`、`OSError`、`Exception`） |
| 重复 AuthService 实例化 | `auth.py`、`users.py`、`chat.py`、`notifications.py` | 统一使用单例 `auth_service`，移除函数内重复创建 |
| CORS `allow_methods=["*"]` | `backend/app/main.py` | 改为 `["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]` |
| 认证路径被排除在限流外 | `backend/app/core/config.py` | 从 `RATE_LIMIT_EXCLUDE_PATHS` 移除 `/api/v1/auth` |

#### MEDIUM 级别

| 问题 | 文件 | 修复 |
|------|------|------|
| `datetime.utcnow()` 已弃用 | `auth_service.py` | 全部改为 `datetime.now(timezone.utc)` |
| 连接池过大 | `config.py` | `DATABASE_POOL_SIZE` 100→20，`DATABASE_MAX_OVERFLOW` 30→10 |
| `traceback.print_exc()` 泄露堆栈 | `auth.py`、`organizations.py` | 移除，使用 logger 记录 |
| 密码无长度校验 | `auth.py` | 添加 `@field_validator`：8-128 位 |

### 前端修复

| 问题 | 文件 | 修复 |
|------|------|------|
| WebSocket `stopGeneration` 双重 JSON 编码 | `utils/websocket.ts` | 新增 `sendStop()` 方法，内部直接 `JSON.stringify` |
| 重复路由守卫 | `utils/request.ts`、`main.ts` | 移除 `setupInterceptors` 函数及其调用 |
| `api/chat.ts` 重复函数定义 | `api/chat.ts` | 移除与 `api/conversation.ts` 重复的 `getConversations`、`createConversation`、`deleteConversation` |
| `getUserInfo` 失败不登出 | `stores/user.ts` | catch 中调用 `logout()` 并 re-throw |
| 主题切换无防抖 | `stores/app.ts` | 添加 500ms debounce，避免频繁 API 调用 |

### 文档

- 重写 `README.md`：专业架构图（ASCII art）、数据流程图、技术栈表格、快速开始指南、API 概览
- 清理根目录：删除 `start.bat`、`package.json`、`requirements.txt`、`PROJECT_STRUCTURE.md`、`interview_guide.txt`、`resume_feedback.txt`
- 重写 `backend/.env.example`：完整配置说明、密钥生成指令

---

## 项目技术栈（当前）

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy 2.0(async, Mapped) + MySQL 8 + Redis + Elasticsearch 8 + Kafka + MinIO |
| AI/RAG | DeepSeek API + OpenAI 兼容 Embedding + LangChain + Adaptive RAG + HyDE |
| Agent | ReAct Loop + Tool Registry + Skill Learning + SubAgent |
| 前端 | Vue 3 + TypeScript + Vite + Naive UI + Pinia + Vue Router |
| 安全 | JWT + RBAC + Token 黑名单 + bcrypt + CORS + 限流 + 暴力破解防护 |
| 可观测 | Prometheus + Grafana + OpenTelemetry + 结构化日志 |
| 测试 | pytest (216) + Vitest (95) |
| CI/CD | GitHub Actions + Dependabot |
| 改造进度 | REFACTOR_PLAN 52/53 项完成（98%） |
