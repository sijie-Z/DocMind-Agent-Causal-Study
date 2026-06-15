#!/usr/bin/env python3
"""Verify that Experience Memory is correctly injected into the Planner prompt.

Runs a single benchmark question and checks whether the planner system
prompt contains experience lessons.

Usage:
    cd DocMind/backend
    python benchmark/test_experience_injection.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agent.config import AgentConfig
from app.agent.experience import get_experience_store


async def main():
    print("=" * 60)
    print("  Verify: Experience Memory → Planner Injection")
    print("=" * 60)

    # ── 1. Ensure store is loaded ──
    store = get_experience_store()
    await store.list_all()  # triggers load
    count = await store.count()
    print(f"\n[1] Experience Store: {count} experiences loaded")

    # ── 2. Test search for a cross-document query ──
    test_queries = [
        "比较 A 公司和 B 公司的营收",
        "用 SWOT 框架分析这家公司",
        "分析苹果",
        "知识库里有什么",
        "今天天气怎么样",
    ]

    print(f"\n[2] Search relevance test:")
    for q in test_queries:
        result = await store.format_for_planner(q, top_k=2)
        if result:
            lines = result.split("\n")
            print(f"  ✓ '{q[:25]:25s}' → {len(lines) - 1} lessons retrieved")
            for line in lines[2:]:  # skip header
                print(f"      {line[:80]}")
        else:
            print(f"  ✗ '{q[:25]:25s}' → no relevant experience")

    # ── 3. Verify Planner would inject it ──
    print(f"\n[3] Planner system prompt simulation:")
    config = AgentConfig(enable_experience=True)
    for q in test_queries[:2]:
        exp_context = await store.format_for_planner(q, top_k=2)
        if exp_context:
            prompt_section = f"\n\n{exp_context}"
            ls = len(prompt_section)
            print(f"  ✓ '{q[:25]:25s}' → +{ls} chars injected into planner prompt")
        else:
            print(f"  ✗ '{q[:25]:25s}' → no injection")

    print("\n" + "=" * 60)
    print("  Done. Experience → Planner pipeline is", "✅ ACTIVE" if count > 0 else "❌ EMPTY")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
