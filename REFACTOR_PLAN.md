# DocMind 生产级改造路线图

> 目标：将 DocMind 从"能跑"提升到"作品集级"的全栈 RAG 系统

---

## Phase 0: 安全与基建（Day 1-2）
> 上线前的硬性前提，不修这些其他都白搭

### 0.1 密钥与凭据安全
- [ ] docker-compose.yml 移除所有硬编码 API Key，改用 `.env` 文件挂载
- [ ] `.env.example` 保留占位符，`.env` 加入 `.gitignore`
- [ ] `config.py` 的 `SECRET_KEY` / `JWT_SECRET_KEY` 空值校验已存在，确认生效
- [ ] MinIO、MySQL 默认密码改为通过环境变量注入
- [ ] `EXPOSE_EXCEPTION_DETAIL` 默认 `false`，docker-compose 中也改为 `false`

### 0.2 认证安全加固
- [ ] WebSocket 认证改为通过 `Sec-WebSocket-Protocol` header 传 token，而非 query param
- [ ] `auth_service.py` 中 `verify_password` 添加 timing-safe 比较
- [ ] 登录接口添加暴力破解防护（基于 Redis 的失败计数）
- [ ] JWT token 增加 `jti` (JWT ID) 用于精确吊销

### 0.3 输入验证与 SQL 安全
- [ ] `chat.py:476` 的 `text()` SQL 改为 SQLAlchemy ORM 操作
- [ ] 所有用户输入端点添加 Pydantic schema 严格校验
- [ ] 文件上传增加 MIME type 校验（不依赖扩展名）

---

## Phase 1: 架构重构（Day 3-7）
> 核心架构改造，这是作品集最能体现设计能力的部分

### 1.1 RAG 服务拆分（最高优先级）
当前 `rag_service.py` 1500+ 行，承担了 6 种职责。拆分为：

```
backend/app/rag/
├── __init__.py
├── query_processor.py      # 查询意图分类 + 查询改写 + HyDE
├── retriever.py             # 混合检索（关键词 + 向量 + RRF 融合）
├── reranker.py              # Cross-Encoder / LLM 重排
├── context_compressor.py    # 上下文压缩
├── cache.py                 # 精确缓存 + 语义缓存（统一接口）
├── metrics.py               # RAG 指标收集（独立于业务逻辑）
└── pipeline.py              # RAG 管线编排器（组合以上组件）
```

关键设计原则：
- 每个组件通过构造函数注入依赖，不引用全局单例
- `pipeline.py` 是唯一知道完整流程的文件，其他组件只关心自己的职责
- 所有组件实现 Protocol/ABC，方便测试时 mock

### 1.2 服务层依赖注入
当前问题：`from app.services.xxx import xxx_service` 在模块顶层，测试无法替换。

改造方案：
```python
# 不再使用模块级单例
# 改为 FastAPI Depends 注入

# backend/app/dependencies.py
from functools import lru_cache
from app.rag.pipeline import RAGPipeline
from app.rag.retriever import HybridRetriever
# ...

@lru_cache
def get_rag_pipeline() -> RAGPipeline:
    return RAGPipeline(
        retriever=get_hybrid_retriever(),
        reranker=get_reranker(),
        cache=get_cache(),
        # ...
    )

# 在 endpoint 中使用
@router.post("/stream")
async def chat_stream(
    body: ChatRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
    current_user: User = Depends(get_current_user),
):
    ...
```

### 1.3 统一错误处理
当前：有些返回 `{"success": False}`，有些抛 `HTTPException`，有些返回空列表。

改造为分层异常体系：
```python
# backend/app/exceptions.py
class DocMindException(Exception):
    """基础业务异常"""
    code: str = "INTERNAL_ERROR"
    status_code: int = 500

class AuthenticationError(DocMindException):
    code = "AUTH_FAILED"
    status_code = 401

class KnowledgeBaseError(DocMindException):
    code = "KNOWLEDGE_ERROR"
    status_code = 500

class RetrievalError(DocMindException):
    code = "RETRIEVAL_FAILED"
    status_code = 503

# main.py 中统一捕获
@app.exception_handler(DocMindException)
async def business_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "code": exc.code, "message": exc.message}
    )
```

### 1.4 消除全局可变状态
- [ ] `rag_service.py` 的 `_retrieval_cache` / `_semantic_cache` 迁移到 Redis
- [ ] `elasticsearch.py` 不再运行时修改 `settings.ES_ANALYZER`，改为初始化时返回配置
- [ ] `middleware.py` 的 `MetricsCollector` 改为 Redis-backed 或 Prometheus client
- [ ] 所有 `xxx_service = XxxService()` 单例改为由 DI 容器管理

### 1.5 语义缓存重写
当前实现遍历 Redis 全量 key 做余弦相似度 — O(n) 不可扩展。

改为：
- 使用 Redis Sorted Set + 向量哈希分桶
- 或引入 Redis Vector Similarity Search (RedisSearch)
- 或使用 Annoy/FAISS 本地索引（适合中小规模）

### 1.6 数据库事务管理
- [ ] 引入 Unit of Work 模式或 SQLAlchemy 的 `begin()` / `commit()` 统一管理
- [ ] 移除散布在业务逻辑中的 `session.commit()`
- [ ] 使用 Alembic 进行正式的数据库迁移，替代 `create_all`

---

## Phase 2: 代码质量提升（Day 8-12）
> 让代码看起来像出自资深工程师之手

### 2.1 消除重复代码
- [ ] 删除 `backend/app/services/doc_parser.py`（旧版），保留 `document_parser.py`
- [ ] 删除 `backend/rag_system.py`（空文件）
- [ ] 删除 `backend/lib/` 下的旧版 RAG 代码（已被 `app/services/` 替代）
- [ ] 合并 `minio.py` 和 `minio_client.py`

### 2.2 Chat 服务整合
当前 `ChatService` 和 `DeepSeekService` 职责重叠。

改造为：
```
chat/
├── __init__.py
├── session_manager.py    # 会话 CRUD（从 ChatService 提取）
├── message_handler.py    # 消息处理与持久化
└── stream_handler.py     # WebSocket / SSE 流式处理
```

### 2.3 类型安全
- [ ] 消除所有 `pyright: ignore` 注释（约 30+ 处），修复底层类型问题
- [ ] 为所有 service 方法添加完整的类型注解
- [ ] `User` 模型的 `to_dict()` 改为 Pydantic schema 序列化

### 2.4 前端清理
- [ ] 移除 `recharts`（保留 `echarts`），移除 `marked`（保留 `markdown-it`）
- [ ] 添加路由级别的代码分割（`() => import(...)` 已存在，确认全部使用）
- [ ] 统一 API 响应类型定义（`frontend/src/types/api.ts`）
- [ ] 为关键 composables 添加单元测试

### 2.5 配置管理
- [ ] `config.py` 拆分为：`base.py`、`database.py`、`ai.py`、`security.py`
- [ ] 添加配置验证测试（确保必填项不为空、数值在合理范围）
- [ ] 敏感配置（API Key）运行时从环境变量读取，不写入日志

---

## Phase 3: 工程化（Day 13-16）
> 体现专业工程素养

### 3.1 测试体系
```
backend/tests/
├── unit/                    # 纯逻辑单元测试
│   ├── test_query_processor.py
│   ├── test_reranker.py
│   ├── test_context_compressor.py
│   └── test_cache.py
├── integration/             # 需要真实服务的测试
│   ├── test_rag_pipeline.py
│   ├── test_document_flow.py
│   └── test_auth_flow.py
├── conftest.py              # 共享 fixtures
└── factories.py             # 测试数据工厂
```

目标覆盖率：
- RAG 核心逻辑：80%+
- 认证/授权：90%+
- API 端点：70%+

### 3.2 CI/CD
```yaml
# .github/workflows/ci.yml
- Lint (ruff / eslint)
- Type check (pyright / vue-tsc)
- Unit tests
- Integration tests (with docker-compose services)
- Build frontend
- Docker image build
```

### 3.3 Docker 优化
- [ ] 多阶段构建（builder → runtime）
- [ ] 非 root 用户运行
- [ ] Health check 端点完善（检查 DB/Redis/ES 连接状态）
- [ ] docker-compose 使用 `.env` 文件 + `env_file` 指令

### 3.4 API 文档
- [ ] 所有端点添加 OpenAPI 示例（`response_model_example`）
- [ ] 添加 `tags` 描述和 API 版本信息
- [ ] 生成前端 API 类型（openapi-typescript-codegen）

---

## Phase 4: 高级特性（Day 17-20）
> 体现技术深度，让作品集脱颖而出

### 4.1 RAG 质量提升
- [ ] 添加 RAG 评估管线（自动计算 Faithfulness / Relevancy / Context Precision）
- [ ] 支持多轮对话的上下文窗口管理
- [ ] 实现 Adaptive RAG（根据查询复杂度动态调整检索策略）

### 4.2 可观测性
- [ ] 结构化日志（JSON 格式，包含 trace_id / span_id）
- [ ] Prometheus 指标完善（RAG 延迟分布、缓存命中率、LLM token 消耗）
- [ ] Grafana Dashboard 模板

### 4.3 前端体验
- [ ] 流式打字机效果优化
- [ ] 消息引用来源的交互式展示
- [ ] 暗色模式完善
- [ ] 移动端响应式适配

---

## 执行顺序建议

```
Phase 0 (安全) → Phase 1.1 (RAG拆分) → Phase 1.3 (错误处理) → Phase 1.4 (消除全局状态)
→ Phase 2.1 (去重) → Phase 2.2 (Chat整合) → Phase 1.2 (DI) → Phase 2.3 (类型安全)
→ Phase 3.1 (测试) → Phase 3.2 (CI/CD) → Phase 4 (高级特性)
```

**核心原则**：先让安全过关，再重构核心（RAG），然后扩展到全栈，最后打磨细节。

---

## 文件变更影响评估

| Phase | 新增文件 | 修改文件 | 删除文件 | 预计改动行数 |
|-------|---------|---------|---------|------------|
| 0     | 0       | 8       | 0       | ~200       |
| 1     | 12      | 15      | 3       | ~3000      |
| 2     | 3       | 20      | 5       | ~1500      |
| 3     | 8       | 5       | 0       | ~1000      |
| 4     | 5       | 10      | 0       | ~1500      |
