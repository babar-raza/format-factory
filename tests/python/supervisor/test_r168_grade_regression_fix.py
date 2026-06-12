"""
test_r168_grade_regression_fix.py -- Regression test for tests_evidence_verified key separation.

Sprint: FORMAT-FACTORY-GAP-CLOSURE-AND-DEEPENING-20260611-001
Fix: grade_declared_work.py GC-008 — changed 'tests_supporting' to 'tests_evidence_verified'
     to prevent false ACCEPTED_VERIFIED when tests_declared has default fallback values.

The bug: when make_inspection is called with tests_declared=[], the `or` default fills it
with ["test_something.py"]. If has_concrete_proof checked grade["tests_supporting"]
(which was populated from tests_declared at line 259), a path-only item would incorrectly
get ACCEPTED_VERIFIED instead of ACCEPTED_WITH_LIMITATIONS.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from grade_declared_work import grade_item


def _make_inspection(
    declared_status="completed",
    has_evidence=True,
    has_tests=True,
    evidence_paths_found=None,
    evidence_paths_missing=None,
    tests_declared=None,
    tests_with_content=None,
    tests_empty_or_stub=None,
    acceptance_criteria_verified=False,
    transcript_validation=None,
):
    return {
        "item_id": "W-REGRESSION-TEST",
        "declared_status": declared_status,
        "has_evidence": has_evidence,
        "has_tests": has_tests,
        "evidence_paths_found": evidence_paths_found or ["reports/test/evidence.md"],
        "evidence_paths_missing": evidence_paths_missing or [],
        "tests_declared": tests_declared if tests_declared is not None else ["test_something.py"],
        "tests_with_content": tests_with_content if tests_with_content is not None else (["test_something.py"] if has_tests else []),
        "tests_empty_or_stub": tests_empty_or_stub or [],
        "acceptance_criteria_verified": acceptance_criteria_verified,
        "acceptance_criteria_pattern": "",
        "transcript_validation": transcript_validation,
    }


def _make_test_results(passed=10, failed=0):
    return {"passed": passed, "failed": failed, "errors": 0}


class TestGradeRegressionFix:
    """Verify that the tests_evidence_verified separation prevents false ACCEPTED_VERIFIED."""

    def test_path_only_no_tests_is_with_limitations(self):
        """Core regression: completed item with evidence but no tests => ACCEPTED_WITH_LIMITATIONS.

        This was failing with ACCEPTED_VERIFIED before the fix because grade["tests_supporting"]
        was populated from tests_declared (which has a default fallback), and has_concrete_proof
        incorrectly checked bool(grade.get("tests_supporting")).
        """
        insp = _make_inspection(
            has_tests=False,
            tests_with_content=[],
            tests_declared=[],
        )
        grade = grade_item(insp, _make_test_results())
        assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS", (
            f"Expected ACCEPTED_WITH_LIMITATIONS but got {grade['supervisor_grade']}. "
            "Regression: path-only item should NOT be ACCEPTED_VERIFIED."
        )

    def test_item_with_test_content_is_accepted_verified(self):
        """Item with actual test content (tests_with_content populated) => ACCEPTED_VERIFIED."""
        insp = _make_inspection(
            has_tests=True,
            tests_with_content=["test_something.py"],
        )
        grade = grade_item(insp, _make_test_results())
        assert grade["supervisor_grade"] == "ACCEPTED_VERIFIED"

    def test_tests_supporting_not_used_for_proof(self):
        """tests_supporting from declaration does not create ACCEPTED_VERIFIED without actual content."""
        insp = _make_inspection(
            has_tests=False,
            tests_with_content=[],
            tests_declared=["test_exists_on_disk.py"],  # declared but no content verification
        )
        grade = grade_item(insp, _make_test_results())
        # Should be WITH_LIMITATIONS, not VERIFIED, because tests_with_content is empty
        assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"

    def test_tests_evidence_verified_populated_from_paths(self):
        """tests_evidence_verified is set when evidence path contains test_ and results pass."""
        insp = _make_inspection(
            has_tests=False,
            tests_with_content=[],
            tests_declared=[],
            evidence_paths_found=["tests/python/format/test_format.py"],
        )
        grade = grade_item(insp, _make_test_results(passed=5, failed=0))
        # The evidence path IS a test file and passed > 0 → tests_evidence_verified populated
        # → has_concrete_proof = True → ACCEPTED_VERIFIED
        assert grade["supervisor_grade"] == "ACCEPTED_VERIFIED"
        assert "tests_evidence_verified" in grade
        assert len(grade["tests_evidence_verified"]) > 0

    def test_tests_evidence_verified_not_populated_when_failed(self):
        """tests_evidence_verified is NOT set when test results show failures."""
        insp = _make_inspection(
            has_tests=False,
            tests_with_content=[],
            tests_declared=[],
            evidence_paths_found=["tests/python/format/test_format.py"],
        )
        grade = grade_item(insp, _make_test_results(passed=5, failed=2))
        # failed > 0 → condition not met → tests_evidence_verified NOT set → WITH_LIMITATIONS
        assert grade.get("tests_evidence_verified") is None or grade.get("tests_evidence_verified") == []

    def test_completed_no_evidence_is_overclaimed(self):
        """Completed with no evidence => OVERCLAIMED (unaffected by the fix)."""
        insp = _make_inspection(has_evidence=False)
        grade = grade_item(insp, _make_test_results())
        assert grade["supervisor_grade"] == "OVERCLAIMED"
