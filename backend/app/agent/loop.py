"""ReAct agent loop — the core execution engine.

Flow:
    1. Build system prompt (role + tools + skills + context)
    2. Send messages to LLM with tool definitions
    3. If LLM returns tool_calls → execute them → append results → goto 2
    4. If LLM returns text → yield as final answer
    5. Repeat until max iterations or LLM stops calling tools

Supports streaming: yields events as they happen (tool calls, observations, chunks).
"""
import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Dict, List, Optional

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.agent.context import ContextEngine, estimate_messages_tokens
from app.agent.registry import tool_registry, ToolEntry

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 10
MAX_TOOL_CALLS_PER_TURN = 5
MAX_RESULT_TOKENS = 3000


def _smart_truncate(result: str, tool_name: str) -> str:
    """Smart truncation that preserves structure based on tool type."""
    if not result or len(result) <= MAX_RESULT_TOKENS * 2:
        return result

    # For list-type results, keep first N items
    if tool_name in ("list_documents", "list_conversations", "list_prompt_templates"):
        lines = result.split("\n")
        kept = lines[:15]
        remaining = len(lines) - 15
        if remaining > 0:
            kept.append(f"... and {remaining} more items")
        return "\n".join(kept)

    # For search results, keep top results with summaries
    if tool_name in ("search_knowledge_base", "vector_search"):
        # Keep first 3 results fully, truncate rest
        sections = result.split("\n\n")
        if len(sections) > 3:
            return "\n\n".join(sections[:3]) + f"\n\n... and {len(sections) - 3} more results omitted"
        return result

    # For document content, keep beginning and end
    if tool_name in ("summarize_document", "get_conversation_history"):
        head = result[:1500]
        tail = result[-500:]
        return f"{head}\n\n... [middle section omitted] ...\n\n{tail}"

    # Default: hard truncate with clear marker
    return result[:MAX_RESULT_TOKENS * 2] + "\n...[result truncated for context efficiency]"


@dataclass
class AgentEvent:
    """An event emitted during agent execution."""
    type: str  # "tool_call", "tool_result", "chunk", "error", "done"
    content: str = ""
    tool_name: str = ""
    tool_args: Dict[str, Any] = field(default_factory=dict)
    iteration: int = 0


@dataclass
class AgentConfig:
    """Agent execution configuration."""
    model: str = "deepseek-chat"
    temperature: float = 0.1
    max_tokens: int = 2048
    max_iterations: int = MAX_ITERATIONS
    max_tool_calls_per_turn: int = MAX_TOOL_CALLS_PER_TURN
    enable_tools: bool = True
    tool_tags: Optional[List[str]] = None
    system_prompt_override: Optional[str] = None
    timeout: float = 60.0


DEFAULT_SYSTEM_PROMPT = """你是 DocMind 智能助手，一个基于企业知识库的 AI Agent。

## 能力
你可以使用工具来完成任务：
- 搜索知识库：混合检索（关键词 + 向量 + RRF 融合）
- 分析文档：摘要、提取关键词
- 管理文档：查看文档列表和详情
- 对话管理：查看历史对话和消息记录
- 提示词模板：查找和使用预设提示词模板

## 工作流程
1. 理解用户意图
2. **复杂任务自动拆解**：如果用户的请求涉及多个步骤（如"分析这 10 份报告的共同风险"），先制定执行计划，再逐步执行
3. 如果需要查找信息，使用 search_knowledge_base 工具
4. 如果需要分析多个文档，逐个调用 summarize_document，然后综合分析
5. 如果需要回顾之前的对话，使用 list_conversations 和 get_conversation_history
6. 基于检索到的文档内容回答问题
7. 如果文档中没有相关信息，明确告知用户

## 复杂任务处理策略
当用户请求涉及以下模式时，自动拆解为子任务：
- **多文档分析**："分析/比较/总结这些文档" → 逐个检索 + 摘要 → 综合对比
- **深度调研**："深入了解 X" → 多轮搜索（不同关键词） → 整合结果
- **流程指导**："如何做 X" → 搜索相关文档 → 提取步骤 → 生成指南
- **数据提取**："找出所有 X" → 搜索 → 过滤 → 结构化输出

## 约束
- 只基于知识库中的文档回答，不编造信息
- 使用 [n] 格式标注引用来源
- 始终使用简体中文回答
- 如果不确定，使用工具搜索确认
- 复杂任务要分步执行，每步用工具获取数据，最后综合分析"""


class AgentLoop:
    """Core ReAct agent loop.

    Orchestrates the conversation between the user, LLM, and tools.
    """

    def __init__(
        self,
        openai_client: AsyncOpenAI,
        config: Optional[AgentConfig] = None,
        organization_id: int = 1,
        user_id: int = 0,
    ):
        self.client = openai_client
        self.config = config or AgentConfig()
        self.organization_id = organization_id
        self.user_id = user_id
        self.context_engine = ContextEngine(
            max_context_tokens=8000,
            tail_window=6,
        )
        self._iteration = 0
        self._tool_call_count = 0

    async def run(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
        context_docs: Optional[List[Dict[str, Any]]] = None,
    ) -> AsyncGenerator[AgentEvent, None]:
        """Execute the agent loop, yielding events as they happen.

        Args:
            query: The user's question or request.
            history: Previous conversation messages.
            context_docs: Pre-retrieved document context (optional).

        Yields:
            AgentEvent objects for tool calls, results, and streaming chunks.
        """
        self._iteration = 0
        self._tool_call_count = 0

        # Build initial messages
        messages = self._build_messages(query, history, context_docs)
        tools = self._get_tools()

        while self._iteration < self.config.max_iterations:
            self._iteration += 1

            # Apply context window management
            fitted_messages = self.context_engine.fit(
                messages,
                system_prompt=self.config.system_prompt_override or DEFAULT_SYSTEM_PROMPT,
            )

            try:
                response = await self.client.chat.completions.create(
                    model=self.config.model,
                    messages=fitted_messages,  # type: ignore
                    tools=tools if tools and self.config.enable_tools else None,
                    tool_choice="auto" if tools and self.config.enable_tools else None,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    timeout=self.config.timeout,
                )
            except Exception as e:
                logger.error(f"LLM call failed on iteration {self._iteration}: {e}")
                yield AgentEvent(type="error", content=f"LLM Error: {e}", iteration=self._iteration)
                return

            message = response.choices[0].message

            # If no tool calls, we're done
            if not message.tool_calls:
                content = message.content or ""
                if content:
                    yield AgentEvent(type="chunk", content=content, iteration=self._iteration)
                yield AgentEvent(type="done", iteration=self._iteration)
                return

            # Process tool calls
            # Add the assistant message (with tool_calls) to history
            messages.append(message.model_dump())  # type: ignore

            # Execute tools in parallel when multiple tool calls are returned
            tool_calls = message.tool_calls[:self.config.max_tool_calls_per_turn]

            # Check tool call budget
            if self._tool_call_count + len(tool_calls) > self.config.max_iterations * self.config.max_tool_calls_per_turn:
                yield AgentEvent(
                    type="error",
                    content="Tool call limit reached.",
                    iteration=self._iteration,
                )
                return

            # Parse all arguments and emit tool_call events upfront
            parsed_calls = []
            for tc in tool_calls:
                func = tc.function
                try:
                    args = json.loads(func.arguments) if func.arguments else {}
                except json.JSONDecodeError:
                    args = {}
                parsed_calls.append((tc, func, args))
                yield AgentEvent(
                    type="tool_call",
                    tool_name=func.name,
                    tool_args=args,
                    iteration=self._iteration,
                )

            # Execute all tools concurrently
            async def _exec_one(tc, func, args):
                start = time.perf_counter()
                result = await tool_registry.execute(
                    func.name,
                    args,
                    organization_id=self.organization_id,
                    user_id=self.user_id,
                )
                elapsed = (time.perf_counter() - start) * 1000
                result = _smart_truncate(result, func.name)
                logger.info(f"Tool {func.name} executed in {elapsed:.0f}ms")
                return tc, func, result

            results = await asyncio.gather(
                *[_exec_one(tc, func, args) for tc, func, args in parsed_calls],
                return_exceptions=True,
            )

            self._tool_call_count += len(tool_calls)

            for item in results:
                if isinstance(item, Exception):
                    yield AgentEvent(type="error", content=str(item), iteration=self._iteration)
                    continue
                tc, func, result = item
                yield AgentEvent(
                    type="tool_result",
                    tool_name=func.name,
                    content=result,
                    iteration=self._iteration,
                )
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

        # Max iterations reached
        yield AgentEvent(
            type="error",
            content=f"Reached maximum iterations ({self.config.max_iterations}).",
            iteration=self._iteration,
        )

    def _build_messages(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]],
        context_docs: Optional[List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """Build the initial message list for the LLM."""
        messages: List[Dict[str, Any]] = []

        # System prompt
        system_prompt = self.config.system_prompt_override or DEFAULT_SYSTEM_PROMPT
        if context_docs:
            context_str = "\n\n".join([
                f"[{i+1}] {doc.get('filename', 'Unknown')}:\n{doc.get('snippet', doc.get('text', ''))[:500]}"
                for i, doc in enumerate(context_docs[:5])
            ])
            system_prompt += f"\n\n## 已检索到的参考文档\n{context_str}"

        messages.append({"role": "system", "content": system_prompt})

        # History
        if history:
            for msg in history[-8:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if content and role in ("user", "assistant"):
                    messages.append({"role": role, "content": content})

        # Current query
        messages.append({"role": "user", "content": query})

        return messages

    def _get_tools(self) -> Optional[List[Dict[str, Any]]]:
        """Get tool definitions for the LLM."""
        if not self.config.enable_tools:
            return None
        tools = tool_registry.to_openai_tools(self.config.tool_tags)
        return tools if tools else None
