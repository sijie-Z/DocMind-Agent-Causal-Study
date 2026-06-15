"""Experience Memory — the Agent learns from its failures.

This package implements the core of the Self-Improving Agent:
    - models.py:       Experience data model (what a "lesson" looks like)
    - store.py:        Persistent storage (Redis + local JSON)
    - extractor.py:    Auto-extraction from benchmark failures + runtime errors

Integration points (outside this package):
    - planner.py:      Experiences are injected into the planning prompt
    - loop.py:         enable_experience toggle for A/B testing
    - benchmark/:      Validation via A/B comparison

Usage:
    from app.agent.experience import (
        Experience,
        get_experience_store,
        extract_all_from_benchmark,
    )

    # Batch extract from all current benchmark failures
    count = await extract_all_from_benchmark()

    # Experiences are now in the store, ready for Planner injection.
"""

from app.agent.experience.models import Experience
from app.agent.experience.store import ExperienceStore, get_experience_store, reset_experience_store
from app.agent.experience.extractor import (
    extract_all_from_benchmark,
    extract_from_benchmark_failure,
    extract_from_runtime_error,
    extract_from_runtime_success,
)

__all__ = [
    "Experience",
    "ExperienceStore",
    "get_experience_store",
    "reset_experience_store",
    "extract_all_from_benchmark",
    "extract_from_benchmark_failure",
    "extract_from_runtime_error",
    "extract_from_runtime_success",
]
