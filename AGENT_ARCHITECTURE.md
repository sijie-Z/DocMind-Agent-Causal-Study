# DocMind Agent Architecture

## Overview

DocMind implements a ReAct-style (Reasoning + Acting) agent system inspired by [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent). The agent can autonomously use tools to search the knowledge base, analyze documents, manage conversations, and compose answers — going beyond simple RAG retrieval.

## Core Design Principles

1. **Single-loop ReAct** — LLM generates tool calls, tools execute, results feed back, repeat until done
2. **Self-registering tools** — Decorator-based tool registration with JSON Schema definitions
3. **Context management** — Automatic conversation compression when approaching token limits
4. **Skill learning** — Successful tool-use patterns are saved as reusable skills
5. **Subagent delegation** — Complex tasks can be split into parallel subtasks

## Architecture Diagram

```
User Query
    │
    ▼
┌─────────────────────────────────────────────┐
│              AgentLoop (loop.py)             │
│  ┌─────────────────────────────────────┐    │
│  │  1. Build messages (system + history)│    │
│  │  2. ContextEngine.fit() — compress  │    │
│  │  3. LLM call with tool definitions  │    │
│  │  4. Parse tool_calls from response  │    │
│  │  5. ToolRegistry.execute() per call │    │
│  │  6. Append results → goto 3         │    │
│  │  7. LLM returns text → done         │    │
│  └─────────────────────────────────────┘    │
│                    │                         │
│         ┌──────────┼──────────┐              │
│         ▼          ▼          ▼              │
│  ┌──────────┐ ┌─────────┐ ┌──────────┐     │
│  │  Tools   │ │ Context │ │  Skills  │     │
│  │ Registry │ │ Engine  │ │ Manager  │     │
│  └──────────┘ └─────────┘ └──────────┘     │
└─────────────────────────────────────────────┘
```

## Module Reference

### `app/agent/registry.py` — Tool Registry

Central registry of all available tools. Tools register themselves via decorator:

```python
@register_tool(
    name="search_knowledge_base",
    description="Search the knowledge base...",
    parameters={"type": "object", "properties": {...}},
    tags=["search"],
)
async def search_knowledge_base(query: str, **ctx) -> str:
    ...
```

Key classes:
- `ToolEntry` — Metadata + handler for a single tool
- `ToolRegistry` — Stores tools, exports OpenAI schemas, executes by name
- `tool_registry` — Global singleton

### `app/agent/tools.py` — Built-in Tools

| Tool | Description | Tags |
|------|-------------|------|
| `search_knowledge_base` | Hybrid retrieval (keyword + vector + RRF) | search |
| `vector_search` | Pure semantic vector search | search |
| `summarize_document` | LLM-powered document summarization | analysis |
| `extract_keywords` | Extract key terms from text | analysis |
| `list_documents` | List documents in knowledge base | management |
| `get_document_info` | Get document metadata and status | management |
| `list_conversations` | List recent chat sessions for current user | conversation |
| `get_conversation_history` | Retrieve messages from a specific session | conversation |
| `list_prompt_templates` | List available prompt templates by category | prompts |
| `get_prompt_template` | Get full content of a prompt template by name | prompts |
| `get_current_time` | Current date/time | utility |

### `app/agent/context.py` — Context Engine

Manages the conversation context window to stay within token limits.

Strategy:
1. System prompt is always preserved (pinned)
2. Recent N messages are always preserved (tail window)
3. Older messages are compressed into a summary

```python
engine = ContextEngine(max_context_tokens=8000, tail_window=6)
fitted = engine.fit(messages, system_prompt="...")
```

### `app/agent/loop.py` — Agent Loop

The core execution engine. Implements the ReAct loop:

```python
agent = AgentLoop(openai_client=client, config=AgentConfig(...))
async for event in agent.run(query, history=history):
    if event.type == "tool_call":
        print(f"Calling {event.tool_name}")
    elif event.type == "chunk":
        print(event.content, end="")
```

Events:
- `tool_call` — LLM wants to call a tool
- `tool_result` — Tool returned a result
- `chunk` — LLM streaming text output
- `error` — Something went wrong
- `done` — Agent finished

### `app/agent/skills.py` — Skill System

Learns successful tool-use patterns for reuse:

```python
await skill_manager.create_skill(
    name="policy_search",
    description="Search for company policy documents",
    trigger_patterns=["政策", "规定", "制度"],
    tool_sequence=[{"name": "search_knowledge_base", "args": {"top_k": 3}}],
)
```

When a new query matches a skill's trigger patterns, the agent can skip planning and execute the skill directly.

### `app/agent/subagent.py` — Subagent Delegation

Spawns child agents for complex subtasks with isolated context:

```python
async for event in delegate_task(client, task="Summarize all policy documents"):
    ...
```

Subagents have:
- Restricted tool access (search + analysis only)
- Lower iteration budget
- Isolated context from parent

### `app/agent/service.py` — Service Layer

High-level interface wiring everything together:

```python
from app.agent.service import agent_service

async for event in agent_service.chat(query="报销流程是什么？"):
    ...
```

### `app/api/v1/endpoints/agent.py` — API Endpoint

REST API for agent interaction:

```
POST /api/v1/agent/chat          — Agent chat (SSE streaming)
GET  /api/v1/agent/tools         — List available tools
GET  /api/v1/agent/skills        — List learned skills
```

## Comparison with hermes-agent

| Feature | hermes-agent | DocMind Agent |
|---------|-------------|---------------|
| Agent loop | ReAct single-loop | ReAct single-loop |
| Tool registry | AST-scanning self-register | Decorator-based self-register |
| Context engine | ContextCompressor | ContextEngine with tail window |
| Skills | Curator (background maintenance) | SkillManager (Redis-backed) |
| Subagents | delegate_task with child AIAgent | delegate_task with child AgentLoop |
| Memory | Honcho/mem0 providers | Redis + semantic cache |
| Streaming | OpenAI streaming | SSE via FastAPI StreamingResponse |

## Running Tests

```bash
cd backend && python -m pytest tests/ -v
```

## API Usage

```bash
# Agent chat (SSE stream)
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "报销流程是什么？", "enable_tools": true}'

# List tools
curl http://localhost:8000/api/v1/agent/tools \
  -H "Authorization: Bearer <token>"
```
