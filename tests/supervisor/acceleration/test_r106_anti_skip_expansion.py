"""Tests for R106 anti-skip checker expansion — 11→16 detectors."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from anti_skip_checker import (
    detect_evidence_quality_score,
    detect_declaration_completeness,
    detect_test_count_regression,
    run_all_checks,
)


# --- Evidence quality score detection (R106) ---

def test_evidence_quality_all_path_only():
    """Positive: all items ACCEPTED_WITH_LIMITATIONS means 0% quality score."""
    grades = [
        {"item_id": "W0", "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS"},
        {"item_id": "W1", "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS"},
    ]
    result = detect_evidence_quality_score(grades)
    assert result["is_violation"] is True
    assert result["score"] == 0.0
    assert result["verified_count"] == 0
    assert result["accepted_count"] == 2


def test_evidence_quality_some_verified():
    """Negative: at least one ACCEPTED_VERIFIED → not a violation."""
    grades = [
        {"item_id": "W0", "supervisor_grade": "ACCEPTED_VERIFIED"},
        {"item_id": "W1", "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS"},
    ]
    result = detect_evidence_quality_score(grades)
    assert result["is_violation"] is False
    assert result["score"] == 0.5
    assert result["verified_count"] == 1


def test_evidence_quality_all_verified():
    """Negative: 100% verified is not a violation."""
    grades = [
        {"item_id": "W0", "supervisor_grade": "ACCEPTED_VERIFIED"},
        {"item_id": "W1", "supervisor_grade": "ACCEPTED_VERIFIED"},
    ]
    result = detect_evidence_quality_score(grades)
    assert result["is_violation"] is False
    assert result["score"] == 1.0


def test_evidence_quality_no_accepted():
    """Negative: no accepted items → no violation."""
    grades = [
        {"item_id": "W0", "supervisor_grade": "REJECTED"},
    ]
    result = detect_evidence_quality_score(grades)
    assert result["is_violation"] is False


def test_evidence_quality_dict_format():
    """Works with dict format (work_item_grades key)."""
    grades = {"work_item_grades": [
        {"item_id": "W0", "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS"},
    ]}
    result = detect_evidence_quality_score(grades)
    assert result["is_violation"] is True


def test_evidence_quality_mixed_grades():
    """Non-accepted grades don't count in denominator."""
    grades = [
        {"item_id": "W0", "supervisor_grade": "ACCEPTED_VERIFIED"},
        {"item_id": "W1", "supervisor_grade": "REJECTED"},
        {"item_id": "W2", "supervisor_grade": "NOT_ATTEMPTED"},
    ]
    result = detect_evidence_quality_score(grades)
    assert result["is_violation"] is False
    assert result["score"] == 1.0
    assert result["accepted_count"] == 1


# --- Declaration completeness detection (R106) ---

def test_declaration_completeness_missing_fields():
    """Positive: missing required fields is violation."""
    decl = {"run_id": "test"}
    result = detect_declaration_completeness(decl)
    assert result["is_violation"] is True
    assert "sprint_id" in result["missing_fields"]
    assert "evidence_root" in result["missing_fields"]


def test_declaration_completeness_all_present():
    """Negative: all required fields present."""
    decl = {
        "run_id": "test",
        "sprint_id": "SPRINT-001",
        "evidence_root": "reports/test",
        "planned_work_items": [],
        "test_results": {"passed": 0},
        "worker_self_verdict": "PASS",
    }
    result = detect_declaration_completeness(decl)
    assert result["is_violation"] is False
    assert len(result["missing_fields"]) == 0


def test_declaration_completeness_empty():
    """Positive: empty declaration has all fields missing."""
    result = detect_declaration_completeness({})
    assert result["is_violation"] is True
    assert len(result["missing_fields"]) == 6


# --- Test count regression detection (R106) ---

def test_test_count_regression_detected():
    """Positive: test count dropped."""
    decl = {"test_results": {"passed": 50, "failed": 0}}
    result = detect_test_count_regression(decl, prior_test_count=100)
    assert result["is_violation"] is True
    assert result["current_count"] == 50
    assert result["prior_count"] == 100


def test_test_count_regression_not_detected():
    """Negative: test count increased."""
    decl = {"test_results": {"passed": 150, "failed": 0}}
    result = detect_test_count_regression(decl, prior_test_count=100)
    assert result["is_violation"] is False


def test_test_count_regression_no_prior():
    """Negative: no prior count means no regression."""
    decl = {"test_results": {"passed": 50, "failed": 0}}
    result = detect_test_count_regression(decl, prior_test_count=0)
    assert result["is_violation"] is False


def test_test_count_regression_equal():
    """Negative: same count is not regression."""
    decl = {"test_results": {"passed": 100, "failed": 0}}
    result = detect_test_count_regression(decl, prior_test_count=100)
    assert result["is_violation"] is False


def test_test_count_includes_failures():
    """Current count includes both passed and failed."""
    decl = {"test_results": {"passed": 90, "failed": 10}}
    result = detect_test_count_regression(decl, prior_test_count=100)
    assert result["is_violation"] is False
    assert result["current_count"] == 100


# --- Consolidated 16-check run (R107) ---

def test_run_all_16_checks(tmp_path):
    """All 16 checks run when all inputs provided."""
    (tmp_path / "raw-test-log.txt").write_text("output")
    (tmp_path / "evidence-manifest.yaml").write_text("sprint_id: SPRINT-R106")
    (tmp_path / "dry-run-ledger.json").write_text("{}")
    samples = tmp_path / "sample-outputs"
    samples.mkdir()
    (samples / "gaps.json").write_text("{}")
    (tmp_path / "reports" / "r106").mkdir(parents=True)
    (tmp_path / "reports" / "r106" / "preflight.md").write_text("ok")
    declaration = {
        "run_id": "acceleration-r106",
        "sprint_id": "SPRINT-R106",
        "evidence_root": "reports/r106",
        "planned_work_items": [],
        "test_results": {"passed": 100, "failed": 0},
        "worker_self_verdict": "PASS",
        "reports_created": ["reports/r106/preflight.md"],
        "git_status_final": "clean",
        "changed_files": [],
    }
    result = run_all_checks(
        prompt_text="Acceleration sprint: improve tools. Add skills registry entries.",
        gaps_data={"sprint_id": "SPRINT-R106", "stream": "acceleration"},
        expected_sprint="SPRINT-R106",
        evidence_root=tmp_path,
        declaration=declaration,
        grades=[{"item_id": "A1", "supervisor_grade": "ACCEPTED_VERIFIED", "test_file_content_checked": True}],
        target_stream="acceleration",
        repo_root=tmp_path,
        sample_outputs_dir=samples,
        prior_test_count=50,
    )
    assert result["total_checks"] == 17
    assert result["all_pass"] is True
