<p align="center">
  <h1 align="center">DocMind</h1>
  <p align="center"><strong>企业级 RAG 智能知识库系统</strong></p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/Vue-3.4-4FC08D?logo=vuedotjs" alt="Vue 3">
    <img src="https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript" alt="TS">
    <img src="https://img.shields.io/badge/Elasticsearch-8.11-005571?logo=elasticsearch" alt="ES">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  </p>
</p>

---

## 简介

DocMind 是一个基于 **RAG（Retrieval-Augmented Generation）** 架构的全栈 AI 知识库系统。上传你的文档后，系统自动完成解析、分块、向量化与索引，用户可通过自然语言对话，获得基于文档内容的精准、可溯源的 AI 回答。

适用于企业知识管理、技术文档问答、客户支持知识库等场景，也可作为大模型落地的全栈参考实现。

---

## 系统架构

```
┌──────────────┐     ┌──────────────────────────────────────────────────┐
│   Browser    │     │                 Backend (FastAPI)                 │
│              │     │                                                  │
│  Vue 3 SPA  ◄┼─────┼►  REST API / WebSocket / SSE                    │
│  (Naive UI) │     │                                                  │
│              │     │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
└──────────────┘     │  │  Auth    │  │  Chat    │  │  Knowledge   │  │
                     │  │  Service │  │  Service │  │  Service     │  │
                     │  └──────────┘  └────┬─────┘  └──────┬───────┘  │
                     │                    │                 │           │
                     │           ┌────────▼─────────┐       │           │
                     │           │   RAG Pipeline    │       │           │
                     │           │ ┌───────────────┐ │       │           │
                     │           │ │ Hybrid Search  │ │       │           │
                     │           │ │ BM25 + Vector  │ │       │           │
                     │           │ └───────────────┘ │       │           │
                     │           └────────┬──────────┘       │           │
                     │                    │                   │           │
                     └────────────────────┼───────────────────┘           │
                                          │                               │
            ┌─────────────────────────────┼───────────────────────────┐   │
            │           Infrastructure    │                           │   │
            │                             │                           │   │
            │  ┌──────────┐  ┌──────────┐ │ ┌──────────┐ ┌────────┐  │   │
            │  │  MySQL   │  │  Redis   │   │   MinIO  │ │ Kafka  │  │   │
            │  │  元数据  │  │  缓存    │   │  文件存储│ │ 消息队列│  │   │
            │  └──────────┘  └──────────┘ │ └──────────┘ └───┬────┘  │   │
            │                             │                   │       │   │
            │  ┌──────────────────────────┴──┐        ┌──────▼────┐  │   │
            │  │  Elasticsearch              │        │  Worker    │  │   │
            │  │  向量 + 全文索引            │◄───────│  文档处理  │  │   │
            │  └─────────────────────────────┘        └───────────┘  │   │
            │                                                       │   │
            └───────────────────────────────────────────────────────┘   │
                                                                        │
                     ┌──────────────────────────────┐                   │
                     │        AI Services           │                   │
                     │ ┌────────────┐ ┌───────────┐ │                   │
                     │ │  DeepSeek  │ │ Embedding │ │                   │
                     │ │  LLM 生成  │ │  向量化   │ │                   │
                     │ └────────────┘ └───────────┘ │                   │
                     └──────────────────────────────┘                   │
```

---

## 核心特性

### 文档智能处理
- 支持 **PDF / Word / Excel / TXT / Markdown** 等多种格式
- 基于 **LangChain** 的智能分块策略（滑动窗口 + 语义分块）
- **Kafka 异步消息队列**解耦上传与处理，支持高并发

### 混合检索
- **BM25 关键词匹配** + **向量语义检索**双路召回
- **Reranker 重排序**提升检索精度
- **组织级多租户隔离**，确保数据安全

### 流式智能问答
- **WebSocket 实时通信**，逐字流式输出
- 支持 **多轮对话**上下文记忆
- 答案附带 **来源引用**，可追溯原始文档

### Agent 自主推理（ReAct）
- **11 个内置工具**：知识库搜索、向量检索、文档摘要、关键词提取、对话管理、提示词模板
- **ReAct 循环**：LLM 自主规划 → 调用工具 → 观察结果 → 继续推理，最多 10 轮迭代
- **上下文管理**：自动压缩历史消息，保持 token 预算内
- **技能学习**：成功的工具使用模式自动保存为可复用技能
- **SSE 流式输出**：实时展示工具调用过程和推理步骤

### 企业级基础设施
- **RBAC 权限体系**：用户 → 角色 → 组织三级管控
- **JWT 认证** + Token 黑名单（Redis）
- **Prometheus + Grafana** 全链路监控告警
- **审计日志**全量记录操作轨迹

### 可视化工作流编排
- 拖拽式 **DAG 工作流编辑器**
- 内置 LLM / API / Code / Condition / Memory 等节点
- 实时调试与执行追踪

---

## 技术栈

| 层级 | 技术选型 |
|------|----------|
| **后端框架** | FastAPI + Uvicorn（async） |
| **数据库** | MySQL 8 + SQLAlchemy 2.0（async）+ Alembic 迁移 |
| **缓存** | Redis 5 |
| **搜索引擎** | Elasticsearch 8（KNN 向量 + BM25 全文） |
| **消息队列** | Kafka（aiokafka） |
| **对象存储** | MinIO（S3 兼容） |
| **AI 模型** | DeepSeek / OpenAI 兼容 API（Chat + Embedding + Rerank） |
| **Agent** | ReAct 循环 + 工具注册中心 + 上下文管理 + 技能学习 |
| **文档解析** | LangChain + PyPDF + Unstructured + python-docx |
| **前端框架** | Vue 3 + TypeScript + Vite |
| **UI 组件** | Naive UI + ECharts + Vue Flow |
| **状态管理** | Pinia |
| **国际化** | Vue I18n（中 / 英 / 日 / 法） |
| **监控** | Prometheus + Grafana + AlertManager |
| **安全** | JWT + RBAC + 多租户 + 审计日志 |

---

## 快速开始

### 前置条件

- **Docker Desktop**（推荐，一键启动所有中间件）
- 或手动安装：Python 3.10+ / Node.js 18+ / MySQL 8 / Redis / Elasticsearch 8 / Kafka / MinIO

### 方式一：一键启动（Docker Compose）

```bash
# 1. 克隆仓库
git clone https://github.com/sijie-Z/DocMind-RAG.git
cd DocMind-RAG

# 2. 启动基础设施
cd backend
docker-compose up -d

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 AI API Key（DeepSeek / OpenAI 等）

# 4. 启动后端 + Worker
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
python -m worker.doc_consumer &

# 5. 启动前端
cd ../frontend
npm install
npm run dev
```

### 方式二：Windows 一键启动

```bash
# 双击运行
start_windows.bat
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost:5173 |
| API 文档（Swagger） | http://localhost:8000/docs |
| Grafana 监控 | http://localhost:3000 |

> **测试账号**：`guest` / `123456`

### 环境变量配置

关键配置项（完整列表见 `backend/.env.example`）：

```bash
# --- AI 模型 ---
DEEPSEEK_API_KEY=sk-xxx           # LLM API Key
DEEPSEEK_API_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

EMBEDDING_API_KEY=sk-xxx          # Embedding API Key
EMBEDDING_API_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small

# --- 基础设施 ---
DATABASE_URL=mysql+aiomysql://root:root@localhost:3306/paicongming_db
REDIS_HOST=localhost
ELASTICSEARCH_HOSTS=["http://localhost:9200"]
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
MINIO_ENDPOINT=localhost:9000

# --- 安全 ---
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
```

---

## 数据流程

### 文档入库

```
用户上传 ──► MinIO 存储 ──► MySQL 记录 ──► Kafka 消息 ──► Worker 消费
                                                              │
                                    文档解析（LangChain）◄────┘
                                           │
                                    智能分块（滑动窗口）
                                           │
                                    Embedding 向量化
                                           │
                                    写入 Elasticsearch ✅
```

### 智能问答

```
用户提问 ──► WebSocket ──► 问题向量化 ──► ES 混合检索（BM25 + KNN）
                                                 │
                                    带权限过滤的结果集
                                                 │
                              上下文 + 历史消息 ──► LLM 流式生成
                                                 │
                                    答案 + 引用来源 ──► 前端渲染
```

---

## 项目结构

```
DocMind/
├── .github/                         # CI/CD 配置
│   ├── workflows/ci.yml             # GitHub Actions（后端 + 前端 + Lint）
│   ├── dependabot.yml               # 自动依赖更新
│   └── pull_request_template.md     # PR 模板
├── backend/                         # FastAPI 后端
│   ├── app/
│   │   ├── agent/                   # Agent 系统（registry, tools, loop, context, skills, subagent）
│   │   ├── api/v1/endpoints/        # 14 个 API 模块（auth, chat, knowledge, agent, workflow...）
│   │   ├── core/                    # 基础设施层（DB, ES, Kafka, MinIO, Redis, 安全, 熔断器, 链路追踪）
│   │   ├── exceptions.py            # 统一异常层级（13 个异常类）
│   │   ├── models/                  # SQLAlchemy 数据模型（12 张表）
│   │   ├── rag/                     # RAG 管线（pipeline, retriever, reranker, cache, metrics）
│   │   ├── schemas/                 # Pydantic 请求/响应模型
│   │   └── services/                # 业务服务层（17 个服务模块）
│   ├── tests/                       # pytest 测试（160 个用例）
│   │   ├── test_auth_service.py     # JWT / 密码哈希 / Token 黑名单 / RBAC
│   │   ├── test_masking_service.py  # PII 脱敏（手机/邮箱/身份证/IP）
│   │   ├── test_circuit_breaker.py  # 熔断器状态机
│   │   ├── test_semantic_cache.py   # 语义缓存余弦相似度
│   │   ├── test_rag_service.py      # RRF 融合 / 查询意图 / 上下文压缩
│   │   ├── test_rag_cache.py        # 精确缓存 + 语义缓存序列化/量化
│   │   ├── test_rag_metrics.py      # 指标快照 / 百分位数 / 窗口过滤
│   │   ├── test_exceptions.py       # 异常层级 / 状态码映射 / 错误码
│   │   ├── test_config.py           # 配置校验（弱密钥拒绝）
│   │   ├── test_document_parser.py  # 文档解析
│   │   ├── test_auth_api.py         # API 端点集成测试
│   │   └── test_memory_service.py   # 记忆系统（52 个用例）
│   ├── lib/rag/                     # RAG 工具库（chunk, vectorizer, retriever, hybrid, BM25）
│   ├── worker/                      # 独立 Kafka 消费者（文档处理 Worker）
│   ├── config/                      # Prometheus + Grafana 监控配置
│   ├── pytest.ini                   # pytest 配置
│   ├── docker-compose.yml           # 基础设施容器编排
│   ├── requirements.txt
│   └── .env.example
├── frontend/                        # Vue 3 前端
│   ├── src/
│   │   ├── views/
│   │   │   └── chat/                # 聊天页面（已重构为组件化架构）
│   │   │       ├── index.vue        # 主入口（230 行，原 1574 行）
│   │   │       ├── components/      # 5 个子组件
│   │   │       │   ├── ChatSidebar.vue
│   │   │       │   ├── ChatMessages.vue
│   │   │       │   ├── ChatInput.vue
│   │   │       │   ├── ChatHeader.vue
│   │   │       │   └── DocumentPreviewModal.vue
│   │   │       └── composables/     # 5 个组合式函数
│   │   │           ├── useChatAttachments.ts
│   │   │           ├── useChatMessages.ts
│   │   │           ├── useChatSessions.ts
│   │   │           ├── useChatConnection.ts
│   │   │           └── useChatSend.ts
│   │   ├── api/                     # 15 个 API 模块封装
│   │   ├── stores/                  # Pinia 状态管理
│   │   ├── utils/
│   │   │   ├── __tests__/           # Vitest 测试（91 个用例）
│   │   │   │   ├── auth.test.ts
│   │   │   │   ├── format.test.ts
│   │   │   │   ├── retry.test.ts
│   │   │   │   └── websocket.test.ts
│   │   ├── stores/
│   │   │   └── __tests__/           # Store 测试
│   │   │       ├── chat.test.ts
│   │   │       └── workflow.test.ts
│   │   ├── composables/
│   │   │   └── __tests__/           # Composable 测试
│   │   │       └── useDebounce.test.ts
│   │   │   ├── websocket.ts         # WebSocket 单例服务
│   │   │   ├── auth.ts              # Token 管理（Cookie + localStorage）
│   │   │   ├── retry.ts             # 指数退避重试
│   │   │   └── format.ts            # 日期/文件大小格式化
│   │   └── locales/                 # 国际化（zh / en / ja / fr）
│   ├── vitest.config.ts             # Vitest 配置
│   └── package.json
├── deploy/monitoring/               # 生产监控部署（Prometheus + Grafana + AlertManager）
├── docs/                            # 项目文档
├── start.sh                         # Linux/Mac 一键启动
└── README.md
```

---

## API 概览

| 模块 | 路径 | 功能 |
|------|------|------|
| 认证 | `/api/v1/auth/*` | 登录、注册、Token 刷新 |
| 用户 | `/api/v1/users/*` | 用户 CRUD、角色分配 |
| 知识库 | `/api/v1/knowledge/*` | 文档上传、检索、索引管理 |
| 聊天 | `/api/v1/chat/*` | WebSocket/SSE 流式对话、会话管理 |
| Agent | `/api/v1/agent/*` | ReAct Agent 对话（SSE）、工具列表、技能列表 |
| 工作流 | `/api/v1/workflow/*` | DAG 可视化编排 |
| 组织 | `/api/v1/organizations/*` | 多租户管理 |
| 监控 | `/api/v1/monitoring/*` | 系统指标、健康检查 |
| 审计 | `/api/v1/audit/*` | 操作日志查询 |

完整 API 文档启动后端后访问：http://localhost:8000/docs

---

## 测试

### 后端测试（160 个用例）

```bash
cd backend
python -m pytest tests/ -v
```

覆盖范围：
- **AuthService**：JWT 创建/验证、密码哈希、Token 黑名单、RBAC 角色检查
- **MaskingService**：PII 脱敏（手机号/邮箱/身份证/IP/银行卡）、还原
- **CircuitBreaker**：熔断器状态机（CLOSED→OPEN→HALF_OPEN→CLOSED）、降级返回值
- **SemanticCache**：余弦相似度边界情况
- **RagService**：RRF 融合、查询意图分类、上下文压缩、查询重写
- **RAG Cache**：精确缓存 + 语义缓存序列化/量化
- **RAG Metrics**：指标快照、百分位数、窗口过滤
- **Exceptions**：异常层级、状态码映射、错误码生成
- **Config**：弱密钥拒绝、连接池上限、限流路径排除
- **DocumentParser**：TXT/DOCX 解析、元数据提取
- **Auth API**：注册密码校验、缺少字段、无效邮箱
- **MemoryService**：短期/长期/工作/反思记忆 + Agent 记忆系统集成（52 个用例）

### 前端测试（91 个用例）

```bash
cd frontend
npm test
```

覆盖范围：
- **auth.ts**：Token 存取/删除/过期检查、Legacy Key 兼容
- **format.ts**：日期相对格式化、文件大小格式化、时长格式化、文本截断
- **retry.ts**：指数退避、可重试条件判断、retry-after 头、最大重试次数
- **websocket.ts**：连接生命周期、发送守卫、状态管理
- **chat store**：会话管理、消息 CRUD、加载状态、文档解绑
- **workflow store**：节点/边 CRUD、选择、执行状态、流程数据序列化
- **useDebounce**：防抖/节流 Ref、防抖/节流函数

### CI/CD

Push 或 PR 到 `main` / `develop` 分支时，GitHub Actions 自动运行：
- 后端测试（Python 3.11 + 3.12）
- 前端测试（Node 18 + 20）
- TypeScript 类型检查（`vue-tsc --noEmit`，零错误要求）
- 生产构建（`npm run build`）
- ESLint 检查（零错误零警告）

---

## 安全加固

本项目经过全面安全审计，修复了以下关键问题：

| 级别 | 问题 | 状态 |
|------|------|------|
| **CRITICAL** | 生产代码泄露明文密码到日志 | 已修复 |
| **CRITICAL** | `.env.example` 包含真实 API Key | 已修复 |
| **CRITICAL** | 默认弱密钥允许 JWT 伪造 | 已修复（启动时强制校验） |
| **CRITICAL** | 登出后 Token 仍有效 | 已修复（Redis 黑名单） |
| **HIGH** | 裸 `except:` 吞掉所有异常 | 已修复（6 处） |
| **HIGH** | 重复 AuthService 实例化 | 已修复（4 处） |
| **HIGH** | CORS `allow_methods=["*"]` | 已修复（限定方法） |
| **HIGH** | 认证路径被排除在限流外 | 已修复 |
| **MEDIUM** | `datetime.utcnow()` 已弃用 | 已修复（→ `datetime.now(timezone.utc)`） |
| **MEDIUM** | Pydantic 验证异常 JSON 序列化崩溃 | 已修复 |

---

## 架构优化

### 前端组件化重构

聊天页面从 **1574 行单文件** 重构为 **5 个子组件 + 5 个组合式函数**：

```
chat/index.vue (230 行)
├── ChatSidebar.vue      — 会话列表侧边栏
├── ChatMessages.vue     — 消息展示区（DynamicScroller）
├── ChatInput.vue        — 输入区（文件附件/模式切换/连接状态）
├── ChatHeader.vue       — 顶部导航（标题/绑定模式/清空）
├── DocumentPreviewModal.vue — 文档预览弹窗
└── composables/
    ├── useChatAttachments.ts  — 文件上传与轮询
    ├── useChatMessages.ts     — 消息展示/滚动/反馈
    ├── useChatSessions.ts     — 会话列表管理
    ├── useChatConnection.ts   — WebSocket/SSE 连接
    └── useChatSend.ts         — 消息发送
```

### RAG 检索管线

系统实现了一套生产级 RAG 检索管线：

```
用户提问
  │
  ├─ 查询理解：意图分类 + 长查询优化 + LLM 查询重写（多候选）
  │
  ├─ 并行召回：BM25 关键词 + KNN 向量（asyncio.gather）
  │
  ├─ RRF 融合：倒数排名融合 + 重写命中加权
  │
  ├─ MMR 去冗余：最大边际相关性（λ=0.65）
  │
  ├─ Cross-Encoder 重排序
  │
  ├─ 后处理：文档去重 + 相关性过滤 + 新鲜度加权
  │
  └─ 缓存：精确缓存 + 语义缓存（余弦相似度 ≥ 0.92）
```

### 基础设施健壮性

| 层级 | 问题 | 方案 |
|------|------|------|
| **依赖注入** | API base URL 用 `split()` 拼接，自定义代理静默失败 | `_normalize_base_url()` — `urlparse` 验证 + 已知后缀剥离 |
| **缓存** | Redis 故障时内存缓存无限增长 | `BoundedLRUCache(OrderedDict)` — 上限 1000 条 LRU 淘汰 |
| **Redis/ES 连接** | 模块级 `redis_client = None` 导入后永不更新 | `_RedisProxy` 代理模式 — 属性访问委托给 holder，延迟初始化 |
| **数据一致性** | 文档标记 INDEXED 后才开始 ES 索引 | ES 索引成功后再更新 DB 状态 |
| **前端容错** | 渲染崩溃白屏 | `ErrorBoundary` 全局包裹，友好错误页 + 刷新/回首页 |
| **请求重试** | 网络抖动/502 直接失败 | Axios 重试拦截器 — 3 次指数退避（1s/2s/4s） |
| **WebSocket** | 固定 5s 重连，服务端未恢复时密集请求 | 指数退避（1s→16s + jitter） |
| **类型安全** | `catch (error: any)` 破坏 TypeScript 推断 | `_extractErrorMessage` 辅助函数 + `unknown` 类型 |

---

## 更新日志

### 2026-05-09（架构深度优化）

**后端**
- API URL 校验：`_normalize_base_url()` 替换脆弱的 `split()` 解析
- 有界 LRU 缓存：Redis 故障时内存不再无限增长
- Redis/ES 生命周期：`_RedisProxy` 代理模式修复导入绑定 bug
- 知识库构建：INDEXED 状态改为 ES 索引成功后才标记

**前端**
- ErrorBoundary 全局包裹，渲染崩溃不再白屏
- Axios 重试拦截器：502/503/504 + 网络错误自动重试 3 次
- WebSocket 指数退避重连（1s→16s + jitter）
- `catch (error: any)` → 类型安全的 `_extractErrorMessage`

**验证**：后端 160 测试 + 前端 91 测试 + 零类型错误

### 2026-05-08（Agent 系统 + 异常体系）

- ReAct Agent：11 个内置工具、上下文压缩、技能学习、子 Agent 委托
- 统一异常层级：13 个异常类，替换裸 HTTPException
- XSS 修复、内存泄漏修复、Landing/Help/About 页面重写
- 后端清理：删除重复 MinIO 模块、接入 OpenTelemetry

### 2026-05-07（TypeScript 类型安全 & 代码质量）

**TypeScript 类型安全**
- 消除前端 137 个 `any` 类型 → 剩余 39 个均为合理用法（catch、泛型约束、Vue Router 断言等）
- 统一 workflow store 与 API 类型定义，消除重复接口
- 新增 `types/api.ts` 集中管理 API 响应类型（OrganizationMember、OrganizationDocument、WorkflowNodeData 等）
- 所有 API 响应 cast 通过 `unknown` 中间层，避免不安全的类型断言
- `vue-tsc --noEmit` 零错误通过

**前端测试**
- 新增 42 个测试用例（chat store 8、workflow store 20、useDebounce/useThrottle 14）
- 总计 91 个 Vitest 用例，7 个测试文件

**ESLint 代码质量**
- 修复 7 个 ESLint 错误（空 catch 块、未使用变量、ts-ignore、常量条件）
- 清理 156 个 ESLint 警告（未使用导入、未使用变量、console 语句）
- ESLint 配置升级为 `@vue/eslint-config-typescript/recommended`
- 最终状态：零错误零警告

**CI/CD 强化**
- `vue-tsc` 类型检查从 `continue-on-error` 改为硬性要求
- 新增 `npm run build` 构建验证步骤
- ESLint 从 `continue-on-error` 改为硬性要求

### 2026-05-07（初始）

**测试**
- 新增 132 个后端 pytest 用例（auth, masking, circuit breaker, RAG, config, parser, API）
- 新增 49 个前端 Vitest 用例（auth, format, retry, websocket）
- 配置 `pytest.ini` 和 `vitest.config.ts`

**CI/CD**
- 新增 GitHub Actions 工作流（后端 Python 3.11/3.12 + 前端 Node 18/20 + Lint）
- 新增 Dependabot 自动依赖更新配置
- 新增 PR 模板

**前端架构**
- 重构 `chat/index.vue`：1574 行 → 230 行，拆分为 5 组件 + 5 组合式函数
- 新增 `useChatConnection` 和 `useChatSend` 组合式函数

**安全**
- 修复 Pydantic 验证异常 JSON 序列化崩溃（`main.py`）

**文档**
- 清理 5 个过时文档（DEVELOPMENT_GUIDE, technical_documentation, 企业级详细文档, 派聪明开发文档, RAG_SYSTEM_SUMMARY）
- 更新 README 项目结构、测试、安全加固、架构优化章节

### 2026-05-06

**安全加固**
- 移除生产代码中的明文密码日志
- 移除 `.env.example` 中的真实 API Key
- 添加 SECRET_KEY / JWT_SECRET_KEY 启动时强制校验
- 添加 JWT Token 黑名单（Redis）实现登出即失效
- 修复 6 处裸 `except:` → 精确异常类型
- 修复 4 处重复 AuthService 实例化
- 修复 CORS 配置（限定方法和头）
- 修复认证路径被排除在限流外
- 修复 `datetime.utcnow()` → `datetime.now(timezone.utc)`
- 添加密码长度校验（8-128 位）

**前端修复**
- 修复 WebSocket `stopGeneration` 双重 JSON 编码
- 移除 `request.ts` 中重复的路由守卫
- 移除 `api/chat.ts` 中重复的函数定义
- 修复 `stores/user.ts` 中 getUserInfo 错误处理
- 添加 `stores/app.ts` 中主题同步防抖

**文档**
- 重写 README（专业架构图、数据流程、API 概览）
- 清理根目录多余文件（bat, sh, txt, package.json）
- 更新 `.env.example`（完整配置说明）

---

## 维护者

- **sijieZ** — [GitHub](https://github.com/sijie-Z/DocMind-RAG) · [Email](mailto:1683039482@qq.com)

---

本项目基于 [MIT License](LICENSE) 开源。如果对你有帮助，欢迎 ⭐ Star！
