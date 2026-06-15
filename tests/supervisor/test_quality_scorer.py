"""
Tests for quality_scorer.py — scoring edge cases.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from quality_scorer import (  # noqa: E402
    QUALITY_DIMENSIONS,
    QUALITY_THRESHOLD,
    score_execution,
    score_taskcard,
)


def _make_taskcard(**overrides):
    """Create a taskcard result with sensible defaults."""
    base = {
        "taskcard_id": "TC-TEST-001",
        "test_references": ["test_example.py"],
        "evidence_paths": ["evidence/log.txt"],
        "changed_files": ["src/module.py"],
        "test_results": {"passed": 5, "failed": 0, "skipped": 0},
        "schema_validated": True,
        "governance_pass": True,
        "governance_fail": False,
        "forbidden_path_violations": [],
        "docs_updated": False,
        "docs_not_needed": True,
        "idempotency_proven": False,
        "performance_regression": False,
        "unhandled_errors": False,
        "integration_verified": True,
        "acceptance_criteria_met": ["AC-1", "AC-2"],
        "acceptance_criteria_failed": [],
        "lint_failures": [],
    }
    base.update(overrides)
    return base


class TestScoreTaskcard:
    def test_all_dimensions_scored(self):
        """Every dimension gets a score between 1-5."""
        tc = _make_taskcard()
        scores = score_taskcard(tc)
        assert len(scores) == len(QUALITY_DIMENSIONS)
        for dim in QUALITY_DIMENSIONS:
            assert dim in scores
            assert 1 <= scores[dim] <= 5

    def test_all_green_taskcard(self):
        """Well-evidenced taskcard scores >= 4 on all dimensions."""
        tc = _make_taskcard()
        scores = score_taskcard(tc)
        for dim, val in scores.items():
            assert val >= QUALITY_THRESHOLD, f"{dim} scored {val}, expected >= {QUALITY_THRESHOLD}"

    def test_failing_taskcard_no_tests(self):
        """Taskcard with no tests scores low on test_coverage."""
        tc = _make_taskcard(
            test_references=[],
            test_results={"passed": 0, "failed": 0, "skipped": 0},
        )
        scores = score_taskcard(tc)
        assert scores["test_coverage"] < QUALITY_THRESHOLD

    def test_failing_taskcard_test_failures(self):
        """Taskcard with test failures scores low on correctness."""
        tc = _make_taskcard(
            test_results={"passed": 3, "failed": 2, "skipped": 0},
        )
        scores = score_taskcard(tc)
        assert scores["correctness"] < 5
        assert scores["regression_safety"] < 5

    def test_forbidden_path_violation(self):
        """Forbidden path violation -> path_discipline = 1."""
        tc = _make_taskcard(
            forbidden_path_violations=["registry/format-registry.yaml"],
        )
        scores = score_taskcard(tc)
        assert scores["path_discipline"] == 1

    def test_no_evidence_paths(self):
        """No evidence paths -> low evidence scores."""
        tc = _make_taskcard(evidence_paths=[], changed_files=[])
        scores = score_taskcard(tc)
        assert scores["evidence_completeness"] < QUALITY_THRESHOLD

    def test_lint_failures(self):
        """Lint failures -> low code_quality."""
        tc = _make_taskcard(lint_failures=["E501", "W503"])
        scores = score_taskcard(tc)
        assert scores["code_quality"] < QUALITY_THRESHOLD

    def test_acceptance_criteria_failed(self):
        """Failed acceptance criteria -> low acceptance_criteria_met."""
        tc = _make_taskcard(
            acceptance_criteria_met=["AC-1"],
            acceptance_criteria_failed=["AC-2"],
        )
        scores = score_taskcard(tc)
        assert scores["acceptance_criteria_met"] < QUALITY_THRESHOLD


class TestScoreExecution:
    def test_all_green_execution(self):
        """All-green execution: all dimensions >= 4, all_green=True."""
        result = score_execution([_make_taskcard()])
        assert result["all_green"] is True
        assert result["overall_verdict"] == "EXECUTION_COMPLETE_VERIFIED"
        for dim, val in result["overall_scores"].items():
            assert val >= QUALITY_THRESHOLD, f"{dim} = {val}"

    def test_not_green_execution(self):
        """Execution with failing taskcard: all_green=False."""
        result = score_execution([
            _make_taskcard(
                taskcard_id="TC-FAIL",
                test_references=[],
                test_results={"passed": 0, "failed": 0, "skipped": 0},
                evidence_paths=[],
                changed_files=[],
            ),
        ])
        assert result["all_green"] is False
        assert result["overall_verdict"] == "EXECUTION_REROUTED_REWORK_REQUIRED"
        assert len(result["reroute_log"]) > 0

    def test_mixed_execution(self):
        """Mix of passing and failing taskcards."""
        result = score_execution([
            _make_taskcard(taskcard_id="TC-GOOD"),
            _make_taskcard(
                taskcard_id="TC-BAD",
                test_references=[],
                test_results={"passed": 0, "failed": 0, "skipped": 0},
                evidence_paths=[],
                changed_files=[],
            ),
        ])
        assert result["all_green"] is False
        rerouted_ids = [r["taskcard_id"] for r in result["reroute_log"]]
        assert "TC-BAD" in rerouted_ids

    def test_empty_taskcard_list(self):
        """Empty taskcard list: all_green=False, scores default to 1."""
        result = score_execution([])
        assert result["all_green"] is False
        assert result["execution_results"] == []

    def test_reroute_log_structure(self):
        """Reroute log entries have required fields."""
        result = score_execution([
            _make_taskcard(
                taskcard_id="TC-REROUTE",
                forbidden_path_violations=["bad/path"],
            ),
        ])
        for entry in result["reroute_log"]:
            assert "taskcard_id" in entry
            assert "reason" in entry
            assert "failing_dimensions" in entry
            assert "rework_owner" in entry
            assert entry["reworked"] is False
            assert entry["rescored"] is False

    def test_15_dimensions_required(self):
        """All 15 dimensions present in overall_scores."""
        result = score_execution([_make_taskcard()])
        assert len(result["overall_scores"]) == 15
        for dim in QUALITY_DIMENSIONS:
            assert dim in result["overall_scores"]
