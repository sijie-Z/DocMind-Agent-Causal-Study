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
2. 如果需要查找信息，使用 search_knowledge_base 工具
3. 如果需要回顾之前的对话，使用 list_conversations 和 get_conversation_history
4. 如果需要特定提示词模板，使用 list_prompt_templates 和 get_prompt_template
5. 基于检索到的文档内容回答问题
6. 如果文档中没有相关信息，明确告知用户

## 约束
- 只基于知识库中的文档回答，不编造信息
- 使用 [n] 格式标注引用来源
- 始终使用简体中文回答
- 如果不确定，使用工具搜索确认"""


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

            # Execute tools (batch parallel when possible)
            tool_events = []
            for tc in message.tool_calls[:self.config.max_tool_calls_per_turn]:
                if self._tool_call_count >= self.config.max_iterations * self.config.max_tool_calls_per_turn:
                    yield AgentEvent(
                        type="error",
                        content="Tool call limit reached.",
                        iteration=self._iteration,
                    )
                    return

                func = tc.function
                try:
                    args = json.loads(func.arguments) if func.arguments else {}
                except json.JSONDecodeError:
                    args = {}

                yield AgentEvent(
                    type="tool_call",
                    tool_name=func.name,
                    tool_args=args,
                    iteration=self._iteration,
                )

                # Execute tool
                start = time.perf_counter()
                result = await tool_registry.execute(
                    func.name,
                    args,
                    organization_id=self.organization_id,
                    user_id=self.user_id,
                )
                elapsed = (time.perf_counter() - start) * 1000
                self._tool_call_count += 1

                # Truncate very long tool results
                if len(result) > 4000:
                    result = result[:4000] + "\n...[result truncated]"

                yield AgentEvent(
                    type="tool_result",
                    tool_name=func.name,
                    content=result,
                    iteration=self._iteration,
                )

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

                logger.info(f"Tool {func.name} executed in {elapsed:.0f}ms")

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
