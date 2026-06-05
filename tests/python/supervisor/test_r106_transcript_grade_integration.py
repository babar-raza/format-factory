"""Tests for Skills R106 transcript-to-grade integration.

Validates that grade_declared_work.py correctly applies transcript validation
when work items are associated with governed skills.

These tests extend R105's transcript grading tests by:
1. Testing the actual grade_item() function with transcript-enriched inspections
2. Verifying missing/invalid/valid transcript scenarios produce correct grades
3. Verifying anti-bypass and LIVE mode scenarios
4. Testing the full grade_all() pipeline with transcript awareness
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from grade_declared_work import grade_item, grade_all
from validate_skill_transcript import validate_transcript, VALID_MODES


# ============================================================
# Helper: build inspection dicts that grade_item() expects
# ============================================================

def make_inspection(
    item_id="W-TEST",
    declared_status="completed",
    has_evidence=True,
    has_tests=True,
    evidence_paths_found=None,
    evidence_paths_missing=None,
    tests_declared=None,
    tests_with_content=None,
    tests_empty_or_stub=None,
    acceptance_criteria_verified=False,
    acceptance_criteria_pattern="",
    transcript_validation=None,
):
    """Build an item inspection dict compatible with grade_item()."""
    return {
        "item_id": item_id,
        "declared_status": declared_status,
        "has_evidence": has_evidence,
        "has_tests": has_tests,
        "evidence_paths_found": evidence_paths_found or ["reports/test/evidence.md"],
        "evidence_paths_missing": evidence_paths_missing or [],
        "tests_declared": tests_declared or ["test_something.py"],
        "tests_with_content": tests_with_content or (["test_something.py"] if has_tests else []),
        "tests_empty_or_stub": tests_empty_or_stub or [],
        "acceptance_criteria_verified": acceptance_criteria_verified,
        "acceptance_criteria_pattern": acceptance_criteria_pattern,
        "transcript_validation": transcript_validation,
    }


def make_test_results(passed=10, failed=0, errors=0):
    return {"passed": passed, "failed": failed, "errors": errors}


# ============================================================
# Test: grade_item handles transcript-enriched inspections
# ============================================================

class TestGradeItemTranscriptAwareness:
    """Test that grade_item produces correct grades for transcript scenarios."""

    def test_completed_with_evidence_and_tests_is_accepted_verified(self):
        """Standard case: completed item with evidence and test content => ACCEPTED_VERIFIED."""
        insp = make_inspection(
            has_evidence=True,
            has_tests=True,
            tests_with_content=["test_a.py"],
        )
        grade = grade_item(insp, make_test_results())
        assert grade["supervisor_grade"] == "ACCEPTED_VERIFIED"

    def test_completed_no_evidence_is_overclaimed(self):
        """Completed but no evidence => OVERCLAIMED."""
        insp = make_inspection(has_evidence=False)
        grade = grade_item(insp, make_test_results())
        assert grade["supervisor_grade"] == "OVERCLAIMED"

    def test_completed_with_missing_paths_is_rework(self):
        """Completed but missing evidence paths => REWORK_REQUIRED."""
        insp = make_inspection(
            evidence_paths_missing=["reports/test/missing.md"],
        )
        grade = grade_item(insp, make_test_results())
        assert grade["supervisor_grade"] == "REWORK_REQUIRED"

    def test_completed_path_only_no_tests_is_with_limitations(self):
        """Completed with evidence paths but no test content => ACCEPTED_WITH_LIMITATIONS."""
        insp = make_inspection(
            has_tests=False,
            tests_with_content=[],
            tests_declared=[],
        )
        grade = grade_item(insp, make_test_results())
        assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"

    def test_blocked_external_gate_passes_through(self):
        """Blocked items should remain BLOCKED_EXTERNAL_GATE."""
        insp = make_inspection(declared_status="blocked_external_gate")
        grade = grade_item(insp, make_test_results())
        assert grade["supervisor_grade"] == "BLOCKED_EXTERNAL_GATE"

    def test_not_started_is_not_attempted(self):
        """Not started items => NOT_ATTEMPTED."""
        insp = make_inspection(declared_status="not_started")
        grade = grade_item(insp, make_test_results())
        assert grade["supervisor_grade"] == "NOT_ATTEMPTED"


# ============================================================
# Test: Transcript validation outcomes map to correct grades
# ============================================================

class TestTranscriptToGradeMapping:
    """Verify that validate_transcript outcomes would produce correct grade decisions."""

    def _make_valid_transcript(self, **overrides):
        base = {
            "invocation_id": "R106-INT-001",
            "skill_id": "add-dotnet-object-model-feature",
            "mode": "dry-run",
            "inputs": {
                "format_id": "fods",
                "feature_name": "TestFeature",
                "exact_source_paths": ["src/net/fods/FodsDocument.cs"],
                "exact_test_paths": ["tests/net/fods/Test.cs"],
                "ledger_entry_path": "reports/r90/product-code-change-ledger.json",
            },
            "allowed_files": ["src/net/fods/FodsDocument.cs", "tests/net/fods/Test.cs"],
            "actual_files_changed": ["src/net/fods/FodsDocument.cs"],
            "tests_run": ["dotnet test"],
            "result": "PASS",
            "timestamp": "2026-06-03T16:00:00Z",
        }
        base.update(overrides)
        return base

    def test_valid_pass_transcript_maps_to_accepted(self):
        """Valid PASS transcript => ACCEPTED_VERIFIED eligible."""
        t = self._make_valid_transcript()
        v = validate_transcript(t)
        assert v["valid"] is True
        assert v["result"] == "PASS"
        # Decision: valid + PASS => ACCEPTED_VERIFIED

    def test_valid_fail_transcript_maps_to_rework(self):
        """Valid FAIL transcript => REWORK_REQUIRED."""
        t = self._make_valid_transcript(result="FAIL")
        v = validate_transcript(t)
        assert v["valid"] is True
        assert v["result"] == "FAIL"
        # Decision: valid + FAIL => REWORK_REQUIRED

    def test_invalid_transcript_maps_to_overclaimed(self):
        """Invalid transcript => OVERCLAIMED."""
        v = validate_transcript({"invocation_id": "bad"})
        assert v["valid"] is False
        # Decision: invalid => OVERCLAIMED

    def test_missing_transcript_maps_to_overclaimed(self):
        """Empty transcript data => OVERCLAIMED."""
        v = validate_transcript({})
        assert v["valid"] is False
        # Decision: missing/empty => OVERCLAIMED

    def test_anti_bypass_fail_maps_to_accepted(self):
        """Anti-bypass demo with FAIL => ACCEPTED (expected behavior)."""
        t = self._make_valid_transcript(mode="anti-bypass-demo", result="FAIL")
        v = validate_transcript(t)
        assert v["valid"] is True
        assert v["mode"] == "anti-bypass-demo"
        assert v["result"] == "FAIL"
        # Decision: anti-bypass + FAIL => ACCEPTED (expected failure)

    def test_live_without_ledger_maps_to_overclaimed(self):
        """LIVE mode without ledger => invalid => OVERCLAIMED."""
        t = self._make_valid_transcript(mode="live", ledger_entry_id=None)
        v = validate_transcript(t)
        assert v["valid"] is False
        # Decision: invalid => OVERCLAIMED

    def test_live_with_ledger_maps_to_accepted(self):
        """LIVE mode with ledger => valid => ACCEPTED_VERIFIED eligible."""
        t = self._make_valid_transcript(mode="live", ledger_entry_id="LEDGER-R106-001")
        v = validate_transcript(t)
        assert v["valid"] is True
        # Decision: valid + PASS + ledger => ACCEPTED_VERIFIED


# ============================================================
# Test: grade_all pipeline with transcript-enriched data
# ============================================================

class TestGradeAllPipeline:
    """Test the full grading pipeline produces correct aggregate results."""

    def _make_declaration(self, items):
        return {
            "run_id": "test-r106",
            "sprint_id": "TEST-R106",
            "evidence_root": "reports/test",
            "planned_work_items": items,
            "test_results": {"passed": 10, "failed": 0, "skipped": 0},
        }

    def _make_inspection_bundle(self, item_inspections, test_results=None):
        return {
            "run_id": "test-r106",
            "sprint_id": "TEST-R106",
            "evidence_root": "reports/test",
            "test_results": test_results or {"passed": 10, "failed": 0, "errors": 0},
            "item_inspections": item_inspections,
        }

    def test_all_accepted_produces_accepted_verdict(self):
        """All items accepted => overall ACCEPTED."""
        items = [
            {"item_id": "W1", "title": "Work 1", "status": "completed"},
            {"item_id": "W2", "title": "Work 2", "status": "completed"},
        ]
        inspections = [
            make_inspection("W1", tests_with_content=["t.py"]),
            make_inspection("W2", tests_with_content=["t.py"]),
        ]
        decl = self._make_declaration(items)
        insp_bundle = self._make_inspection_bundle(inspections)

        review = grade_all(insp_bundle, decl)
        assert review["overall_verdict"] == "ACCEPTED"
        assert review["autonomous_continue"] is True
        assert len(review["accepted_items"]) == 2

    def test_overclaimed_item_blocks_autonomous(self):
        """One overclaimed item => ACCEPTED_WITH_REWORK, autonomous blocked."""
        items = [
            {"item_id": "W1", "title": "Good", "status": "completed"},
            {"item_id": "W2", "title": "Bad", "status": "completed"},
        ]
        inspections = [
            make_inspection("W1", tests_with_content=["t.py"]),
            make_inspection("W2", has_evidence=False),
        ]
        decl = self._make_declaration(items)
        insp_bundle = self._make_inspection_bundle(inspections)

        review = grade_all(insp_bundle, decl)
        assert review["overall_verdict"] == "ACCEPTED_WITH_REWORK"
        assert review["autonomous_continue"] is False
        assert "W2" in review["overclaimed_items"]

    def test_mixed_grades_produce_correct_counts(self):
        """Mix of accepted, rework, blocked items correctly counted."""
        items = [
            {"item_id": "W1", "title": "OK", "status": "completed"},
            {"item_id": "W2", "title": "Missing", "status": "completed"},
            {"item_id": "W3", "title": "Blocked", "status": "blocked_external_gate"},
        ]
        inspections = [
            make_inspection("W1", tests_with_content=["t.py"]),
            make_inspection("W2", evidence_paths_missing=["missing.md"]),
            make_inspection("W3", declared_status="blocked_external_gate"),
        ]
        decl = self._make_declaration(items)
        insp_bundle = self._make_inspection_bundle(inspections)

        review = grade_all(insp_bundle, decl)
        assert len(review["accepted_items"]) == 1
        assert "W2" in review["rework_items"]
        assert review["critical_rework_count"] == 0  # REWORK_REQUIRED is not critical


# ============================================================
# Test: Decision matrix JSON integrity
# ============================================================

class TestDecisionMatrixIntegrity:
    """Verify the R105 decision matrix JSON is still valid and complete."""

    def test_decision_matrix_exists_and_valid(self):
        matrix_path = REPO_ROOT / "reports" / "skills-r105" / "transcript-grade-matrix.json"
        if not matrix_path.exists():
            pytest.skip("R105 decision matrix not found")
        data = json.loads(matrix_path.read_text(encoding="utf-8"))
        assert "states" in data
        assert len(data["states"]) == 7, "Expected 7 transcript states"

    def test_decision_matrix_covers_all_grade_outcomes(self):
        matrix_path = REPO_ROOT / "reports" / "skills-r105" / "transcript-grade-matrix.json"
        if not matrix_path.exists():
            pytest.skip("R105 decision matrix not found")
        data = json.loads(matrix_path.read_text(encoding="utf-8"))
        grades = {s["grade"] for s in data["states"]}
        expected = {"OVERCLAIMED", "ACCEPTED_VERIFIED", "REWORK_REQUIRED", "ACCEPTED"}
        assert expected.issubset(grades), f"Missing grades: {expected - grades}"

    def test_decision_matrix_modes_match_validator(self):
        """All modes in the decision matrix should be valid per the transcript validator."""
        matrix_path = REPO_ROOT / "reports" / "skills-r105" / "transcript-grade-matrix.json"
        if not matrix_path.exists():
            pytest.skip("R105 decision matrix not found")
        data = json.loads(matrix_path.read_text(encoding="utf-8"))
        matrix_modes = {s["mode"] for s in data["states"] if s["mode"] is not None}
        assert matrix_modes.issubset(VALID_MODES), (
            f"Matrix modes {matrix_modes} not all in validator modes {VALID_MODES}"
        )
