"""Agent service — high-level interface for the agent system.

Wires together the agent loop, tools, skills, and context engine
into a single service that the API layer can use.
"""
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

from openai import AsyncOpenAI

from app.agent.loop import AgentConfig, AgentEvent, AgentLoop
from app.agent.skills import skill_manager
from app.agent.registry import tool_registry

logger = logging.getLogger(__name__)

# Force import of tools module to trigger registration
import app.agent.tools  # noqa: F401


class AgentService:
    """High-level agent interface."""

    def __init__(self, openai_client: Optional[AsyncOpenAI] = None):
        self._client = openai_client

    @property
    def client(self) -> Optional[AsyncOpenAI]:
        if self._client is None:
            from app.dependencies import get_rag_pipeline
            pipeline = get_rag_pipeline()
            self._client = pipeline.openai_client
        return self._client

    async def chat(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
        organization_id: int = 1,
        user_id: int = 0,
        enable_tools: bool = True,
        model: str = "deepseek-chat",
    ) -> AsyncGenerator[AgentEvent, None]:
        """Run the agent loop and yield events.

        This is the main entry point for the agent chat API.
        """
        if not self.client:
            yield AgentEvent(type="error", content="LLM not configured.")
            return

        # Load skills
        await skill_manager.load()

        # Check for matching skill
        matched_skill = skill_manager.match(query)
        if matched_skill:
            logger.info(f"Matched skill: {matched_skill.name}")
            yield AgentEvent(
                type="tool_call",
                tool_name="skill",
                tool_args={"skill_id": matched_skill.id, "name": matched_skill.name},
            )

        # Configure agent
        config = AgentConfig(
            model=model,
            enable_tools=enable_tools,
            max_iterations=8,
        )

        # Create and run agent
        agent = AgentLoop(
            openai_client=self.client,
            config=config,
            organization_id=organization_id,
            user_id=user_id,
        )

        async for event in agent.run(query, history=history):
            yield event

    async def search_and_chat(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
        organization_id: int = 1,
        user_id: int = 0,
        top_k: int = 5,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Hybrid mode: retrieve context first, then run agent.

        This combines traditional RAG retrieval with agent capabilities.
        """
        if not self.client:
            yield {"type": "error", "content": "LLM not configured."}
            return

        # Step 1: Retrieve context
        from app.dependencies import get_rag_pipeline
        pipeline = get_rag_pipeline()
        context_docs = await pipeline.search_knowledge_base(
            query=query,
            organization_id=organization_id,
            top_k=top_k,
        )

        if context_docs:
            yield {
                "type": "context",
                "sources": [
                    {
                        "filename": d.get("filename", "Unknown"),
                        "score": d.get("score", 0),
                        "snippet": d.get("snippet", "")[:200],
                    }
                    for d in context_docs
                ],
            }

        # Step 2: Run agent with context
        config = AgentConfig(
            model="deepseek-chat",
            enable_tools=True,
            max_iterations=5,
        )

        agent = AgentLoop(
            openai_client=self.client,
            config=config,
            organization_id=organization_id,
            user_id=user_id,
        )

        async for event in agent.run(query, history=history, context_docs=context_docs):
            yield {"type": event.type, "content": event.content, "tool_name": event.tool_name}


# Singleton
agent_service = AgentService()
