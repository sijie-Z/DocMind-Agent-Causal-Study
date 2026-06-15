"""Pattern Mining — discovers recurring tool-use patterns from execution history.

Pipeline:
    Execution Replay (benchmark/replay/*.json)
        ↓
    PatternMiner (miner.py) — extract tool sequences, compute frequency
        ↓
    PatternAnalyzer (analyzer.py) — filter, score, recommend Skills
        ↓
    SuggestedSkill → SkillManager (skills.py) — register new skills

Usage:
    # Analyze all replays and print report
    python -m app.agent.mining.analyzer

    # Analyze and persist results
    python -m app.agent.mining.analyzer --save
"""

from app.agent.mining.patterns import ToolSequence, PatternStats, SuggestedSkill
from app.agent.mining.miner import PatternMiner
from app.agent.mining.analyzer import PatternAnalyzer

__all__ = [
    "ToolSequence",
    "PatternStats",
    "SuggestedSkill",
    "PatternMiner",
    "PatternAnalyzer",
]
