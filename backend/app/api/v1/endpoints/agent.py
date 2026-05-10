"""Agent API endpoint — provides ReAct agent chat via SSE streaming.

Endpoints:
    POST /api/v1/agent/chat         — Agent chat with tool calling
    GET  /api/v1/agent/tools        — List available tools
    GET  /api/v1/agent/skills       — List learned skills
"""
import json
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


class AgentChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    enable_tools: bool = True
    model: str = "deepseek-chat"


@router.post("/chat")
async def agent_chat(
    body: AgentChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Agent chat with tool calling — streams events via SSE."""
    from app.agent.service import agent_service

    async def event_stream():
        async for event in agent_service.chat(
            query=body.query,
            history=[],
            organization_id=current_user.organization_id or 1,
            user_id=current_user.id,
            enable_tools=body.enable_tools,
            model=body.model,
        ):
            data = {
                "type": event.type,
                "content": event.content,
                "tool_name": event.tool_name,
                "iteration": event.iteration,
            }
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/tools", response_model=dict)
async def list_tools(
    current_user: User = Depends(get_current_user),
):
    """List all available agent tools."""
    from app.agent.registry import tool_registry
    tools = tool_registry.list_tools()
    return {
        "success": True,
        "data": [
            {
                "name": t.name,
                "description": t.description,
                "tags": t.tags,
                "parameters": t.parameters,
            }
            for t in tools
        ],
    }


@router.get("/skills", response_model=dict)
async def list_skills(
    current_user: User = Depends(get_current_user),
):
    """List learned agent skills."""
    from app.agent.skills import skill_manager
    await skill_manager.load()
    skills = skill_manager.list_skills()
    return {
        "success": True,
        "data": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "success_rate": round(s.success_rate, 2),
                "trigger_patterns": s.trigger_patterns,
            }
            for s in skills
        ],
    }
