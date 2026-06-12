"""
Regression tests for evidence declaration worker_self_grade schema.

Sprint: FORMAT-FACTORY-SAL-PHASE2-CLOSEOUT-AND-PRODUCT-GATED-ADVANCEMENT-001
Fixes: Prior sprint failure where ACCEPTED_WITH_LIMITATIONS was used as worker_self_grade,
       which is not a valid enum value.

Valid values: PASS, PARTIAL, FAIL, BLOCKED
"""
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO / "tools" / "supervisor"))

from evidence_declaration import validate_schema, VALID_SELF_GRADES


class TestValidSelfGrades:
    """Verify the enum values allowed for worker_self_grade."""

    def test_valid_grades_are_exactly_four(self):
        assert len(VALID_SELF_GRADES) == 4

    def test_pass_is_valid(self):
        assert "PASS" in VALID_SELF_GRADES

    def test_partial_is_valid(self):
        assert "PARTIAL" in VALID_SELF_GRADES

    def test_fail_is_valid(self):
        assert "FAIL" in VALID_SELF_GRADES

    def test_blocked_is_valid(self):
        assert "BLOCKED" in VALID_SELF_GRADES

    def test_accepted_with_limitations_is_not_valid(self):
        """Prior sprint used ACCEPTED_WITH_LIMITATIONS which caused schema failure."""
        assert "ACCEPTED_WITH_LIMITATIONS" not in VALID_SELF_GRADES

    def test_accepted_is_not_valid(self):
        assert "ACCEPTED" not in VALID_SELF_GRADES

    def test_warn_is_not_valid(self):
        assert "WARN" not in VALID_SELF_GRADES


class TestDeclarationSchemaWorkerSelfGrade:
    """Verify validate_declaration_schema catches invalid worker_self_grade."""

    def _minimal_decl(self, grade):
        return {
            "sprint_id": "TEST-SPRINT-001",
            "run_id": "test-run-001",
            "evidence_root": ".local/evidences/test-run-001",
            "declared_scope": "test",
            "planned_work_items": [],
            "completed_work_items": [],
            "tests_run": 0,
            "test_results": {"passed": 0, "failed": 0, "skipped": 0, "errors": 0},
            "worker_self_verdict": "PASS",
            "worker_self_grade": grade,
        }

    def _grade_errors(self, grade):
        """Return only the custom worker_self_grade validation errors (not JSON schema dump)."""
        decl = self._minimal_decl(grade)
        errors = validate_schema(decl)
        # Custom error message is exactly "Invalid worker_self_grade: <value>"
        return [e for e in errors if e.startswith("Invalid worker_self_grade:")]

    def test_accepted_with_limitations_fails_schema(self):
        """ACCEPTED_WITH_LIMITATIONS must be rejected — regression test for prior sprint failure."""
        errors = self._grade_errors("ACCEPTED_WITH_LIMITATIONS")
        assert errors, "Expected Invalid worker_self_grade error for ACCEPTED_WITH_LIMITATIONS"
        assert "ACCEPTED_WITH_LIMITATIONS" in errors[0]

    def test_partial_passes_schema(self):
        errors = self._grade_errors("PARTIAL")
        assert not errors, f"PARTIAL should be valid but got: {errors}"

    def test_pass_passes_schema(self):
        errors = self._grade_errors("PASS")
        assert not errors, f"PASS should be valid but got: {errors}"

    def test_fail_passes_schema(self):
        errors = self._grade_errors("FAIL")
        assert not errors, f"FAIL should be valid but got: {errors}"

    def test_blocked_passes_schema(self):
        errors = self._grade_errors("BLOCKED")
        assert not errors, f"BLOCKED should be valid but got: {errors}"

    def test_empty_grade_is_allowed(self):
        """Empty grade is skipped (not a required field)."""
        errors = self._grade_errors("")
        assert not errors

    def test_accepted_fails_schema(self):
        errors = self._grade_errors("ACCEPTED")
        assert errors, "Expected Invalid worker_self_grade error for ACCEPTED"

    def test_accepted_verified_fails_schema(self):
        errors = self._grade_errors("ACCEPTED_VERIFIED")
        assert errors, "Expected Invalid worker_self_grade error for ACCEPTED_VERIFIED"
