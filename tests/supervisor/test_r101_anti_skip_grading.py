"""
R101 — Anti-Skip Grading Tests
Tests that the grading engine correctly rejects or downgrades items with:
  - Path-only evidence (file exists but empty/stub)
  - Missing raw logs
  - Stale selected gaps
  - Generic prompts in non-mainstream stream
  - Cross-stream context pollution

These are the "deep grading" checks that prevent accepting shallow work.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from grade_declared_work import grade_item, grade_all


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _basic_test_results(passed=10, failed=0, errors=0):
    return {"passed": passed, "failed": failed, "errors": errors}


def _completed_inspection(
    item_id="TEST-001",
    has_evidence=True,
    has_tests=True,
    missing_paths=None,
    found_paths=None,
    tests_with_content=None,
    tests_empty_or_stub=None,
    acceptance_criteria_verified=False,
    acceptance_criteria_pattern="",
):
    return {
        "item_id": item_id,
        "declared_status": "completed",
        "has_evidence": has_evidence,
        "has_tests": has_tests,
        "evidence_paths_missing": missing_paths or [],
        "evidence_paths_found": found_paths or ["evidence/test.txt"],
        "tests_declared": ["test_x.py"] if has_tests else [],
        "tests_with_content": tests_with_content or (["test_x.py"] if has_tests else []),
        "tests_empty_or_stub": tests_empty_or_stub or [],
        "acceptance_criteria_verified": acceptance_criteria_verified,
        "acceptance_criteria_pattern": acceptance_criteria_pattern,
    }


# ---------------------------------------------------------------------------
# Anti-skip: path-only evidence (declared complete, no actual content)
# ---------------------------------------------------------------------------

def test_path_only_no_evidence_is_overclaimed():
    """Declared complete but no evidence at all → OVERCLAIMED."""
    inspection = _completed_inspection(has_evidence=False)
    grade = grade_item(inspection, _basic_test_results())
    assert grade["supervisor_grade"] == "OVERCLAIMED"


def test_path_only_missing_paths_is_rework():
    """Declared complete but some evidence paths missing → REWORK_REQUIRED."""
    inspection = _completed_inspection(missing_paths=["reports/r101/missing.md"])
    grade = grade_item(inspection, _basic_test_results())
    assert grade["supervisor_grade"] == "REWORK_REQUIRED"
    assert "Missing evidence paths" in grade["required_rework"]


def test_stub_tests_get_limitations():
    """Tests exist but are empty stubs → ACCEPTED_WITH_LIMITATIONS, not VERIFIED."""
    inspection = _completed_inspection(
        tests_with_content=[],
        tests_empty_or_stub=["test_stub.py"],
    )
    grade = grade_item(inspection, _basic_test_results())
    assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"
    assert any("stub" in c.lower() for c in grade.get("acceptance_criteria_failed", []))


def test_acceptance_criteria_not_verified_gets_limitations():
    """Acceptance criteria pattern declared but not found → ACCEPTED_WITH_LIMITATIONS."""
    inspection = _completed_inspection(
        acceptance_criteria_pattern="BUNDLE_VALIDATION: PASS",
        acceptance_criteria_verified=False,
    )
    grade = grade_item(inspection, _basic_test_results())
    assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"


def test_full_evidence_gets_verified():
    """Complete evidence + real tests + criteria verified → ACCEPTED_VERIFIED."""
    inspection = _completed_inspection(
        tests_with_content=["test_real.py"],
        acceptance_criteria_pattern="test passes",
        acceptance_criteria_verified=True,
    )
    grade = grade_item(inspection, _basic_test_results())
    assert grade["supervisor_grade"] == "ACCEPTED_VERIFIED"


# ---------------------------------------------------------------------------
# Anti-skip: test failures
# ---------------------------------------------------------------------------

def test_failed_tests_require_rework():
    """Even with complete evidence, test failures → REWORK_REQUIRED."""
    inspection = _completed_inspection()
    grade = grade_item(inspection, _basic_test_results(failed=3))
    assert grade["supervisor_grade"] == "REWORK_REQUIRED"
    assert "test" in grade["required_rework"].lower()


# ---------------------------------------------------------------------------
# Anti-skip: declared status edge cases
# ---------------------------------------------------------------------------

def test_partial_no_evidence_is_rework():
    """Partial work claimed but no evidence → REWORK_REQUIRED."""
    inspection = _completed_inspection(item_id="PARTIAL-001")
    inspection["declared_status"] = "partial"
    inspection["has_evidence"] = False
    grade = grade_item(inspection, _basic_test_results())
    assert grade["supervisor_grade"] == "REWORK_REQUIRED"


def test_partial_with_evidence_is_accepted_with_warnings():
    """Partial work with evidence → ACCEPTED_WITH_WARNINGS."""
    inspection = _completed_inspection(item_id="PARTIAL-002")
    inspection["declared_status"] = "partial"
    grade = grade_item(inspection, _basic_test_results())
    assert grade["supervisor_grade"] == "ACCEPTED_WITH_WARNINGS"


def test_not_started_is_not_attempted():
    inspection = _completed_inspection(item_id="SKIP-001")
    inspection["declared_status"] = "not_started"
    grade = grade_item(inspection, _basic_test_results())
    assert grade["supervisor_grade"] == "NOT_ATTEMPTED"


def test_deferred_is_deferred_with_reason():
    inspection = _completed_inspection(item_id="DEFER-001")
    inspection["declared_status"] = "deferred"
    grade = grade_item(inspection, _basic_test_results())
    assert grade["supervisor_grade"] == "DEFERRED_WITH_REASON"


def test_blocked_gate_is_blocked():
    inspection = _completed_inspection(item_id="GATE-001")
    inspection["declared_status"] = "blocked_external_gate"
    grade = grade_item(inspection, _basic_test_results())
    assert grade["supervisor_grade"] == "BLOCKED_EXTERNAL_GATE"


# ---------------------------------------------------------------------------
# grade_all: overall verdict logic
# ---------------------------------------------------------------------------

def test_grade_all_overclaimed_blocks_continuation():
    """Any OVERCLAIMED item should block autonomous continuation."""
    declaration = {
        "planned_work_items": [
            {"item_id": "A", "title": "Item A"},
            {"item_id": "B", "title": "Item B"},
        ],
    }
    inspection = {
        "test_results": _basic_test_results(),
        "item_inspections": [
            _completed_inspection(item_id="A"),
            _completed_inspection(item_id="B", has_evidence=False),  # will be OVERCLAIMED
        ],
    }
    review = grade_all(inspection, declaration)
    assert not review["autonomous_continue"]
    assert "B" in review["overclaimed_items"]
    assert review["critical_rework_count"] > 0


def test_grade_all_all_accepted_allows_continuation():
    declaration = {
        "planned_work_items": [
            {"item_id": "A", "title": "Item A"},
        ],
    }
    inspection = {
        "test_results": _basic_test_results(),
        "item_inspections": [
            _completed_inspection(item_id="A", tests_with_content=["test.py"]),
        ],
    }
    review = grade_all(inspection, declaration)
    assert review["autonomous_continue"]
    assert "A" in review["accepted_items"]


def test_grade_all_test_failures_block_continuation():
    declaration = {
        "planned_work_items": [{"item_id": "A", "title": "Item A"}],
    }
    inspection = {
        "test_results": _basic_test_results(failed=5),
        "item_inspections": [
            _completed_inspection(item_id="A"),
        ],
    }
    review = grade_all(inspection, declaration)
    assert not review["autonomous_continue"]
