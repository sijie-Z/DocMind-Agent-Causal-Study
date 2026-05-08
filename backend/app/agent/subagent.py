"""Subagent delegation — spawn child agents for complex subtasks.

A parent agent can delegate a subtask to a child agent with its own
isolated context, restricted toolset, and iteration budget. The child
returns a summary to the parent.

Inspired by hermes-agent's delegate_task pattern.
"""
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

from openai import AsyncOpenAI

from app.agent.loop import AgentConfig, AgentEvent, AgentLoop
from app.agent.registry import tool_registry

logger = logging.getLogger(__name__)

# Tools that subagents can use (restricted set)
SUBAGENT_ALLOWED_TAGS = ["search", "analysis"]


async def delegate_task(
    client: AsyncOpenAI,
    task: str,
    parent_context: str = "",
    model: str = "deepseek-chat",
    max_iterations: int = 5,
    organization_id: int = 1,
) -> AsyncGenerator[AgentEvent, None]:
    """Delegate a subtask to a child agent.

    Args:
        client: OpenAI client for LLM calls.
        task: The subtask description.
        parent_context: Context from the parent agent (e.g., what's been found so far).
        model: Model to use for the child agent.
        max_iterations: Maximum iterations for the child.
        organization_id: Organization scope.

    Yields:
        AgentEvent objects from the child agent's execution.
    """
    child_config = AgentConfig(
        model=model,
        max_iterations=max_iterations,
        max_tool_calls_per_turn=3,
        tool_tags=SUBAGENT_ALLOWED_TAGS,
        system_prompt_override=(
            f"你是 DocMind 子任务代理。你的任务是：{task}\n\n"
            f"## 父代理上下文\n{parent_context}\n\n"
            "请使用工具完成任务，然后给出简洁的结论。"
        ),
    )

    child = AgentLoop(
        openai_client=client,
        config=child_config,
        organization_id=organization_id,
    )

    async for event in child.run(task):
        yield event


async def run_parallel_subtasks(
    client: AsyncOpenAI,
    tasks: List[str],
    model: str = "deepseek-chat",
    organization_id: int = 1,
) -> List[str]:
    """Execute multiple subtasks in parallel and collect results.

    Returns a list of final answers from each subtask.
    """
    results = []

    async def _run_one(task: str) -> str:
        answer_parts = []
        async for event in delegate_task(
            client=client,
            task=task,
            model=model,
            organization_id=organization_id,
        ):
            if event.type == "chunk":
                answer_parts.append(event.content)
            elif event.type == "error":
                answer_parts.append(f"[Error: {event.content}]")
        return "".join(answer_parts) or "No result."

    # Run in parallel with gather
    results = await _gather_with_concurrency(
        [_run_one(task) for task in tasks],
        max_concurrency=3,
    )
    return results


async def _gather_with_concurrency(coros, max_concurrency: int = 3):
    """Run coroutines with limited concurrency."""
    semaphore = __import__("asyncio").Semaphore(max_concurrency)

    async def _wrap(coro):
        async with semaphore:
            return await coro

    import asyncio
    return await asyncio.gather(*[_wrap(c) for c in coros])
