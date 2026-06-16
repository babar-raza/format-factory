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
    """Passing grades: ac_met gets synthetic entries, ac_failed cleared.
    Failing grades: both preserved as-is."""
    # Passing grade: ac_failed cleared, ac_met gets synthetics
    grades_pass = [_make_grade(ac_met=["AC1", "AC2"], ac_failed=["AC3"])]
    result_pass = adapt_item_grades(grades_pass)
    ac_met = result_pass[0]["acceptance_criteria_met"]
    assert "AC1" in ac_met
    assert "AC2" in ac_met
    assert "AC_GRADE_PASS" in ac_met  # synthetic entry added
    assert result_pass[0]["acceptance_criteria_failed"] == []  # cleared for passing

    # Failing grade: both preserved as-is
    grades_fail = [_make_grade(grade="REJECTED", ac_met=["AC1"], ac_failed=["AC3"])]
    result_fail = adapt_item_grades(grades_fail)
    assert result_fail[0]["acceptance_criteria_met"] == ["AC1"]
    assert result_fail[0]["acceptance_criteria_failed"] == ["AC3"]


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


# ---------------------------------------------------------------------------
# TC-ACSCORE-001: all_green chain test
# ---------------------------------------------------------------------------

def test_all_accepted_produces_all_green():
    """All-ACCEPTED grades through adapter+scorer must produce all_green=true.

    This validates TC-ACSCORE-001: the AC dimension fix ensures passing grades
    score >= 4 on acceptance_criteria_met, making all_green reachable.
    """
    from quality_scorer import score_execution

    grades = [
        _make_grade("A1", "ACCEPTED_VERIFIED", tests=["t1", "t2"], evidence=["e1"]),
        _make_grade("A2", "ACCEPTED", tests=["t3"], evidence=["e2"]),
        _make_grade("A3", "ACCEPTED_WITH_WARNINGS", tests=["t4"], evidence=["e3"]),
    ]
    adapted = adapt_item_grades(grades)
    result = score_execution(adapted)

    # AC dimension must be >= 4 for all passing items
    for er in result["execution_results"]:
        ac_score = er["quality_scores"]["acceptance_criteria_met"]
        assert ac_score >= 4, (
            f"TC {er['taskcard_id']}: acceptance_criteria_met={ac_score}, "
            f"expected >= 4 for passing grade"
        )

    assert result["all_green"] is True, (
        f"Expected all_green=true for all-ACCEPTED grades. "
        f"Overall scores: {result.get('overall_scores')}. "
        f"Reroute log: {result.get('reroute_log')}"
    )


def test_accepted_with_pattern_diagnostics_still_green():
    """ACCEPTED grade with non-empty ac_failed (pattern diagnostics) must still score >= 4.

    This validates TC-ACSCORE-002: the adapter treats passing grades as authoritative,
    clearing ac_failed pattern diagnostics so the scorer doesn't penalize them.
    """
    from quality_scorer import score_execution

    grades = [_make_grade(
        "P1", "ACCEPTED_WITH_WARNINGS",
        tests=["t1", "t2"], evidence=["e1"],
        ac_met=["Evidence found", "No missing paths"],
        ac_failed=["Acceptance criteria pattern not found: gap closure tests pass"],
    )]
    adapted = adapt_item_grades(grades)

    # Adapter should clear ac_failed for passing grade
    assert adapted[0]["acceptance_criteria_failed"] == []
    assert "AC_GRADE_PASS" in adapted[0]["acceptance_criteria_met"]

    result = score_execution(adapted)
    ac_score = result["execution_results"][0]["quality_scores"]["acceptance_criteria_met"]
    assert ac_score >= 4, (
        f"acceptance_criteria_met={ac_score}, expected >= 4 for passing grade with diagnostics"
    )
    assert result["all_green"] is True


def test_mixed_passing_grades_with_diagnostics():
    """Mix of passing grades all with non-empty ac_failed diagnostics -> all_green=true."""
    from quality_scorer import score_execution

    grades = [
        _make_grade("M1", "ACCEPTED_VERIFIED", tests=["t1"], evidence=["e1"],
                    ac_met=["Evidence found"], ac_failed=["Pattern not found: X"]),
        _make_grade("M2", "ACCEPTED", tests=["t2"], evidence=["e2"],
                    ac_met=["Tests verified"], ac_failed=["Pattern not found: Y"]),
        _make_grade("M3", "ACCEPTED_WITH_WARNINGS", tests=["t3"], evidence=["e3"],
                    ac_met=["Paths clean"], ac_failed=["Pattern not found: Z"]),
    ]
    adapted = adapt_item_grades(grades)

    # All passing grades should have ac_failed cleared
    for a in adapted:
        assert a["acceptance_criteria_failed"] == [], (
            f"{a['taskcard_id']}: ac_failed should be cleared for passing grade"
        )

    result = score_execution(adapted)
    assert result["all_green"] is True, (
        f"Expected all_green=true. Scores: {result.get('overall_scores')}"
    )


# ---------------------------------------------------------------------------
# TC-ADVERSARIAL-001: Edge case tests for adapter fix
# ---------------------------------------------------------------------------

def test_passing_grade_with_empty_evidence_still_scores_well():
    """ACCEPTED_VERIFIED with empty evidence and suspicious ac_failed.

    The adapter treats the passing grade as authoritative. Even when evidence_paths
    is empty and ac_failed has concerning content, the grade decision stands.
    This documents the design choice: the grader made the ACCEPTED decision,
    the adapter respects it.
    """
    from quality_scorer import score_execution

    grades = [_make_grade(
        "EDGE-1", "ACCEPTED_VERIFIED",
        tests=["t1"], evidence=[],
        ac_met=["Tests verified"],
        ac_failed=["No evidence found", "Critical validation missing"],
    )]
    adapted = adapt_item_grades(grades)

    # Passing grade clears ac_failed and injects synthetics
    assert adapted[0]["acceptance_criteria_failed"] == []
    assert "AC_GRADE_PASS" in adapted[0]["acceptance_criteria_met"]

    result = score_execution(adapted)
    ac_score = result["execution_results"][0]["quality_scores"]["acceptance_criteria_met"]
    assert ac_score >= 4, (
        f"Passing grade must score >= 4 on AC even with empty evidence, got {ac_score}"
    )


@pytest.mark.parametrize("grade", [
    "REJECTED", "REWORK_REQUIRED", "OVERCLAIMED",
    "INSUFFICIENT_EVIDENCE", "BLOCKED_EXTERNAL_GATE",
])
def test_all_failing_grades_preserve_ac_failed(grade):
    """Failing grades must preserve ac_failed and NOT inject synthetic AC entries."""
    grades = [_make_grade(
        "FAIL-1", grade,
        tests=[], evidence=[],
        ac_met=["Partial check"],
        ac_failed=["Missing proof", "Test failures"],
    )]
    adapted = adapt_item_grades(grades)

    assert adapted[0]["acceptance_criteria_failed"] == ["Missing proof", "Test failures"], (
        f"Grade {grade}: ac_failed must be preserved, got {adapted[0]['acceptance_criteria_failed']}"
    )
    assert "AC_GRADE_PASS" not in adapted[0]["acceptance_criteria_met"], (
        f"Grade {grade}: must NOT inject AC_GRADE_PASS synthetic"
    )


def test_mixed_sprint_one_failing_prevents_green():
    """4 ACCEPTED + 1 REWORK_REQUIRED -> all_green=false."""
    from quality_scorer import score_execution

    grades = [
        _make_grade("OK-1", "ACCEPTED_VERIFIED", tests=["t1", "t2"], evidence=["e1"]),
        _make_grade("OK-2", "ACCEPTED", tests=["t3"], evidence=["e2"]),
        _make_grade("OK-3", "ACCEPTED_WITH_WARNINGS", tests=["t4"], evidence=["e3"]),
        _make_grade("OK-4", "ACCEPTED_WITH_LIMITATIONS", tests=["t5"], evidence=["e4"]),
        _make_grade("BAD-1", "REWORK_REQUIRED", tests=[], evidence=[],
                    ac_met=[], ac_failed=["Failed validation"]),
    ]
    adapted = adapt_item_grades(grades)
    result = score_execution(adapted)

    assert result["all_green"] is False, (
        "One REWORK_REQUIRED item must prevent all_green=true"
    )
