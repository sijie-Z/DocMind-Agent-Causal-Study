#!/usr/bin/env python3
"""Agent Execution Replay CLI.

Replay, inspect, and diff any saved agent execution.

Usage:
    # Replay a specific task
    python -m benchmark.replay <task_id>

    # Diff two tasks
    python -m benchmark.replay --diff <task_a> <task_b>

    # List all saved replays
    python -m benchmark.replay --list

    # Save a task from Redis to local JSON
    python -m benchmark.replay --save <task_id>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure backend is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agent.replay.engine import ReplayEngine, REPLAY_DIR

REPLAY_DIR.mkdir(parents=True, exist_ok=True)


async def cmd_replay(task_id: str) -> None:
    """Replay a single execution."""
    engine = ReplayEngine()
    ctx = await engine.load(task_id)
    if not ctx:
        print(f"❌ Task not found: {task_id}")
        print(f"   Looked in Redis and {REPLAY_DIR}/")
        sys.exit(1)
    print(engine.format_replay(ctx))


async def cmd_diff(task_a: str, task_b: str) -> None:
    """Diff two executions."""
    engine = ReplayEngine()
    ctx_a = await engine.load(task_a)
    ctx_b = await engine.load(task_b)
    if not ctx_a:
        print(f"❌ Task not found: {task_a}")
        sys.exit(1)
    if not ctx_b:
        print(f"❌ Task not found: {task_b}")
        sys.exit(1)
    print(engine.format_diff(ctx_a, ctx_b))


async def cmd_list() -> None:
    """List all saved replays."""
    engine = ReplayEngine()
    files = sorted(REPLAY_DIR.glob("*.json"))
    if not files:
        print(f"  No replays found in {REPLAY_DIR}/")
        return
    print(f"  Saved replays ({len(files)}):")
    for f in files:
        ctx = engine.load_sync(str(f))
        if ctx:
            print(engine.format_summary(ctx))


async def cmd_save(task_id: str) -> None:
    """Save a task from Redis to local JSON."""
    engine = ReplayEngine()
    ctx = await engine.load(task_id)
    if not ctx:
        print(f"❌ Task not found: {task_id}")
        sys.exit(1)
    path = REPLAY_DIR / f"{task_id}.json"
    path.write_text(json.dumps(ctx, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Saved to {path}")


def main():
    parser = argparse.ArgumentParser(description="Agent Execution Replay")
    parser.add_argument("task_id", nargs="?", help="Task ID to replay")
    parser.add_argument("--diff", nargs=2, metavar=("TASK_A", "TASK_B"),
                        help="Compare two executions")
    parser.add_argument("--list", action="store_true", help="List all saved replays")
    parser.add_argument("--save", metavar="TASK_ID", help="Save a task to local JSON")
    args = parser.parse_args()

    import asyncio

    if args.list:
        asyncio.run(cmd_list())
    elif args.diff:
        asyncio.run(cmd_diff(args.diff[0], args.diff[1]))
    elif args.save:
        asyncio.run(cmd_save(args.save))
    elif args.task_id:
        asyncio.run(cmd_replay(args.task_id))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
