"""Benchmark scorer — evaluates agent responses against expected criteria.

Metrics:
    completion (bool):        Agent produced a non-empty, non-error response.
    keyword_coverage (float): Fraction of expected keywords found in response.
    step_count (int):         Number of plan steps used (agent mode).
    duration (float):         Wall-clock time in seconds.
    tool_failures (int):      Number of failed tool calls.

Case classification:
    success (score >= 0.8)    All or most keywords found.
    partial (0.4 <= score < 0.8)  Some keywords found, some missing.
    failure (score < 0.4)     Most keywords missing or empty answer.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any


# ── Classification ────────────────────────────────────────────────────

class FailureCause:
    """Categorised reason why a question result was < 0.4 coverage."""
    NONE = ""                    # Not a failure (success/partial)
    API_ERROR = "API_ERROR"      # LLM API connection / auth errors
    TIMEOUT = "TIMEOUT"          # Request timed out
    TOOL_ERROR = "TOOL_ERROR"    # Tool call failed (search, code, etc.)
    NO_RESULT = "NO_RESULT"      # Agent produced empty/no-result answer
    REASONING_ERROR = "REASONING_ERROR"  # Agent plan/execution logic failed
    UNKNOWN = "UNKNOWN"          # Unclassifiable

    @classmethod
    def classify(cls, answer: str, tool_failures: int, step_count: int) -> str:
        """Heuristic classification based on answer content and execution stats."""
        if not answer:
            return cls.NO_RESULT
        a = answer.lower()
        if tool_failures >= 3:
            return cls.TOOL_ERROR
        if any(kw in a for kw in ["error", "connection", "timeout", "api"]):
            if "timeout" in a or "timed out" in a:
                return cls.TIMEOUT
            return cls.API_ERROR
        if "(no answer)" in a:
            return cls.NO_RESULT
        if step_count == 0 and not a.startswith("知识库"):
            return cls.REASONING_ERROR
        return cls.UNKNOWN


class CaseGrade:
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"

    @classmethod
    def from_score(cls, score: float) -> str:
        if score >= 0.8:
            return cls.SUCCESS
        elif score >= 0.4:
            return cls.PARTIAL
        else:
            return cls.FAILURE


# ── Single question result ────────────────────────────────────────────

@dataclass
class QuestionResult:
    id: str
    category: str
    question: str
    difficulty: str
    answer: str
    duration: float
    step_count: int = 0
    tool_failures: int = 0
    tokens_used: int = 0

    # Failure cause (populated after scoring)
    failure_cause: str = ""

    # Computed
    completion: bool = False
    keyword_coverage: float = 0.0
    keywords_found: list[str] = field(default_factory=list)
    keywords_missed: list[str] = field(default_factory=list)

    # Trace link (populated by runner)
    trace_id: str = ""
    trace_url: str = ""

    def score(self, expected_keywords: list[str]) -> None:
        """Score this single question-answer pair and classify failure cause."""
        self.completion = bool(self.answer and len(self.answer) > 20
                               and not self.answer.startswith("Error"))

        if expected_keywords and self.answer:
            answer_lower = self.answer.lower()
            found: list[str] = []
            missed: list[str] = []
            for kw in expected_keywords:
                if kw.lower() in answer_lower:
                    found.append(kw)
                else:
                    missed.append(kw)
            self.keywords_found = found
            self.keywords_missed = missed
            self.keyword_coverage = len(found) / len(expected_keywords)
        else:
            self.keyword_coverage = 0.0

        # Classify failure cause
        if self.grade == "failure":
            self.failure_cause = FailureCause.classify(self.answer, self.tool_failures, self.step_count)

    @property
    def grade(self) -> str:
        return CaseGrade.from_score(self.keyword_coverage)


# ── Case file (single question, saved to disk) ────────────────────────

@dataclass
class CaseFile:
    """A single question case saved to benchmark/cases/{grade}/.json"""
    question_id: str
    grade: str
    category: str
    question: str
    difficulty: str
    expected_keywords: list[str]
    actual_answer: str
    keyword_coverage: float
    keywords_found: list[str]
    keywords_missed: list[str]
    step_count: int
    tool_failures: int
    duration: float
    trace_id: str
    trace_url: str
    timestamp: str
    failure_cause: str = ""       # FailureCause enum value

    @classmethod
    def from_question_result(
        cls,
        result: QuestionResult,
        expected_keywords: list[str],
    ) -> "CaseFile":
        cause = FailureCause.classify(result.answer, result.tool_failures, result.step_count)
        return cls(
            question_id=result.id,
            grade=result.grade,
            failure_cause=cause if result.grade == "failure" else "",
            category=result.category,
            question=result.question,
            difficulty=result.difficulty,
            expected_keywords=expected_keywords,
            actual_answer=result.answer[:1000],
            keyword_coverage=result.keyword_coverage,
            keywords_found=result.keywords_found,
            keywords_missed=result.keywords_missed,
            step_count=result.step_count,
            tool_failures=result.tool_failures,
            duration=result.duration,
            trace_id=result.trace_id,
            trace_url=result.trace_url,
            timestamp=datetime.now().isoformat(timespec="seconds"),
        )


# ── Case saver ────────────────────────────────────────────────────────

def save_case(result: QuestionResult, expected_keywords: list[str], cases_dir: str = "benchmark/cases") -> str:
    """Save a single question case to benchmark/cases/{grade}/{id}.json.

    Returns the file path saved to.
    """
    case = CaseFile.from_question_result(result, expected_keywords)
    grade_dir = Path(cases_dir) / case.grade
    grade_dir.mkdir(parents=True, exist_ok=True)

    path = grade_dir / f"{case.question_id}.json"
    path.write_text(
        json.dumps(asdict(case), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return str(path)


def load_all_cases(cases_dir: str = "benchmark/cases") -> dict[str, list[dict[str, Any]]]:
    """Load all saved cases grouped by grade."""
    groups: dict[str, list[dict]] = {"success": [], "partial": [], "failure": []}
    for grade in groups:
        grade_path = Path(cases_dir) / grade
        if not grade_path.exists():
            continue
        for f in sorted(grade_path.glob("*.json")):
            data = json.loads(f.read_text(encoding="utf-8"))
            groups[grade].append(data)
    return groups


def cases_summary(cases_dir: str = "benchmark/cases") -> str:
    """Print a summary of all saved cases."""
    groups = load_all_cases(cases_dir)
    total = sum(len(v) for v in groups.values())
    lines = [
        f"评测案例 ({total} 个)",
        f"  ✅ success: {len(groups['success'])}",
        f"  🟡 partial: {len(groups['partial'])}",
        f"  ❌ failure: {len(groups['failure'])}",
    ]
    if groups["failure"]:
        lines.append("")
        lines.append("失败案例:")
        for c in groups["failure"]:
            kw_pct = f"{c['keyword_coverage']:.0%}"
            cause = c.get("failure_cause", "")
            tag = f" [{cause}]" if cause else ""
            lines.append(f"  [{c['question_id']}] {c['question'][:55]}...{tag} 覆盖={kw_pct}")
    return "\n".join(lines)


# ── Aggregate report (keeps existing interface) ───────────────────────

@dataclass
class BenchmarkReport:
    mode: str  # "baseline" | "agent"
    total_questions: int = 0
    completion_rate: float = 0.0
    avg_keyword_coverage: float = 0.0
    avg_duration: float = 0.0
    avg_step_count: float = 0.0
    avg_tool_failures: float = 0.0
    total_tokens: int = 0
    results: list[dict[str, Any]] = field(default_factory=list)

    # Grade distribution
    grade_success: int = 0
    grade_partial: int = 0
    grade_failure: int = 0

    # Failure cause distribution (only for failures)
    failure_causes: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_results(cls, mode: str, results: list[QuestionResult]) -> "BenchmarkReport":
        n = len(results) or 1
        # Aggregate failure causes
        fc: dict[str, int] = {}
        for r in results:
            if r.grade == "failure" and r.failure_cause:
                fc[r.failure_cause] = fc.get(r.failure_cause, 0) + 1
        return cls(
            mode=mode,
            total_questions=len(results),
            completion_rate=sum(1 for r in results if r.completion) / n,
            avg_keyword_coverage=sum(r.keyword_coverage for r in results) / n,
            avg_duration=sum(r.duration for r in results) / n,
            avg_step_count=sum(r.step_count for r in results) / n,
            avg_tool_failures=sum(r.tool_failures for r in results) / n,
            total_tokens=sum(r.tokens_used for r in results),
            results=[asdict(r) for r in results],
            grade_success=sum(1 for r in results if r.grade == "success"),
            grade_partial=sum(1 for r in results if r.grade == "partial"),
            grade_failure=sum(1 for r in results if r.grade == "failure"),
            failure_causes=dict(sorted(fc.items(), key=lambda x: -x[1])),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def summary_text(self) -> str:
        lines = [
            f"Benchmark: {self.total_questions} 个评测问题",
            f"模式: {self.mode}",
            f"──{'─' * 30}",
            f"完成率:            {self.completion_rate:.0%}",
            f"关键词覆盖率:      {self.avg_keyword_coverage:.0%}",
            f"平均耗时:          {self.avg_duration:.2f}s",
            f"平均步骤数:        {self.avg_step_count:.1f}",
            f"平均工具失败数:    {self.avg_tool_failures:.1f}",
            f"总 Token 消耗:     {self.total_tokens}",
            f"",
            f"分类分布:",
            f"  ✅ success: {self.grade_success}",
            f"  🟡 partial: {self.grade_partial}",
            f"  ❌ failure: {self.grade_failure}",
        ]
        if self.failure_causes:
            lines.append("")
            lines.append(f"失败归因 ({sum(self.failure_causes.values())} 题):")
            for cause, count in self.failure_causes.items():
                lines.append(f"  {cause:<25s} {count}")
        return "\n".join(lines)

    def comparison_text(self, other: "BenchmarkReport") -> str:
        """Compare this report against another (e.g. agent vs baseline)."""
        lines = [
            f"{'指标':<20} {'Baseline':<14} {'Agent':<14} {'变化':<10}",
            f"{'─' * 20} {'─' * 14} {'─' * 14} {'─' * 10}",
        ]
        metrics = [
            ("完成率", self.completion_rate, other.completion_rate, "pp", 100),
            ("关键词覆盖率", self.avg_keyword_coverage, other.avg_keyword_coverage, "pp", 100),
            ("平均耗时 (s)", self.avg_duration, other.avg_duration, "x", 1),
        ]
        for name, b_val, a_val, unit, scale in metrics:
            diff = (a_val - b_val) * scale
            sign = "+" if diff > 0 else ""
            lines.append(
                f"{name:<20} {b_val * scale:<8.1f}{'':>6}"
                f" {a_val * scale:<8.1f}{'':>6}"
                f" {sign}{diff:<.1f}{unit if unit != 'pp' else '%':>2}"
            )
        return "\n".join(lines)
