"""
Tests for summary_classifier and loop controller using production-like data.
TC-REALDATA-001: Verify classifier handles quality-scores.json schema correctly
and the full chain (adapter -> scorer -> classifier -> loop controller) works.
"""
import json
import sys
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))
sys.path.insert(0, str(_repo_root / "tools" / "supervisor"))

from summary_classifier import classify_summary, _is_quality_scores_format
from post_sprint_loop_controller import init_loop, transition_to, classify_and_decide
from grade_to_quality_adapter import adapt_item_grades, PASSING_GRADES, FAILING_GRADES
from quality_scorer import score_execution


# ---------------------------------------------------------------------------
# Fixtures: production-like quality-scores.json
# ---------------------------------------------------------------------------

def _make_quality_scores_json(tmp_path, all_green=True, ac_score=5):
    """Write a quality-scores.json matching real production schema.

    Real production files have: execution_results, overall_scores,
    overall_verdict, all_green, reroute_log — but NO evidence_bundle_path
    and NO evidence_manifest.
    """
    base_score = 5 if all_green else 3
    scores = {
        "correctness": base_score,
        "test_coverage": base_score,
        "evidence_completeness": base_score,
        "code_quality": base_score,
        "schema_compliance": base_score,
        "governance_compliance": base_score,
        "path_discipline": base_score,
        "documentation": max(base_score, 4),
        "idempotency": max(base_score, 4),
        "regression_safety": base_score,
        "performance": max(base_score, 4),
        "error_handling": max(base_score, 4),
        "integration_consistency": base_score,
        "evidence_traceability": base_score,
        "acceptance_criteria_met": ac_score,
    }
    rerouted = not all_green or ac_score < 4
    data = {
        "execution_results": [
            {
                "taskcard_id": "TASK-001",
                "status": "REROUTED" if rerouted else "COMPLETED",
                "quality_scores": scores,
                "evidence_paths": ["path/to/evidence.txt"],
                "test_results": {"passed": 5, "failed": 0, "skipped": 0},
                "rerouted": rerouted,
            }
        ],
        "overall_scores": scores,
        "overall_verdict": "EXECUTION_COMPLETE_VERIFIED" if all_green and not rerouted
            else "EXECUTION_REROUTED_REWORK_REQUIRED",
        "all_green": all_green and not rerouted,
        "reroute_log": [] if (all_green and not rerouted) else [
            {"taskcard_id": "TASK-001", "reason": "Below threshold", "failing_dimensions": ["acceptance_criteria_met"]}
        ],
    }
    path = tmp_path / "quality-scores.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Tests: _is_quality_scores_format detection
# ---------------------------------------------------------------------------

def test_detects_quality_scores_format():
    data = {
        "execution_results": [{"taskcard_id": "T1"}],
        "overall_scores": {"correctness": 5},
        "overall_verdict": "EXECUTION_COMPLETE_VERIFIED",
    }
    assert _is_quality_scores_format(data) is True


def test_rejects_non_quality_scores_format():
    data = {"some_key": "some_value"}
    assert _is_quality_scores_format(data) is False


def test_rejects_empty_dict():
    assert _is_quality_scores_format({}) is False


# ---------------------------------------------------------------------------
# Tests: Classifier on quality-scores.json (BUG-1 fix validation)
# ---------------------------------------------------------------------------

def test_classifier_not_evidence_missing_for_quality_scores(tmp_path):
    """Quality-scores.json must NOT be classified as EVIDENCE_MISSING."""
    path = _make_quality_scores_json(tmp_path, all_green=True)
    result = classify_summary(path)
    assert result["classification"] != "EVIDENCE_MISSING", (
        f"Classifier returned EVIDENCE_MISSING for quality-scores.json: {result['reason']}"
    )


def test_classifier_all_green_quality_scores(tmp_path):
    """All-green quality-scores.json should classify as STRUCTURED_ALL_GREEN."""
    path = _make_quality_scores_json(tmp_path, all_green=True, ac_score=5)
    result = classify_summary(path)
    assert result["classification"] == "STRUCTURED_ALL_GREEN", (
        f"Expected STRUCTURED_ALL_GREEN, got {result['classification']}: {result['reason']}"
    )


def test_classifier_not_green_quality_scores(tmp_path):
    """Low-score quality-scores.json should classify as STRUCTURED_NOT_GREEN."""
    path = _make_quality_scores_json(tmp_path, all_green=False, ac_score=2)
    result = classify_summary(path)
    assert result["classification"] == "STRUCTURED_NOT_GREEN", (
        f"Expected STRUCTURED_NOT_GREEN, got {result['classification']}: {result['reason']}"
    )


def test_classifier_still_catches_true_evidence_missing(tmp_path):
    """Files with no execution_results AND no evidence should still be EVIDENCE_MISSING."""
    data = {"some_field": "some_value", "no_results": True}
    path = tmp_path / "not-quality-scores.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    result = classify_summary(path)
    # This should be EVIDENCE_MISSING or TASKCARDS_INCOMPLETE — NOT STRUCTURED_*
    assert result["classification"] in ("EVIDENCE_MISSING", "TASKCARDS_INCOMPLETE", "SCORES_MISSING")


# ---------------------------------------------------------------------------
# Tests: Full chain (adapter -> scorer -> classifier)
# ---------------------------------------------------------------------------

def test_full_chain_accepted_grades_not_evidence_missing(tmp_path):
    """Full chain: ACCEPTED grades -> adapter -> scorer -> classifier -> NOT EVIDENCE_MISSING."""
    grades = [
        {
            "item_id": "ITEM-001",
            "supervisor_grade": "ACCEPTED_VERIFIED",
            "evidence_paths": ["evidence/proof.txt"],
            "tests_supporting": ["tests/test_a.py::test_one", "tests/test_a.py::test_two"],
            "acceptance_criteria_met": ["AC1"],
            "acceptance_criteria_failed": [],
        },
    ]
    adapted = adapt_item_grades(grades)
    result = score_execution(adapted)

    # Write to file for classifier
    path = tmp_path / "quality-scores.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    classification = classify_summary(path)
    assert classification["classification"] != "EVIDENCE_MISSING", (
        f"Full chain produced EVIDENCE_MISSING: {classification['reason']}"
    )


def test_full_chain_accepted_produces_all_green(tmp_path):
    """Full chain: all-ACCEPTED grades should produce all_green=true -> STRUCTURED_ALL_GREEN."""
    grades = [
        {
            "item_id": "ITEM-001",
            "supervisor_grade": "ACCEPTED_VERIFIED",
            "evidence_paths": ["evidence/proof.txt"],
            "tests_supporting": ["tests/test_a.py::test_one", "tests/test_b.py::test_two"],
            "acceptance_criteria_met": ["AC1"],
            "acceptance_criteria_failed": [],
        },
        {
            "item_id": "ITEM-002",
            "supervisor_grade": "ACCEPTED",
            "evidence_paths": ["evidence/proof2.txt"],
            "tests_supporting": ["tests/test_c.py::test_three"],
            "acceptance_criteria_met": [],
            "acceptance_criteria_failed": [],
        },
    ]
    adapted = adapt_item_grades(grades)
    result = score_execution(adapted)

    assert result["all_green"] is True, (
        f"Expected all_green=true for all-ACCEPTED grades. "
        f"Scores: {result.get('overall_scores')}. Reroute: {result.get('reroute_log')}"
    )

    path = tmp_path / "quality-scores.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    classification = classify_summary(path)
    assert classification["classification"] == "STRUCTURED_ALL_GREEN", (
        f"Expected STRUCTURED_ALL_GREEN, got {classification['classification']}: {classification['reason']}"
    )


def test_full_chain_rejected_not_all_green(tmp_path):
    """Full chain: REJECTED grades should NOT produce all_green."""
    grades = [
        {
            "item_id": "ITEM-001",
            "supervisor_grade": "REJECTED",
            "evidence_paths": [],
            "tests_supporting": [],
            "acceptance_criteria_met": [],
            "acceptance_criteria_failed": ["AC1"],
        },
    ]
    adapted = adapt_item_grades(grades)
    result = score_execution(adapted)
    assert result["all_green"] is False


# ---------------------------------------------------------------------------
# Tests: Loop controller with fresh state (BUG-2 fix validation)
# ---------------------------------------------------------------------------

def test_loop_controller_fresh_state_not_max_loops(tmp_path):
    """Fresh loop state + classify should NOT hit MAX_LOOPS_EXCEEDED on first iteration."""
    init_loop(tmp_path, "test-fresh-001", max_loops=12)
    # Fast-forward to EXECUTION_COMPLETE
    for state, trigger in [
        ("AUDIT_RUNNING", "audit"), ("AUDIT_COMPLETE", "audit_done"),
        ("HARDENING_RUNNING", "harden"), ("HARDENING_COMPLETE", "harden_done"),
        ("EXECUTION_RUNNING", "execute"), ("EXECUTION_COMPLETE", "execute_done"),
    ]:
        transition_to(tmp_path, state, trigger)

    # Write quality scores
    path = _make_quality_scores_json(tmp_path, all_green=True, ac_score=5)
    decision = classify_and_decide(tmp_path, path)

    assert decision["next_state"] != "MAX_LOOPS_EXCEEDED", (
        f"Fresh state should not hit MAX_LOOPS_EXCEEDED. "
        f"Classification: {decision['classification']['classification']}, "
        f"Iteration: {decision['iteration']}"
    )
    assert decision["iteration"] == 1


# ---------------------------------------------------------------------------
# Tests: Production-realistic AC diagnostics (TC-ACSCORE-002 / TC-REALDATA-002)
# ---------------------------------------------------------------------------

def test_full_chain_with_production_ac_diagnostics(tmp_path):
    """Full chain: ACCEPTED grades with non-empty ac_failed diagnostics -> STRUCTURED_ALL_GREEN.

    Real production grades have ac_failed populated with pattern-matching messages
    even for ACCEPTED items. The adapter must treat passing grades as authoritative
    and clear these diagnostics so the scorer doesn't penalize them.
    """
    grades = [
        {
            "item_id": "SWARM-S2-DIF-GAP-CLOSURE",
            "supervisor_grade": "ACCEPTED_WITH_WARNINGS",
            "evidence_paths": ["evidence/dif-proof.txt"],
            "tests_supporting": ["tests/python/dif/test_dif_gaps.py::test_one"],
            "acceptance_criteria_met": ["Evidence found", "No missing paths", "Test content verified"],
            "acceptance_criteria_failed": ["Acceptance criteria pattern not found: DIF gap closure tests pass"],
        },
        {
            "item_id": "SWARM-S2-FODG-GAP-CLOSURE",
            "supervisor_grade": "ACCEPTED_WITH_WARNINGS",
            "evidence_paths": ["evidence/fodg-proof.txt"],
            "tests_supporting": ["tests/python/fodg/test_fodg_gaps.py::test_one"],
            "acceptance_criteria_met": ["Evidence found", "Tests verified"],
            "acceptance_criteria_failed": ["Acceptance criteria pattern not found: FODG gap closure tests pass for all 15 gaps"],
        },
    ]
    adapted = adapt_item_grades(grades)
    result = score_execution(adapted)

    # All passing grades must score >= 4 on acceptance_criteria_met
    for er in result["execution_results"]:
        ac_score = er["quality_scores"]["acceptance_criteria_met"]
        assert ac_score >= 4, (
            f"{er['taskcard_id']}: acceptance_criteria_met={ac_score}, "
            f"expected >= 4 for passing grade with pattern diagnostics"
        )

    assert result["all_green"] is True, (
        f"Expected all_green=true for production-like ACCEPTED grades. "
        f"Scores: {result.get('overall_scores')}. Reroute: {result.get('reroute_log')}"
    )

    # Write to file for classifier
    path = tmp_path / "quality-scores.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    classification = classify_summary(path)
    assert classification["classification"] == "STRUCTURED_ALL_GREEN", (
        f"Expected STRUCTURED_ALL_GREEN, got {classification['classification']}: "
        f"{classification['reason']}"
    )
