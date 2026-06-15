"""
Tests for the grade-to-quality adapter bridge.
TC-BRIDGE-001: Verify grade_to_quality_adapter converts item_grades correctly
and quality_scorer accepts the adapted output.
"""
import json
import sys
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))
sys.path.insert(0, str(_repo_root / "tools" / "supervisor"))

from grade_to_quality_adapter import (
    PASSING_GRADES,
    FAILING_GRADES,
    adapt_item_grades,
    is_item_grades_format,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_grade(item_id="T1", grade="ACCEPTED_VERIFIED", tests=None, evidence=None,
                ac_met=None, ac_failed=None):
    """Create a single item-grade dict matching grade_declared_work output."""
    return {
        "item_id": item_id,
        "item_title": f"Test item {item_id}",
        "declared_status": "completed",
        "supervisor_grade": grade,
        "evidence_found": True,
        "evidence_paths": evidence or ["path/to/evidence.txt"],
        "tests_supporting": tests or ["tests/test_sample.py::test_one"],
        "tests_missing": [],
        "acceptance_criteria_met": ac_met or ["AC1"],
        "acceptance_criteria_failed": ac_failed or [],
        "required_rework": "",
        "can_autonomously_repair": False,
        "next_prompt_instruction": "",
    }


# ---------------------------------------------------------------------------
# is_item_grades_format
# ---------------------------------------------------------------------------

def test_detects_item_grades_format():
    data = [_make_grade()]
    assert is_item_grades_format(data) is True


def test_rejects_empty():
    assert is_item_grades_format([]) is False


def test_rejects_taskcard_format():
    data = [{"taskcard_id": "TC1", "test_results": {"passed": 1}}]
    assert is_item_grades_format(data) is False


# ---------------------------------------------------------------------------
# adapt_item_grades — basic conversion
# ---------------------------------------------------------------------------

def test_adapter_converts_single_grade():
    grades = [_make_grade()]
    result = adapt_item_grades(grades)
    assert len(result) == 1
    r = result[0]
    assert r["taskcard_id"] == "T1"
    assert r["test_references"] == ["tests/test_sample.py::test_one"]
    assert r["evidence_paths"] == ["path/to/evidence.txt"]
    assert r["governance_pass"] is True
    assert r["governance_fail"] is False
    assert r["test_results"]["passed"] >= 1
    assert r["test_results"]["failed"] == 0
    assert r["schema_validated"] is True  # ACCEPTED_VERIFIED → schema_validated
    assert r["integration_verified"] is True


def test_adapter_converts_multiple_grades():
    grades = [
        _make_grade("T1", "ACCEPTED_VERIFIED"),
        _make_grade("T2", "REWORK_REQUIRED"),
        _make_grade("T3", "ACCEPTED_WITH_WARNINGS"),
    ]
    result = adapt_item_grades(grades)
    assert len(result) == 3
    assert result[0]["governance_pass"] is True
    assert result[1]["governance_fail"] is True
    assert result[2]["governance_pass"] is True


# ---------------------------------------------------------------------------
# adapt_item_grades — all grade values
# ---------------------------------------------------------------------------

ALL_GRADES = list(PASSING_GRADES) + list(FAILING_GRADES) + [
    "BLOCKED_EXTERNAL_GATE", "NOT_ATTEMPTED", "NOT_IN_SCOPE",
    "INSUFFICIENT_EVIDENCE", "DEFERRED_WITH_REASON",
]


@pytest.mark.parametrize("grade", ALL_GRADES)
def test_adapter_handles_grade(grade):
    """Adapter must not crash on any known grade value."""
    grades = [_make_grade("G1", grade)]
    result = adapt_item_grades(grades)
    assert len(result) == 1
    r = result[0]
    assert r["taskcard_id"] == "G1"
    assert "_original_supervisor_grade" in r
    assert r["_original_supervisor_grade"] == grade

    if grade in PASSING_GRADES:
        assert r["governance_pass"] is True
        assert r["test_results"]["passed"] >= 1
    elif grade in FAILING_GRADES:
        assert r["governance_fail"] is True
        assert r["test_results"]["failed"] >= 1


# ---------------------------------------------------------------------------
# adapt_item_grades — edge cases
# ---------------------------------------------------------------------------

def test_adapter_empty_input():
    assert adapt_item_grades([]) == []


def test_adapter_preserves_acceptance_criteria():
    grades = [_make_grade(ac_met=["AC1", "AC2"], ac_failed=["AC3"])]
    result = adapt_item_grades(grades)
    assert result[0]["acceptance_criteria_met"] == ["AC1", "AC2"]
    assert result[0]["acceptance_criteria_failed"] == ["AC3"]


def test_adapter_missing_fields_use_defaults():
    """Adapter handles grades missing optional fields gracefully."""
    minimal = {"item_id": "MIN", "supervisor_grade": "ACCEPTED"}
    result = adapt_item_grades([minimal])
    assert len(result) == 1
    r = result[0]
    assert r["taskcard_id"] == "MIN"
    assert r["test_references"] == []
    assert r["evidence_paths"] == []


# ---------------------------------------------------------------------------
# quality_scorer integration
# ---------------------------------------------------------------------------

def test_quality_scorer_accepts_adapted_output():
    """score_execution works with adapter output and returns 15 dimensions."""
    from quality_scorer import score_execution

    grades = [
        _make_grade("T1", "ACCEPTED_VERIFIED", tests=["t1", "t2"], evidence=["e1.txt"]),
        _make_grade("T2", "ACCEPTED_WITH_WARNINGS", tests=["t3"], evidence=["e2.txt"]),
    ]
    adapted = adapt_item_grades(grades)
    result = score_execution(adapted)

    assert "overall_scores" in result
    assert "overall_verdict" in result
    assert "execution_results" in result

    # Check 15 quality dimensions present
    overall = result["overall_scores"]
    expected_dims = [
        "correctness", "test_coverage", "evidence_completeness",
        "code_quality", "schema_compliance", "governance_compliance",
        "path_discipline", "documentation", "idempotency",
        "regression_safety", "performance", "error_handling",
        "integration_consistency", "evidence_traceability",
        "acceptance_criteria_met",
    ]
    for dim in expected_dims:
        assert dim in overall, f"Missing dimension: {dim}"
        assert 1 <= overall[dim] <= 5, f"Dimension {dim} out of range: {overall[dim]}"

    # Each execution result should have quality_scores
    for er in result["execution_results"]:
        assert "quality_scores" in er
        assert "taskcard_id" in er


def test_quality_scorer_reroutes_failing_grades():
    """Failing grades should produce below-threshold scores and reroute entries."""
    from quality_scorer import score_execution

    grades = [_make_grade("F1", "REJECTED", tests=[], evidence=[])]
    adapted = adapt_item_grades(grades)
    result = score_execution(adapted)

    # Rejected item should have low scores
    er = result["execution_results"][0]
    assert er["quality_scores"]["governance_compliance"] < 4
    assert er.get("rerouted") or not result.get("all_green", True)
