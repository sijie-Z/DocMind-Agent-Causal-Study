"""ReplayEngine — formats saved ExecutionContext snapshots for human-readable playback.

Usage:
    engine = ReplayEngine()
    ctx = await engine.load("B017")
    engine.print_replay(ctx)
    engine.print_summary(ctx)

    # Diff two runs
    engine.print_diff(ctx_a, ctx_b)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPLAY_DIR = Path("benchmark/replay")


class ReplayEngine:
    """Loads and formats ExecutionContext snapshots for replay."""

    # ── Load ──────────────────────────────────────────────────────────────

    async def load(self, task_id: str) -> dict[str, Any] | None:
        """Load a saved execution context by task_id.

        Supports partial ID matching (e.g. "abc123" matches "abc123def456").
        Tries Redis first, then local benchmark/replay/ directory.
        """
        # Try Redis
        try:
            from app.agent.exec_context import ExecutionContext
            ctx = await ExecutionContext.load(task_id)
            if ctx:
                return ctx
        except Exception:
            pass

        # Try local file — exact match first, then partial prefix match
        exact = REPLAY_DIR / f"{task_id}.json"
        if exact.exists():
            return json.loads(exact.read_text(encoding="utf-8"))

        # Partial prefix match
        if REPLAY_DIR.exists():
            for f in REPLAY_DIR.glob("*.json"):
                if f.stem.startswith(task_id):
                    return json.loads(f.read_text(encoding="utf-8"))

        return None

    def load_sync(self, path: str) -> dict[str, Any] | None:
        """Synchronous load from a local JSON file."""
        p = Path(path)
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return None

    # ── Formatting ────────────────────────────────────────────────────────

    def format_replay(self, ctx: dict[str, Any]) -> str:
        """Format a full execution replay as a human-readable string."""
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append(f"  Execution Replay: {ctx.get('task_id', 'unknown')}")
        lines.append("=" * 60)
        lines.append(f"  Query:   {ctx.get('query', '')[:100]}")
        lines.append(f"  Goal:    {ctx.get('goal', '')[:80]}")
        lines.append(f"  Plan:    {ctx.get('plan_summary', '')}")
        lines.append(f"  Elapsed: {ctx.get('duration_ms', 0) / 1000:.1f}s")
        lines.append(f"  Tokens:  {ctx.get('total_tokens', 0)}")
        lines.append(f"  Steps:   {ctx.get('steps_completed', 0)}")
        lines.append(f"  Findings:{len(ctx.get('findings', []))}")
        lines.append(f"  Failures:{len(ctx.get('failures', []))}")
        lines.append("")

        # Steps
        steps = ctx.get("steps", [])
        if not steps:
            lines.append("  (no step data recorded)")
        else:
            lines.append("  ── Execution Steps ──")
            for i, step in enumerate(steps, 1):
                lines.append(self._format_step(i, step))

        # Findings
        findings = ctx.get("findings", [])
        if findings:
            lines.append("")
            lines.append("  ── Key Findings ──")
            for f in findings[:5]:
                lines.append(f"    [{f['source_step']}] {f.get('content', '')[:120]}")
            if len(findings) > 5:
                lines.append(f"    ... and {len(findings) - 5} more findings")

        # Decisions
        decisions = ctx.get("decisions", [])
        if decisions:
            lines.append("")
            lines.append("  ── Key Decisions ──")
            for d in decisions:
                lines.append(f"    [{d['phase']}] {d['action']}: {d.get('reasoning', '')[:100]}")

        # Failures
        failures = ctx.get("failures", [])
        if failures:
            lines.append("")
            lines.append(f"  ── Failures ({len(failures)}) ──")
            for f in failures:
                lines.append(f"    ❌ {f[:150]}")

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)

    def format_summary(self, ctx: dict[str, Any]) -> str:
        """One-line summary for listing multiple executions."""
        task_id = ctx.get("task_id", "????")[:8]
        query = ctx.get("query", "")[:40]
        steps = ctx.get("steps_completed", 0)
        duration = ctx.get("duration_ms", 0) / 1000
        fails = len(ctx.get("failures", []))
        findings = len(ctx.get("findings", []))
        status = "❌" if fails > 0 else "✅"
        return f"  {status} [{task_id}] {query:<40s} {steps} steps, {duration:.1f}s, {findings} findings, {fails} failures"

    # ── Diff ──────────────────────────────────────────────────────────────

    def format_diff(self, ctx_a: dict[str, Any], ctx_b: dict[str, Any]) -> str:
        """Side-by-side comparison of two execution contexts."""
        lines: list[str] = []
        lines.append("=" * 70)
        lines.append(f"  Execution Diff: {ctx_a.get('task_id', 'A')[:8]} vs {ctx_b.get('task_id', 'B')[:8]}")
        lines.append("=" * 70)

        # Overall comparison
        dur_a = ctx_a.get("duration_ms", 0) / 1000
        dur_b = ctx_b.get("duration_ms", 0) / 1000
        steps_a = ctx_a.get("steps_completed", 0)
        steps_b = ctx_b.get("steps_completed", 0)
        fails_a = len(ctx_a.get("failures", []))
        fails_b = len(ctx_b.get("failures", []))
        find_a = len(ctx_a.get("findings", []))
        find_b = len(ctx_b.get("findings", []))

        lines.append(f"  {'Metric':<20} {'Run A':<15} {'Run B':<15} {'Delta':<10}")
        lines.append(f"  {'-'*20} {'-'*15} {'-'*15} {'-'*10}")
        lines.append(f"  {'Duration':<20} {dur_a:<14.1f}s {dur_b:<14.1f}s {dur_b - dur_a:+8.1f}s")
        lines.append(f"  {'Steps':<20} {steps_a:<15d} {steps_b:<15d} {steps_b - steps_a:+8d}")
        lines.append(f"  {'Findings':<20} {find_a:<15d} {find_b:<15d} {find_b - find_a:+8d}")
        lines.append(f"  {'Failures':<20} {fails_a:<15d} {fails_b:<15d} {fails_b - fails_a:+8d}")
        lines.append("")

        # Step-by-step comparison
        steps_list_a = ctx_a.get("steps", [])
        steps_list_b = ctx_b.get("steps", [])
        max_steps = max(len(steps_list_a), len(steps_list_b))

        lines.append("  ── Step Comparison ──")
        for i in range(max_steps):
            step_a = steps_list_a[i] if i < len(steps_list_a) else None
            step_b = steps_list_b[i] if i < len(steps_list_b) else None
            label_a = self._step_label(step_a) if step_a else "(no step)"
            label_b = self._step_label(step_b) if step_b else "(no step)"
            dur_a_s = f"{step_a['duration_ms']:.1f}s" if step_a else "-"
            dur_b_s = f"{step_b['duration_ms']:.1f}s" if step_b else "-"
            status_a = self._step_status_icon(step_a) if step_a else " "
            status_b = self._step_status_icon(step_b) if step_b else " "

            marker = "  " if step_a and step_b else " ←" if step_b else " →"
            lines.append(
                f"  Step {i+1}: {status_a} {label_a:<35s} {dur_a_s:>7s}  |  "
                f"{status_b} {label_b:<35s} {dur_b_s:>7s}{marker}"
            )

        # Show added / removed steps
        if steps_list_b and steps_list_a:
            tools_a = {s["tool_used"] for s in steps_list_a if s.get("tool_used")}
            tools_b = {s["tool_used"] for s in steps_list_b if s.get("tool_used")}
            added_tools = tools_b - tools_a
            removed_tools = tools_a - tools_b
            if added_tools:
                lines.append(f"\n  ➕ New tools: {', '.join(sorted(added_tools))}")
            if removed_tools:
                lines.append(f"  ➖ Removed tools: {', '.join(sorted(removed_tools))}")

        lines.append("")
        lines.append("=" * 70)
        return "\n".join(lines)

    # ── Internal helpers ──

    @staticmethod
    def _format_step(i: int, step: dict) -> str:
        tool = step.get("tool_used") or "—"
        status = step.get("status", "?")
        duration = step.get("duration_ms", 0)
        result = (step.get("result_summary") or "")[:100]
        error = step.get("error")

        icon = {"completed": "✅", "failed": "❌", "skipped": "⏭️", "pending": "⏳"}.get(status, "❓")
        duration_sec = duration / 1000.0
        line = f"  {icon} Step {i}: {step.get('description', '?')[:50]}"
        line += f"\n      Tool: {tool:<20s} Status: {status:<10s} Time: {duration_sec:.1f}s"

        if result:
            line += f"\n      Result: {result}"
        if error:
            line += f"\n      Error:  {error[:120]}"
        return line

    @staticmethod
    def _step_label(step: dict) -> str:
        desc = step.get("description", "")[:30]
        tool = step.get("tool_used") or "—"
        return f"{desc} ({tool})"

    @staticmethod
    def _step_status_icon(step: dict) -> str:
        status = step.get("status", "")
        return {"completed": "✅", "failed": "❌", "skipped": "⏭️"}.get(status, "❓")
