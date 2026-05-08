"""Agent system — ReAct-style tool-calling agent inspired by hermes-agent.

Architecture:
    registry.py  — Self-registering tool system with JSON schemas
    tools.py     — Built-in tools (search, analyze, summarize, sql, etc.)
    context.py   — Context window management and compression
    loop.py      — Core ReAct agent loop (LLM → tool call → observe → repeat)
    skills.py    — Procedural memory: learned tool-use patterns from past runs
    subagent.py  — Delegation: spawn child agents for complex subtasks

Execution flow:
    User query → AgentLoop.run()
        → Build system prompt (tools + skills + context)
        → LLM generates tool calls or final answer
        → ToolRegistry.execute(tool_name, args)
        → Append observation to conversation
        → Repeat until LLM returns text (no more tool calls)
"""
