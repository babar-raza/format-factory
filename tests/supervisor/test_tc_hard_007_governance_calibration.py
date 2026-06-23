"""Regression tests for TC-HARD-007 Option A: per-item governance calibration.

TC-HARD-007: grade_item() must return ACCEPTED_VERIFIED (not ACCEPTED_WITH_LIMITATIONS)
for GOVERNANCE_TASKCARD items that have evidence but no pytest test files.

Before the fix: governance items without test files fell through with has_concrete_proof=False
and received ACCEPTED_WITH_LIMITATIONS ("No raw proof, test content, or acceptance criteria verified").

After the fix (TC-HARD-007 Option A, 2026-06-22): governance types are calibrated so that
verified file existence IS concrete proof — these items reach ACCEPTED_VERIFIED.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


def _minimal_inspection(item_id: str = "TC-GOV-001") -> dict:
    """Build a minimal item_inspection dict for a governance item with evidence, no tests."""
    return {
        "item_id": item_id,
        "declared_status": "completed",
        "has_evidence": True,
        "has_tests": False,
        "evidence_paths_found": [".claude/commands/autonomous-loop.md"],
        "evidence_paths_missing": [],
        "tests_declared": [],
        "tests_with_content": [],
        "tests_empty_or_stub": [],
        "acceptance_criteria_verified": False,
        "acceptance_criteria_pattern": "",
    }


def _passing_test_results() -> dict:
    return {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}


class TestGovernanceItemCalibration:
    """TC-HARD-007 Option A: per-item governance type calibration in grade_item()."""

    def test_governance_taskcard_accepted_verified(self):
        """GOVERNANCE_TASKCARD with evidence but no tests → ACCEPTED_VERIFIED."""
        from grade_declared_work import grade_item
        inspection = _minimal_inspection("TC-HARD-TEST-001")
        result = grade_item(inspection, _passing_test_results(), item_type="GOVERNANCE_TASKCARD")
        assert result["supervisor_grade"] == "ACCEPTED_VERIFIED", (
            f"Expected ACCEPTED_VERIFIED for GOVERNANCE_TASKCARD, got {result['supervisor_grade']}. "
            f"criteria_met={result.get('acceptance_criteria_met')}, "
            f"criteria_failed={result.get('acceptance_criteria_failed')}"
        )

    def test_governance_taskcard_calibration_message_in_criteria(self):
        """GOVERNANCE_TASKCARD calibration must append the N/A rationale to criteria_met."""
        from grade_declared_work import grade_item
        inspection = _minimal_inspection("TC-HARD-TEST-002")
        result = grade_item(inspection, _passing_test_results(), item_type="GOVERNANCE_TASKCARD")
        criteria_met_str = " ".join(result.get("acceptance_criteria_met", []))
        assert "Governance item" in criteria_met_str, (
            f"Expected 'Governance item' in criteria_met. Got: {result.get('acceptance_criteria_met')}"
        )
        assert "test coverage N/A by design" in criteria_met_str, (
            f"Expected 'test coverage N/A by design' in criteria_met. Got: {result.get('acceptance_criteria_met')}"
        )

    def test_governance_doc_accepted_verified(self):
        """GOVERNANCE_DOC type also receives ACCEPTED_VERIFIED via governance calibration."""
        from grade_declared_work import grade_item
        inspection = _minimal_inspection("TC-HARD-TEST-003")
        result = grade_item(inspection, _passing_test_results(), item_type="GOVERNANCE_DOC")
        assert result["supervisor_grade"] == "ACCEPTED_VERIFIED", (
            f"Expected ACCEPTED_VERIFIED for GOVERNANCE_DOC, got {result['supervisor_grade']}"
        )

    def test_governance_policy_accepted_verified(self):
        """GOVERNANCE_POLICY type receives ACCEPTED_VERIFIED."""
        from grade_declared_work import grade_item
        inspection = _minimal_inspection("TC-HARD-TEST-004")
        result = grade_item(inspection, _passing_test_results(), item_type="GOVERNANCE_POLICY")
        assert result["supervisor_grade"] == "ACCEPTED_VERIFIED", (
            f"Expected ACCEPTED_VERIFIED for GOVERNANCE_POLICY, got {result['supervisor_grade']}"
        )

    def test_governance_schema_accepted_verified(self):
        """GOVERNANCE_SCHEMA type receives ACCEPTED_VERIFIED."""
        from grade_declared_work import grade_item
        inspection = _minimal_inspection("TC-HARD-TEST-005")
        result = grade_item(inspection, _passing_test_results(), item_type="GOVERNANCE_SCHEMA")
        assert result["supervisor_grade"] == "ACCEPTED_VERIFIED", (
            f"Expected ACCEPTED_VERIFIED for GOVERNANCE_SCHEMA, got {result['supervisor_grade']}"
        )

    def test_governance_calibration_not_applied_when_no_evidence(self):
        """Calibration must NOT fire if has_evidence=False (item would be OVERCLAIMED)."""
        from grade_declared_work import grade_item
        inspection = _minimal_inspection("TC-HARD-TEST-006")
        inspection["has_evidence"] = False
        inspection["evidence_paths_found"] = []
        result = grade_item(inspection, _passing_test_results(), item_type="GOVERNANCE_TASKCARD")
        # No evidence → OVERCLAIMED regardless of governance type
        assert result["supervisor_grade"] == "OVERCLAIMED", (
            f"Expected OVERCLAIMED for governance item with no evidence, got {result['supervisor_grade']}"
        )

    def test_governance_calibration_not_applied_when_criteria_failed(self):
        """Calibration must NOT fire if acceptance criteria patterns are failing."""
        from grade_declared_work import grade_item
        inspection = _minimal_inspection("TC-HARD-TEST-007")
        inspection["acceptance_criteria_verified"] = False
        inspection["acceptance_criteria_pattern"] = "expected_string_not_in_file"
        result = grade_item(inspection, _passing_test_results(), item_type="GOVERNANCE_TASKCARD")
        # criteria_failed → ACCEPTED_WITH_LIMITATIONS (calibration blocked by criteria_failed check)
        assert result["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS", (
            f"Expected ACCEPTED_WITH_LIMITATIONS when criteria pattern fails, got {result['supervisor_grade']}"
        )

    def test_product_source_not_calibrated(self):
        """PRODUCT_SOURCE item without test files should NOT receive governance calibration."""
        from grade_declared_work import grade_item
        inspection = _minimal_inspection("TC-HARD-TEST-008")
        result = grade_item(inspection, _passing_test_results(), item_type="PRODUCT_SOURCE")
        # Without test content or criteria verification, PRODUCT_SOURCE gets ACCEPTED_WITH_LIMITATIONS
        assert result["supervisor_grade"] != "ACCEPTED_VERIFIED", (
            f"PRODUCT_SOURCE should NOT be upgraded by governance calibration, got {result['supervisor_grade']}"
        )

    def test_governance_calibration_skipped_when_already_concrete_proof(self):
        """If has_concrete_proof is already True (tests present), calibration branch is skipped."""
        from grade_declared_work import grade_item
        inspection = _minimal_inspection("TC-HARD-TEST-009")
        # Simulate item that already has test content verified
        inspection["has_tests"] = True
        inspection["tests_declared"] = ["tests/supervisor/test_something.py"]
        inspection["tests_with_content"] = ["tests/supervisor/test_something.py"]
        inspection["evidence_paths_found"] = [
            ".claude/commands/autonomous-loop.md",
            "tests/supervisor/test_something.py",
        ]
        result = grade_item(
            inspection,
            {"passed": 5, "failed": 0, "skipped": 0, "errors": 0},
            item_type="GOVERNANCE_TASKCARD",
        )
        # Already ACCEPTED_VERIFIED via test content — governance branch not needed but result same
        assert result["supervisor_grade"] == "ACCEPTED_VERIFIED"
        # The governance calibration message should NOT appear (branch condition: not has_concrete_proof)
        criteria_met_str = " ".join(result.get("acceptance_criteria_met", []))
        assert "test coverage N/A by design" not in criteria_met_str, (
            "Governance calibration message should not appear when test content is already present"
        )
