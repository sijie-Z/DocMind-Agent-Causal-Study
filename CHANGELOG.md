# DocMind 更新日志

本文档记录项目的所有重要变更，方便追溯和查询。

---

## 2026-05-07

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
| 后端 | FastAPI + SQLAlchemy(async) + MySQL 8 + Redis + Elasticsearch 8 + Kafka + MinIO |
| AI/RAG | DeepSeek API + OpenAI 兼容 Embedding + LangChain 文档解析 |
| 前端 | Vue 3 + TypeScript + Vite + Naive UI + Pinia + Vue Router |
| 安全 | JWT + RBAC + Token 黑名单 + bcrypt + CORS + 限流 |
| 测试 | pytest (132) + Vitest (49) |
| CI/CD | GitHub Actions + Dependabot |
