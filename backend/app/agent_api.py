"""DocMind Agent Service API — stateless FastAPI interface for agent execution.

Endpoints:
    POST /chat     — Run agent, return answer + metrics
    POST /trace    — Run agent, return full execution trace
    POST /plan     — Run planner only, return decomposition

Usage:
    cd backend && uvicorn app.agent_api:app --host 0.0.0.0 --port 8010 --reload

    curl -X POST http://localhost:8010/chat \
      -H "Content-Type: application/json" \
      -d '{"query": "对比星辰科技和远方创新的财务表现", "mode": "structured"}'
"""
import os, sys, json, asyncio, time, uuid, logging
from pathlib import Path

# ── Bootstrap ────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import logging
logging.disable(logging.CRITICAL)

os.environ.setdefault("DEEPSEEK_API_KEY", "056beadf58874c58b9b7f121f4f3e7e6.un6ZXWawRWlfH6c3")
os.environ.setdefault("DEEPSEEK_API_URL", "https://open.bigmodel.cn/api/paas/v4/")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from app.agent.config import AgentConfig
from app.agent.loop import PERAgentLoop
from app.agent.planner import Plan, PlanStep
from app.core.step_runner import StepRunner, safe_run, StepResult, StepError

import app.agent.service  # noqa: F401 — register tools

LLM_MODEL = "glm-4-flash"
AGENT_TIMEOUT = 90.0  # max seconds for entire agent run

# ── Pydantic schemas ─────────────────────────────────────────

class AgentRequest(BaseModel):
    query: str = Field(..., description="User query")
    mode: str = Field(default="structured")
    expected_keywords: list[str] = Field(default_factory=list)


class StepInfo(BaseModel):
    id: str
    description: str
    dependencies: list[str] = []
    tool_hint: str = ""
    status: str = ""


class ToolCallInfo(BaseModel):
    step_id: str
    tool_name: str
    args: dict = {}
    result: str = ""
    duration_ms: float = 0.0
    status: str = ""


class ErrorInfo(BaseModel):
    step_id: str = ""
    type: str = "unknown"
    message: str = ""
    recoverable: bool = False


class TraceResponse(BaseModel):
    request_id: str
    query: str
    mode: str
    plan: list[StepInfo] = []
    execution: list[ToolCallInfo] = []
    answer: str = ""
    coverage: float = 0.0
    latency_seconds: float = 0.0
    steps: int = 0
    tool_calls: int = 0
    errors: list[ErrorInfo] = []


# ── App ──────────────────────────────────────────────────────

app = FastAPI(
    title="DocMind Agent Service",
    description="Agent execution service with trace-level observability",
    version="2.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Orchestrator ─────────────────────────────────────────────

async def run_agent(
    query: str,
    mode: str = "structured",
    expected_keywords: list[str] | None = None,
) -> dict:
    """Execute the agent and return structured result."""
    request_id = uuid.uuid4().hex[:12]
    client = AsyncOpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ.get("DEEPSEEK_API_URL"),
    )

    config = AgentConfig(
        model=LLM_MODEL,
        enable_planning=(mode == "structured"),
        enable_reflection=False,
        enable_memory=False,
        enable_thinking=False,
        enable_tools=True,
        enable_experience=False,
        max_plan_steps=12,
        max_iterations=10,
        max_retries_per_step=1,
    )

    agent = PERAgentLoop(
        client, config, organization_id=3, user_id=0, execution_mode="dag",
    )

    plan_steps: list[dict] = []
    tool_calls: list[dict] = []
    chunks: list[str] = []
    errors: list[dict] = []
    step_errors: list[dict] = []
    start = time.perf_counter()

    # Wrap entire agent run with StepRunner
    async def run_agent_loop():
        async for event in agent.run(query):
            if event.type == "plan_step":
                plan_steps.append({
                    "id": event.plan_step_id,
                    "description": event.content,
                    "dependencies": event.dependencies or [],
                    "tool_hint": event.tool_hint or "",
                    "status": "ready",
                })
            elif event.type == "tool_call":
                tool_calls.append({
                    "step_id": event.plan_step_id,
                    "tool_name": event.tool_name,
                    "args": event.tool_args,
                    "result": "",
                    "duration_ms": 0.0,
                    "status": "running",
                })
            elif event.type == "tool_result":
                if tool_calls:
                    tc = tool_calls[-1]
                    tc["result"] = event.content[:300]
                    tc["duration_ms"] = event.tool_duration_ms
                    tc["status"] = "success"
            elif event.type == "tool_error":
                step_errors.append({
                    "step_id": event.plan_step_id,
                    "type": f"tool_error:{event.tool_name}",
                    "message": event.content[:200],
                    "recoverable": True,
                })
                if tool_calls:
                    tool_calls[-1]["status"] = "error"
                    tool_calls[-1]["result"] = event.content[:200]
            elif event.type == "chunk":
                chunks.append(event.content)
        return True

    runner = StepRunner(timeout=AGENT_TIMEOUT, max_retries=0, step_id=request_id)
    result = await runner.run(run_agent_loop)

    duration = time.perf_counter() - start

    if not result.success and not chunks:
        errors.append({
            "step_id": request_id,
            "type": result.error_type or "agent_failure",
            "message": result.error or "Agent execution failed",
            "recoverable": result.recoverable,
        })
        answer = f"[System error: {result.error}]"
    else:
        answer = "".join(chunks) or "(no answer)"
        errors = step_errors

    # Coverage scoring
    coverage = 0.0
    if expected_keywords and answer:
        al = answer.lower()
        found = sum(1 for kw in expected_keywords if kw.lower() in al)
        coverage = found / len(expected_keywords)

    return {
        "request_id": request_id,
        "query": query,
        "mode": mode,
        "plan": plan_steps,
        "execution": tool_calls,
        "answer": answer,
        "coverage": round(coverage, 3),
        "latency_seconds": round(duration, 2),
        "steps": len(plan_steps),
        "tool_calls": len(tool_calls),
        "errors": errors,
    }


# ── Endpoints ────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "docmind-agent"}


@app.post("/chat", response_model=TraceResponse)
async def chat(req: AgentRequest):
    """Run agent, return answer + metrics (no full trace)."""
    result = await run_agent(
        query=req.query,
        mode=req.mode,
        expected_keywords=req.expected_keywords,
    )
    # Strip execution details for /chat (keep summary)
    result.pop("execution", None)
    # Truncate plan detail
    result["plan"] = [
        {"id": s["id"], "description": s["description"]}
        for s in result["plan"]
    ]
    return result


@app.post("/trace", response_model=TraceResponse)
async def trace(req: AgentRequest):
    """Run agent, return full execution trace."""
    return await run_agent(
        query=req.query,
        mode=req.mode,
        expected_keywords=req.expected_keywords,
    )


@app.post("/plan")
async def plan(req: AgentRequest):
    """Run planner only, return decomposition."""
    result = await run_agent(
        query=req.query,
        mode=req.mode,
    )
    return {
        "request_id": result["request_id"],
        "query": result["query"],
        "mode": result["mode"],
        "steps": len(result["plan"]),
        "plan": result["plan"],
        "latency_seconds": result["latency_seconds"],
    }


# ── Run ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
