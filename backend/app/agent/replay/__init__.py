"""Execution Replay — replay, inspect, and diff agent executions.

This package turns ExecutionContext snapshots into a full Agent Flight Recorder:
    - replay:         step-by-step playback of any agent execution
    - diff:           side-by-side comparison of two runs
    - list:           browse all saved executions

Usage:
    python -m benchmark.replay <task_id>
    python -m benchmark.replay --diff <task_a> <task_b>
    python -m benchmark.replay --list
"""

from app.agent.replay.engine import ReplayEngine

__all__ = ["ReplayEngine"]
