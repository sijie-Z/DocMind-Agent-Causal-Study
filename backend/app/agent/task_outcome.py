"""TaskOutcome — the single source of truth for whether a task succeeded.

This is NOT a metric.  This is NOT a trace.
This is the unified model for "what happened to this task".
Every agent run produces exactly one TaskOutcome.

Core principle:
    Users pay for completed tasks, not for clever components.
    TaskOutcome is the objective function we optimize.

Usage:
    outcome = TaskOutcome.from_context(ctx)
    outcome.record_component("planner", enabled=True)
    outcome.mark_success()
    await outcome.save()

    # Later, aggregate across outcomes:
    success_rate = await TaskOutcome.aggregate(
        filters={"planner_enabled": True},
        window=timedelta(days=7),
    )
"""

from __future__ import annotations

import json
import logging
import time as _time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Final status of a task execution."""
    SUCCESS = "success"                # Task completed with satisfactory result
    PARTIAL = "partial"                # Partially completed (some steps skipped)
    FAILURE = "failure"                # Completed but unsatisfactory or error
    REJECTED = "rejected"              # Rejected by guardrail / permission / quality gate
    INTERRUPTED = "interrupted"        # Stopped by user or system
    TIMEOUT = "timeout"                # Exceeded max_turns or wall-clock limit
    UNKNOWN = "unknown"                # Not yet set (initial state)


class FailureStage(str, Enum):
    """Which stage the task failed at."""
    NONE = "none"                      # Did not fail
    INPUT = "input"                    # Input guardrail / validation
    PLANNING = "planning"              # Planner failed to generate a valid plan
    EXECUTION = "execution"            # Executor failed (tool errors, step failures)
    REFLECTION = "reflection"          # Reflector failed or unrecoverable
    REVIEW = "review"                  # Reviewer found fatal issues
    QUALITY_GATE = "quality_gate"      # Quality gate rejected
    PERMISSION = "permission"          # Permission denied
    TIMEOUT = "timeout"               # System timeout
    UNKNOWN = "unknown"


@dataclass
class PolicyViolation:
    """A specific guarantee that was violated during execution."""
    policy_name: str          # "permission_check", "citation_required", "human_approval"
    detail: str               # Human-readable description
    severity: str             # "low" | "medium" | "high" | "fatal"


@dataclass
class ComponentRecord:
    """Which agent components ran and their individual outcomes."""
    name: str                 # "planner", "executor", "reflector", "reviewer", "quality_gate"
    enabled: bool             # Was this component enabled for this task?
    invoked: bool             # Was it actually invoked?
    duration_ms: float = 0.0
    tokens_used: int = 0
    result: str = ""          # "pass" | "fail" | "retry" | "skip"


@dataclass
class TaskOutcome:
    """The single outcome record for one agent execution.

    One TaskOutcome per call to PERAgentLoop.run().
    All components (Planner, Executor, Reflector, Reviewer) write into this.

    This replaces scattered per-component logging with a unified record.
    """

    # ── Identity ──
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    trace_id: str = ""                 # Langfuse / OTEL trace (set after initialisation)
    session_id: str = ""               # Conversation session

    # ── Input ──
    query: str = ""
    query_intent: str = ""             # "exploration" | "construction" | "execution" | "unknown"
    query_length_chars: int = 0
    organization_id: int = 0
    user_id: int = 0

    # ── Outcome ──
    status: TaskStatus = TaskStatus.UNKNOWN
    failure_stage: FailureStage = FailureStage.UNKNOWN
    failure_reason: str = ""

    # ── Which components were enabled for this task ──
    planner_enabled: bool = False
    reflector_enabled: bool = False
    reviewer_enabled: bool = False
    quality_gate_enabled: bool = False
    memory_enabled: bool = False

    # ── Per-component outcomes ──
    components: list[ComponentRecord] = field(default_factory=list)
    policies_violated: list[PolicyViolation] = field(default_factory=list)

    # ── Cost ──
    total_tokens: int = 0
    total_duration_ms: float = 0.0
    tool_call_count: int = 0
    tool_error_count: int = 0
    step_count: int = 0
    retry_count: int = 0

    # ── Output ──
    output_length_chars: int = 0

    # ── Timing ──
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    # ── Tags (arbitrary, for filtering/aggregation) ──
    tags: dict[str, str] = field(default_factory=dict)

    # ──────────────────────────────────────────────────────────────
    # Factories
    # ──────────────────────────────────────────────────────────────

    @classmethod
    def from_context(cls, ctx: Any) -> "TaskOutcome":
        """Build from an existing ExecutionContext."""
        return cls(
            task_id=ctx.task_id if hasattr(ctx, "task_id") else uuid.uuid4().hex[:12],
            query=ctx.query if hasattr(ctx, "query") else "",
            total_duration_ms=ctx.duration_ms if hasattr(ctx, "duration_ms") else 0.0,
            total_tokens=ctx.total_tokens if hasattr(ctx, "total_tokens") else 0,
            step_count=len(ctx.completed_steps) if hasattr(ctx, "completed_steps") else 0,
            query_length_chars=len(ctx.query) if hasattr(ctx, "query") else 0,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskOutcome":
        """Restore from a saved dict."""
        return cls(
            task_id=data.get("task_id", ""),
            trace_id=data.get("trace_id", ""),
            session_id=data.get("session_id", ""),
            query=data.get("query", ""),
            query_intent=data.get("query_intent", ""),
            status=TaskStatus(data.get("status", "unknown")),
            failure_stage=FailureStage(data.get("failure_stage", "unknown")),
            failure_reason=data.get("failure_reason", ""),
            planner_enabled=data.get("planner_enabled", False),
            reflector_enabled=data.get("reflector_enabled", False),
            reviewer_enabled=data.get("reviewer_enabled", False),
            quality_gate_enabled=data.get("quality_gate_enabled", False),
            memory_enabled=data.get("memory_enabled", False),
            total_tokens=data.get("total_tokens", 0),
            total_duration_ms=data.get("total_duration_ms", 0.0),
            tool_call_count=data.get("tool_call_count", 0),
            tool_error_count=data.get("tool_error_count", 0),
            step_count=data.get("step_count", 0),
            retry_count=data.get("retry_count", 0),
            output_length_chars=data.get("output_length_chars", 0),
            components=[ComponentRecord(**c) for c in data.get("components", [])],
            policies_violated=[PolicyViolation(**p) for p in data.get("policies_violated", [])],
            tags=data.get("tags", {}),
        )

    # ──────────────────────────────────────────────────────────────
    # Recording
    # ──────────────────────────────────────────────────────────────

    def record_component(self, name: str, enabled: bool, invoked: bool = False,
                         duration_ms: float = 0.0, tokens_used: int = 0,
                         result: str = "") -> None:
        """Record that a component ran."""
        self.components.append(ComponentRecord(
            name=name, enabled=enabled, invoked=invoked,
            duration_ms=duration_ms, tokens_used=tokens_used, result=result,
        ))
        # Also set the per-component flag
        if name == "planner":
            self.planner_enabled = enabled
        elif name == "reflector":
            self.reflector_enabled = enabled
        elif name == "reviewer":
            self.reviewer_enabled = enabled
        elif name == "quality_gate":
            self.quality_gate_enabled = enabled
        elif name == "memory":
            self.memory_enabled = enabled

    def record_policy_violation(self, policy_name: str, detail: str,
                                severity: str = "medium") -> None:
        self.policies_violated.append(PolicyViolation(
            policy_name=policy_name, detail=detail, severity=severity,
        ))

    def mark_success(self) -> None:
        self.status = TaskStatus.SUCCESS
        self.completed_at = datetime.now(timezone.utc)

    def mark_failure(self, stage: FailureStage, reason: str,
                     status: TaskStatus = TaskStatus.FAILURE) -> None:
        self.status = status
        self.failure_stage = stage
        self.failure_reason = reason
        self.completed_at = datetime.now(timezone.utc)

    def finalise(self) -> None:
        """Call once at the end of execution to finalise timing."""
        self.completed_at = datetime.now(timezone.utc)

    @property
    def is_complete(self) -> bool:
        return self.status != TaskStatus.UNKNOWN

    @property
    def is_success(self) -> bool:
        return self.status == TaskStatus.SUCCESS

    # ──────────────────────────────────────────────────────────────
    # Serialisation
    # ──────────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "query": self.query[:200],
            "query_intent": self.query_intent,
            "organization_id": self.organization_id,
            "user_id": self.user_id,
            "status": self.status.value,
            "failure_stage": self.failure_stage.value if self.failure_stage else "",
            "failure_reason": self.failure_reason[:500],
            "planner_enabled": self.planner_enabled,
            "reflector_enabled": self.reflector_enabled,
            "reviewer_enabled": self.reviewer_enabled,
            "quality_gate_enabled": self.quality_gate_enabled,
            "memory_enabled": self.memory_enabled,
            "components": [
                {"name": c.name, "enabled": c.enabled, "invoked": c.invoked,
                 "duration_ms": round(c.duration_ms, 1), "tokens_used": c.tokens_used,
                 "result": c.result}
                for c in self.components
            ],
            "policies_violated": [
                {"policy_name": p.policy_name, "detail": p.detail[:200],
                 "severity": p.severity}
                for p in self.policies_violated
            ],
            "total_tokens": self.total_tokens,
            "total_duration_ms": round(self.total_duration_ms, 1),
            "tool_call_count": self.tool_call_count,
            "tool_error_count": self.tool_error_count,
            "step_count": self.step_count,
            "retry_count": self.retry_count,
            "output_length_chars": self.output_length_chars,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else "",
            "tags": self.tags,
        }

    def to_metrics_labels(self) -> dict[str, str]:
        """Return a label set suitable for Prometheus counters.

        Low cardinality by design:
            - status (5 values)
            - failure_stage (10 values)
            - planner_enabled (2 values)
            - reflector_enabled (2 values)
            - reviewer_enabled (2 values)
        """
        return {
            "status": self.status.value,
            "failure_stage": self.failure_stage.value if self.failure_stage else "none",
            "planner": "1" if self.planner_enabled else "0",
            "reflector": "1" if self.reflector_enabled else "0",
            "reviewer": "1" if self.reviewer_enabled else "0",
        }

    # ──────────────────────────────────────────────────────────────
    # Persistence
    # ──────────────────────────────────────────────────────────────

    async def save(self) -> bool:
        """Persist to Redis under agent:outcome:{task_id} for 7 days."""
        try:
            from app.core.redis import redis_client
            if redis_client:
                key = f"agent:outcome:{self.task_id}"
                await redis_client.setex(key, 86400 * 7,
                                         json.dumps(self.to_dict(), ensure_ascii=False))
                return True
        except Exception as e:
            logger.debug("Failed to save TaskOutcome to Redis: %s", e)
        return False

    @classmethod
    async def load(cls, task_id: str) -> "TaskOutcome | None":
        """Load a saved TaskOutcome from Redis."""
        try:
            from app.core.redis import redis_client
            if redis_client:
                raw = await redis_client.get(f"agent:outcome:{task_id}")
                if raw:
                    return cls.from_dict(json.loads(raw))
        except Exception:
            pass
        return None

    @classmethod
    def from_config(cls, task_id: str, query: str,
                    planner_enabled: bool = False,
                    reflector_enabled: bool = False,
                    reviewer_enabled: bool = False,
                    quality_gate_enabled: bool = False,
                    memory_enabled: bool = False,
                    organization_id: int = 0,
                    user_id: int = 0) -> "TaskOutcome":
        """Build from a task's config flags (used by TaskOutcomeBuilder)."""
        return cls(
            task_id=task_id,
            query=query,
            query_length_chars=len(query),
            planner_enabled=planner_enabled,
            reflector_enabled=reflector_enabled,
            reviewer_enabled=reviewer_enabled,
            quality_gate_enabled=quality_gate_enabled,
            memory_enabled=memory_enabled,
            organization_id=organization_id,
            user_id=user_id,
        )

    @classmethod
    async def aggregate(cls, filters: dict[str, Any] | None = None,
                        window_days: int = 7) -> dict[str, Any]:
        """Aggregate outcomes across tasks.

        NOTE: In production this would query ClickHouse or PostgreSQL.
        For now, iterates Redis keys with the agent:outcome: prefix.
        This is O(N) and should only be used for dashboards / ad-hoc analysis.

        Returns:
            dict with success_rate, total, per-stage breakdown, etc.
        """
        try:
            from app.core.redis import redis_client
            if not redis_client:
                return {"error": "Redis not available"}

            keys = await redis_client.keys("agent:outcome:*")
            outcomes: list[TaskOutcome] = []
            for key in keys[-1000:]:  # limit to last 1000
                raw = await redis_client.get(key)
                if raw:
                    outcome = cls.from_dict(json.loads(raw))
                    # Apply filters
                    if filters:
                        match = True
                        for k, v in filters.items():
                            if getattr(outcome, k, None) != v:
                                match = False
                                break
                        if match:
                            outcomes.append(outcome)
                    else:
                        outcomes.append(outcome)

            total = len(outcomes)
            if total == 0:
                return {"total": 0, "success_rate": 0.0}

            successes = sum(1 for o in outcomes if o.is_success)
            stage_breakdown: dict[str, int] = {}
            for o in outcomes:
                if o.failure_stage:
                    stage = o.failure_stage.value
                    stage_breakdown[stage] = stage_breakdown.get(stage, 0) + 1

            return {
                "total": total,
                "success_rate": round(successes / total, 4),
                "by_stage": stage_breakdown,
                "avg_duration_ms": round(
                    sum(o.total_duration_ms for o in outcomes) / total, 1),
                "avg_tokens": round(
                    sum(o.total_tokens for o in outcomes) / total, 1),
            }
        except Exception as e:
            logger.warning("TaskOutcome.aggregate failed: %s", e)
            return {"error": str(e)}


# ────────────────────────────────────────────────────────────────────────────
# Builder — lifecycle wrapper that lives inside PERAgentLoop.run()
# ────────────────────────────────────────────────────────────────────────────


class TaskOutcomeBuilder:
    """Lifecycle builder for TaskOutcome.

    Created at the start of PERAgentLoop.run(), updated throughout
    execution, and persisted in a try/finally block.

    This ensures:
    - Every task produces exactly one TaskOutcome (even on crash/interrupt)
    - enabled vs invoked are tracked separately (for A/B experiment analysis)
    - failure_stage is always set when a task fails (the single source of truth)

    Usage in loop.py:

        builder = TaskOutcomeBuilder(task_id=ctx.task_id, query=query, config=self.config)
        builder.current_stage = FailureStage.PLANNING
        ...
        builder.mark_planning_completed(step_count=len(plan.steps))
        builder.current_stage = FailureStage.EXECUTION
        ...
        builder.finalise(output=final_output, total_tokens=ctx.total_tokens)
        await builder.persist()
    """

    def __init__(self, task_id: str, query: str, config: Any, ctx: Any):
        # Extract config flags
        planner = getattr(config, "enable_planning", False)
        reflector = getattr(config, "enable_reflection", False)
        tools = getattr(config, "enable_tools", False)
        memory = getattr(config, "enable_memory", False)

        self.outcome = TaskOutcome.from_config(
            task_id=task_id,
            query=query,
            planner_enabled=planner,
            reflector_enabled=reflector,
            reviewer_enabled=reflector,   # reviewer is gated by enable_reflection
            quality_gate_enabled=tools,
            memory_enabled=memory,
            organization_id=getattr(ctx, "organization_id", 0),
            user_id=getattr(ctx, "user_id", 0),
        )
        self.current_stage: FailureStage = FailureStage.NONE
        self._phase_timers: dict[str, float] = {}
        self._start_wall = _time.perf_counter()

    # ── internal helpers ──

    def _start_timer(self, key: str) -> None:
        self._phase_timers[key] = _time.perf_counter()

    def _pop_timer(self, key: str) -> float:
        start = self._phase_timers.pop(key, None)
        if start is None:
            return 0.0
        return (_time.perf_counter() - start) * 1000

    # ── Phase 1: Planning ──

    def mark_planning_started(self) -> None:
        """Call before planner.plan()."""
        self.current_stage = FailureStage.PLANNING
        self._start_timer("planner")

    def mark_planning_completed(self, step_count: int, result: str = "pass") -> None:
        """Call after Planner yields plan_complete. result: pass | fail | skip."""
        self.outcome.record_component(
            name="planner",
            enabled=self.outcome.planner_enabled,
            invoked=True,
            duration_ms=self._pop_timer("planner"),
            result=result,
        )
        if result == "pass":
            self.outcome.step_count = step_count
        if result == "fail":
            self.outcome.mark_failure(FailureStage.PLANNING,
                                      "Planner failed to generate plan")

    def mark_planning_skipped(self) -> None:
        """Call when planning is disabled (config or direct-execution mode)."""
        self.outcome.record_component(
            name="planner",
            enabled=self.outcome.planner_enabled,
            invoked=False,
            result="skip",
        )

    # ── Phase 2: Execution (tool-call tracking) ──

    def record_tool_call(self, tool_name: str, success: bool) -> None:
        """Call once per tool invocation. Increments aggregated counters."""
        self.outcome.tool_call_count += 1
        if not success:
            self.outcome.tool_error_count += 1

    def record_retry(self) -> None:
        """Call on automatic retry."""
        self.outcome.retry_count += 1

    # ── Phase 2b: Quality Gate ──

    def mark_quality_gate(self, passed: bool, fatal_count: int = 0,
                          issues_total: int = 0) -> None:
        """Call after quality_gate_check()."""
        self.outcome.record_component(
            name="quality_gate",
            enabled=self.outcome.quality_gate_enabled,
            invoked=True,
            result="pass" if passed else "fail",
        )
        if not passed and fatal_count > 0:
            self.outcome.mark_failure(
                FailureStage.QUALITY_GATE,
                f"{fatal_count} fatal / {issues_total} total issues",
            )

    # ── Phase 3: Reflection ──

    def mark_reflector(self, decision: str, invoked: bool = True) -> None:
        """Call with the reflector's decision: pass | retry | replan."""
        self.outcome.record_component(
            name="reflector",
            enabled=self.outcome.reflector_enabled,
            invoked=invoked,
            result=decision,
        )

    # ── Phase 3b: Adversarial Review ──

    def mark_reviewer(self, issues_found: int, high_severity: int = 0) -> None:
        """Call after reviewer.review()."""
        result = "pass" if issues_found == 0 else "fail"
        self.outcome.record_component(
            name="reviewer",
            enabled=self.outcome.reviewer_enabled,
            invoked=True,
            result=result,
        )

    # ── Finalisation ──

    def mark_failure(self, stage: FailureStage, reason: str,
                     status: TaskStatus = TaskStatus.FAILURE) -> None:
        """Mark the task as failed at a specific stage."""
        self.outcome.mark_failure(stage, reason, status)

    def mark_success(self) -> None:
        """Mark the task as successful."""
        self.outcome.mark_success()
        # Also clear any stale failure stage
        if self.outcome.failure_stage != FailureStage.NONE:
            self.outcome.failure_stage = FailureStage.NONE

    def finalise(self, output: str = "", total_tokens: int = 0) -> None:
        """Set final cost/output metrics. Call before persist()."""
        self.outcome.total_duration_ms = (_time.perf_counter() - self._start_wall) * 1000
        self.outcome.total_tokens = total_tokens
        self.outcome.output_length_chars = len(output)
        self.outcome.finalise()

    async def persist(self) -> bool:
        """Save the outcome to Redis. Safe to call multiple times."""
        return await self.outcome.save()

    def to_dict(self) -> dict[str, Any]:
        """Current snapshot of the outcome (useful for debug logging)."""
        return self.outcome.to_dict()
