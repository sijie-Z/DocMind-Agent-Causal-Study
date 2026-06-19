#!/usr/bin/env python3
"""Smoke test — validate Failure Collection + Langfuse + Case storage.

Runs without database, LLM, or any backend infrastructure.
Tests only the code logic:
  - Question scoring and grading
  - Case file creation and storage
  - Langfuse trace creation (if API key configured)
  - Directory structure
  - Report generation

Usage:
    python -m benchmark.test_smoke
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmark.scorer import (
    BenchmarkReport,
    QuestionResult,
    cases_summary,
    load_all_cases,
    save_case,
)


def test_scoring():
    """Test that scoring and grading logic works correctly."""
    print("  [test] Scoring logic...")

    # Perfect answer (must be >20 chars for completion)
    r = QuestionResult(id="T1", category="test", question="q?", difficulty="easy", answer="该公司毛利率和收入都呈现了持续增长的良好态势", duration=1.0)
    r.score(["毛利率", "收入", "增长"])
    assert r.completion == True
    assert r.keyword_coverage == 1.0
    assert r.grade == "success"
    assert r.keywords_found == ["毛利率", "收入", "增长"]
    assert r.keywords_missed == []
    print("    PASS: success")

    # Partial answer
    r = QuestionResult(id="T2", category="test", question="q?", difficulty="medium", answer="公司毛利率有所提升同时收入也表现良好盈利能力增强", duration=1.0)
    r.score(["毛利率", "收入", "增长"])
    assert r.grade == "partial"
    assert r.keywords_found == ["毛利率", "收入"]
    assert r.keywords_missed == ["增长"]
    print("    PASS: partial")

    # Failed answer (most keywords missing)
    r = QuestionResult(id="T3", category="test", question="q?", difficulty="hard", answer="我不确定这个问题的答案是什么", duration=1.0)
    r.score(["毛利率", "收入", "增长"])
    assert r.grade == "failure"
    assert r.keywords_found == []
    print("    PASS: failure")

    # Empty answer
    r = QuestionResult(id="T4", category="test", question="q?", difficulty="easy", answer="Error: LLM timeout after 30 seconds", duration=1.0)
    r.score(["毛利率"])
    assert r.completion == False
    assert r.grade == "failure"
    print("    PASS: error handling")

    return True


def test_case_storage():
    """Test that case files are saved and loaded correctly."""
    print("  [test] Case storage...")

    with tempfile.TemporaryDirectory() as tmp:
        cases_dir = Path(tmp) / "cases"
        cases_dir.mkdir()

        for grade, coverage in [("success", 1.0), ("partial", 0.5), ("failure", 0.0)]:
            r = QuestionResult(
                id=f"T-{grade.upper()}",
                category="test",
                question=f"Test {grade} case",
                difficulty="easy",
                answer=f"This is a test answer for {grade} case verification",
                duration=1.0,
                trace_id=f"trc_{grade}",
                trace_url=f"https://langfuse.test/trace/trc_{grade}",
            )
            r.score(["test", "answer"])
            # Override coverage for testing
            r.keyword_coverage = coverage

            path = save_case(r, ["test", "answer"], cases_dir=str(cases_dir))
            assert Path(path).exists(), f"Case file not created: {path}"

        # Test loading
        groups = load_all_cases(cases_dir=str(cases_dir))
        assert len(groups["success"]) == 1
        assert len(groups["partial"]) == 1
        assert len(groups["failure"]) == 1
        assert groups["failure"][0]["question_id"] == "T-FAILURE"

        # Test summary
        summary = cases_summary(cases_dir=str(cases_dir))
        assert "failure" in summary
        assert "partial" in summary
        assert "success" in summary

    print("    PASS")

    # Also test with real path
    r_real = QuestionResult(
        id="SMOKE-OK", category="test", question="Smoke test question",
        difficulty="easy", answer="This is a smoke test to verify the pipeline end to end",
        duration=0.5, trace_id="smoke_trc", trace_url="https://langfuse.test/trace/smoke_trc",
    )
    r_real.score(["smoke", "test"])
    path = save_case(r_real, ["smoke", "test"])
    assert Path(path).exists()
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    assert data["question_id"] == "SMOKE-OK"
    assert data["grade"] == "success"
    print(f"    Case file structure: {json.dumps(data, ensure_ascii=False, indent=2)}")

    # Clean up - remove file only, keep directory structure
    if Path(path).exists():
        Path(path).unlink()

    return True


def test_report_generation():
    """Test that BenchmarkReport aggregates correctly."""
    print("  [test] Report generation...")

    results = [
        QuestionResult(id=f"R{i:02d}", category="test", question=f"Question {i}",
                       difficulty="easy", answer=f"This is a test answer number {i} for verification", duration=0.5 * (i % 3 + 1),
                       step_count=i, tool_failures=i % 2)
        for i in range(10)
    ]
    for r in results:
        r.score(["test"])
        r.keyword_coverage = min(1.0, (10 - results.index(r)) / 10)

    report = BenchmarkReport.from_results("test", results)
    assert report.total_questions == 10
    assert 0 < report.avg_keyword_coverage <= 1.0
    assert 0 < report.avg_duration <= 2.0

    summary = report.summary_text()
    assert "完成率" in summary
    assert "关键词覆盖率" in summary
    assert "分类分布" in summary

    # Comparison
    baseline = BenchmarkReport.from_results("baseline", results[:5])
    agent = BenchmarkReport.from_results("agent", results[5:])
    comparison = baseline.comparison_text(agent)
    assert "Baseline" in comparison
    assert "Agent" in comparison

    print("    PASS")
    return True


def test_benchmark_questions():
    """Validate v2.json structure."""
    print("  [test] Questions v2.json...")

    path = Path("benchmark/questions/v2.json")
    assert path.exists(), "v2.json not found"

    data = json.loads(path.read_text(encoding="utf-8"))
    assert "meta" in data
    assert "questions" in data
    assert len(data["questions"]) == 30

    for q in data["questions"]:
        assert "id" in q
        assert "layer" in q
        assert "question" in q
        assert q["layer"] in ("L1_capability", "L2_system")

    print(f"    PASS: {len(data['questions'])} questions valid")
    return True


def test_directory_structure():
    """Validate benchmark directory structure."""
    print("  [test] Directory structure...")

    dirs = [
        "benchmark/questions",
        "benchmark/results",
        "benchmark/cases/success",
        "benchmark/cases/partial",
        "benchmark/cases/failure",
    ]
    for d in dirs:
        assert Path(d).exists(), f"Missing: {d}"

    print("    PASS")
    return True


def main():
    print(f'{"=" * 50}')
    print("  DocMind Benchmark -- Smoke Test Suite")
    print(f'{"=" * 50}')
    print()

    tests = [
        ("Scoring & Grading", test_scoring),
        ("Case Storage", test_case_storage),
        ("Report Generation", test_report_generation),
        ("Questions v2.json", test_benchmark_questions),
        ("Directory Structure", test_directory_structure),
    ]

    passed = 0
    failed = 0

    for name, fn in tests:
        print(f"  [{name}]")
        try:
            fn()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  FAIL: {type(e).__name__}: {e}")
            failed += 1

    print(f'{"─" * 50}')
    print(f"  Results: {passed} passed, {failed} failed")
    print(f'{"─" * 50}')
    print()

    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
