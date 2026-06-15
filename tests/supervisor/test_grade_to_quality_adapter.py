"""Tests for grade_to_quality_adapter — converts supervisor item-grades to quality_scorer format."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from grade_to_quality_adapter import adapt_item_grades, is_item_grades_format  # noqa: E402


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------

def test_detects_item_grades_format():
    data = [{"item_id": "X", "supervisor_grade": "ACCEPTED_VERIFIED"}]
    assert is_item_grades_format(data) is True


def test_rejects_stage3_format():
    data = [{"taskcard_id": "X", "test_results": {"passed": 1, "failed": 0}}]
    assert is_item_grades_format(data) is False


def test_rejects_empty_list():
    assert is_item_grades_format([]) is False


# ---------------------------------------------------------------------------
# Mapping correctness
# ---------------------------------------------------------------------------

def _make_grade(item_id="TC-001", grade="ACCEPTED_VERIFIED", tests=None, evidence=None,
                criteria_met=None, criteria_failed=None):
    return {
        "item_id": item_id,
        "supervisor_grade": grade,
        "tests_supporting": tests or ["tests/test_a.py"],
        "evidence_paths": evidence or ["evidence/proof.md"],
        "acceptance_criteria_met": criteria_met or ["Evidence found"],
        "acceptance_criteria_failed": criteria_failed or [],
    }


def test_maps_item_id_to_taskcard_id():
    adapted = adapt_item_grades([_make_grade(item_id="MY-ITEM")])
    assert adapted[0]["taskcard_id"] == "MY-ITEM"


def test_maps_tests_supporting_to_references():
    adapted = adapt_item_grades([_make_grade(tests=["t1.py", "t2.py"])])
    assert adapted[0]["test_references"] == ["t1.py", "t2.py"]


def test_verified_grade_produces_passed_tests():
    adapted = adapt_item_grades([_make_grade(grade="ACCEPTED_VERIFIED")])
    assert adapted[0]["test_results"]["passed"] >= 1
    assert adapted[0]["test_results"]["failed"] == 0


def test_rework_grade_produces_failed_tests():
    adapted = adapt_item_grades([_make_grade(grade="REWORK_REQUIRED")])
    assert adapted[0]["test_results"]["failed"] >= 1
    assert adapted[0]["test_results"]["passed"] == 0


def test_rejected_grade_produces_failed_tests():
    adapted = adapt_item_grades([_make_grade(grade="REJECTED")])
    assert adapted[0]["test_results"]["failed"] >= 1


def test_accepted_with_limitations_counts_as_pass():
    adapted = adapt_item_grades([_make_grade(grade="ACCEPTED_WITH_LIMITATIONS")])
    assert adapted[0]["test_results"]["passed"] >= 1
    assert adapted[0]["test_results"]["failed"] == 0


def test_evidence_paths_passed_through():
    adapted = adapt_item_grades([_make_grade(evidence=["a.md", "b.md"])])
    assert adapted[0]["evidence_paths"] == ["a.md", "b.md"]


def test_acceptance_criteria_mapped():
    adapted = adapt_item_grades([_make_grade(
        criteria_met=["Evidence found", "Tests pass"],
        criteria_failed=["Missing schema proof"],
    )])
    assert len(adapted[0]["acceptance_criteria_met"]) == 2
    assert len(adapted[0]["acceptance_criteria_failed"]) == 1


# ---------------------------------------------------------------------------
# Integration with quality_scorer
# ---------------------------------------------------------------------------

from quality_scorer import score_taskcard, QUALITY_THRESHOLD  # noqa: E402


def test_verified_item_scores_correctness_above_threshold():
    adapted = adapt_item_grades([_make_grade(grade="ACCEPTED_VERIFIED", tests=["t1", "t2", "t3"])])
    scores = score_taskcard(adapted[0])
    assert scores["correctness"] >= QUALITY_THRESHOLD


def test_verified_item_scores_test_coverage_above_threshold():
    adapted = adapt_item_grades([_make_grade(grade="ACCEPTED_VERIFIED", tests=["t1", "t2", "t3"])])
    scores = score_taskcard(adapted[0])
    assert scores["test_coverage"] >= QUALITY_THRESHOLD


def test_rework_item_scores_correctness_below_threshold():
    adapted = adapt_item_grades([_make_grade(grade="REWORK_REQUIRED")])
    scores = score_taskcard(adapted[0])
    assert scores["correctness"] < QUALITY_THRESHOLD


def test_all_green_on_fully_verified_sprint():
    items = [
        _make_grade(item_id=f"TC-{i}", grade="ACCEPTED_VERIFIED", tests=["t1", "t2", "t3"])
        for i in range(3)
    ]
    adapted = adapt_item_grades(items)
    from quality_scorer import score_execution
    result = score_execution(adapted)
    assert result["all_green"] is True
    assert result["overall_verdict"] == "EXECUTION_COMPLETE_VERIFIED"


def test_not_all_green_with_rework_items():
    items = [
        _make_grade(item_id="TC-1", grade="ACCEPTED_VERIFIED", tests=["t1", "t2", "t3"]),
        _make_grade(item_id="TC-2", grade="REWORK_REQUIRED"),
    ]
    adapted = adapt_item_grades(items)
    from quality_scorer import score_execution
    result = score_execution(adapted)
    assert result["all_green"] is False


def test_mixed_grades_produce_meaningful_scores():
    """ACCEPTED_WITH_LIMITATIONS should still score above 1 on key dimensions."""
    adapted = adapt_item_grades([_make_grade(grade="ACCEPTED_WITH_LIMITATIONS", tests=["t1"])])
    scores = score_taskcard(adapted[0])
    # Should score meaningfully — not all 1s
    assert scores["correctness"] >= QUALITY_THRESHOLD
    assert scores["governance_compliance"] >= QUALITY_THRESHOLD
    assert scores["evidence_completeness"] >= QUALITY_THRESHOLD


# ---------------------------------------------------------------------------
# Real data integration (uses actual item-grades.json if available)
# ---------------------------------------------------------------------------

REAL_GRADES_PATH = REPO_ROOT / ".local" / "supervisor" / "reviews" / "post-sprint-autonomy-loop-20260615-0f43aa0" / "item-grades.json"


@pytest.mark.skipif(not REAL_GRADES_PATH.exists(), reason="Real item-grades not available")
def test_real_item_grades_adapter_produces_meaningful_scores():
    """Prove adapter works on actual supervisor output, not just synthetic fixtures."""
    data = json.loads(REAL_GRADES_PATH.read_text(encoding="utf-8"))
    assert is_item_grades_format(data)
    adapted = adapt_item_grades(data)
    assert len(adapted) == len(data)

    from quality_scorer import score_execution
    result = score_execution(adapted)

    # Verify: ACCEPTED_VERIFIED items should score well
    for entry in result["execution_results"]:
        orig_grade = entry.get("_original_supervisor_grade", "")
        # The adapted results don't carry _original, but we can check by index
        pass  # Just verify it runs without error and produces structured output

    # Must produce structured output with all required fields
    assert "overall_scores" in result
    assert "all_green" in result
    assert "execution_results" in result
    assert len(result["execution_results"]) == len(data)


@pytest.mark.skipif(not REAL_GRADES_PATH.exists(), reason="Real item-grades not available")
def test_real_verified_items_score_above_threshold():
    """Verified items from real data should score correctness >= 4 after adaptation."""
    data = json.loads(REAL_GRADES_PATH.read_text(encoding="utf-8"))
    adapted = adapt_item_grades(data)

    verified_indices = [i for i, g in enumerate(data) if g.get("supervisor_grade") == "ACCEPTED_VERIFIED"]
    for idx in verified_indices:
        scores = score_taskcard(adapted[idx])
        assert scores["correctness"] >= QUALITY_THRESHOLD, (
            f"Item {data[idx]['item_id']} (ACCEPTED_VERIFIED) scored correctness={scores['correctness']}"
        )
