"""TC-C3-001: Regression tests for grading timeout fix for spec-parity claims.

Verifies that PRODUCT_SOURCE items claiming spec-parity do NOT receive
benefit-of-doubt when the LLM grader is unavailable (confidence == 0.0 / timeout).

Non-spec-parity items and TEST items must still receive ACCEPTED_WITH_LIMITATIONS
(existing behaviour preserved).
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

import grade_declared_work as gdw


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_inspection(item_id, evidence_paths=None):
    """Minimal item inspection dict with all paths 'found'."""
    paths = evidence_paths or [f"tests/supervisor/fixtures/{item_id}_proof.py"]
    return {
        "item_id": item_id,
        "declared_status": "completed",
        "has_evidence": True,
        "missing_paths": [],
        "found_paths": paths,
        "evidence_paths_found": paths,
        "has_tests": True,
        "test_failed": False,
        "tests_with_content": paths,
        "tests_empty_or_stub": [],
        "acceptance_criteria_verified": True,
        "acceptance_criteria_pattern": "",
        "transcript_validation": None,
    }


def _make_declaration_item(item_id, item_type, acceptance_criteria, evidence_paths=None):
    paths = evidence_paths or [f"tests/supervisor/fixtures/{item_id}_proof.py"]
    return {
        "item_id": item_id,
        "title": f"Test: {item_id}",
        "item_type": item_type,
        "status": "completed",
        "acceptance_criteria": acceptance_criteria,
        "evidence_paths": paths,
        "spec_fact_refs": ["FACT-FODS-001"],
    }


def _grade_single_item(item_id, item_type, acceptance_criteria):
    """Run grade_all on a single item with LLM patched to be unavailable."""
    inspection = {
        "run_id": "test",
        "sprint_id": "test",
        "evidence_root": "",
        "test_results": {"passed": 1, "failed": 0},
        "raw_log_found": False,
        "sample_outputs_found": False,
        "item_inspections": [_make_inspection(item_id)],
        "_repo_root": str(_REPO),
    }
    declaration = {
        "_repo_root": str(_REPO),
        "planned_work_items": [
            _make_declaration_item(item_id, item_type, acceptance_criteria)
        ],
    }

    # Patch LLM to simulate unavailable (returns llm_used=False, confidence=0.0)
    original_sv = gdw.semantic_verify_item

    def _sv_unavailable(ii, decl_item, repo_root, cache_path=None):
        return {
            "adequate": False,
            "confidence": 0.0,
            "stub_detected": False,
            "deficiencies": ["llm_verification_unavailable"],
            "llm_used": False,
            "source": "fallback_llm_unavailable",
        }

    gdw.semantic_verify_item = _sv_unavailable
    try:
        result = gdw.grade_all(inspection, declaration)
    finally:
        gdw.semantic_verify_item = original_sv

    return result


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

class TestSpecParityDeferredOnTimeout:
    """TC-C3-001: spec-parity PRODUCT_SOURCE items deferred on LLM timeout."""

    def test_spec_qname_keyword_deferred(self):
        """PRODUCT_SOURCE with 'spec_qname' in acceptance_criteria → DEFERRED_WITH_REASON."""
        result = _grade_single_item(
            "TEST-SPEC-001",
            "PRODUCT_SOURCE",
            "Class must have spec_qname = 'table:table' matching ODF spec.",
        )
        grades = result["item_grades"]
        assert len(grades) == 1, f"Expected 1 grade, got {len(grades)}"
        grade = grades[0]
        assert grade["supervisor_grade"] == "DEFERRED_WITH_REASON", (
            f"Expected DEFERRED_WITH_REASON for spec_qname claim, got {grade['supervisor_grade']!r}"
        )
        assert "grading_timeout_on_spec_claim" in grade.get("required_rework", ""), (
            "required_rework must mention grading_timeout_on_spec_claim"
        )
        assert grade["item_id"] in result.get("deferred_items", []), (
            "Item must appear in review['deferred_items']"
        )

    def test_spec_parity_keyword_deferred(self):
        """PRODUCT_SOURCE with 'spec_parity' in acceptance_criteria → DEFERRED_WITH_REASON."""
        result = _grade_single_item(
            "TEST-SPEC-002",
            "PRODUCT_SOURCE",
            "Must achieve full spec_parity with ODF table namespace.",
        )
        grade = result["item_grades"][0]
        assert grade["supervisor_grade"] == "DEFERRED_WITH_REASON", (
            f"Expected DEFERRED_WITH_REASON for spec_parity claim, got {grade['supervisor_grade']!r}"
        )

    def test_canonical_class_keyword_deferred(self):
        """PRODUCT_SOURCE with 'canonical_class' in acceptance_criteria → DEFERRED_WITH_REASON."""
        result = _grade_single_item(
            "TEST-SPEC-003",
            "PRODUCT_SOURCE",
            "Implement canonical_class Table.Table with correct QName mapping.",
        )
        grade = result["item_grades"][0]
        assert grade["supervisor_grade"] == "DEFERRED_WITH_REASON", (
            f"Expected DEFERRED_WITH_REASON for canonical_class claim, got {grade['supervisor_grade']!r}"
        )

    def test_deferred_item_not_in_rework_items(self):
        """DEFERRED_WITH_REASON items must NOT appear in rework_items — no rework taskcard."""
        result = _grade_single_item(
            "TEST-SPEC-004",
            "PRODUCT_SOURCE",
            "Implement spec_qname = 'table:table-row'.",
        )
        grade = result["item_grades"][0]
        assert grade["supervisor_grade"] == "DEFERRED_WITH_REASON"
        assert "TEST-SPEC-004" not in result.get("rework_items", []), (
            "DEFERRED items must not appear in rework_items — they are not rework, they are deferred"
        )
        assert "TEST-SPEC-004" not in result.get("accepted_items", []), (
            "DEFERRED items must not appear in accepted_items"
        )
        # Autonomous continuation must not be blocked by deferred items
        assert result["autonomous_continue"] is True, (
            "DEFERRED items alone must not block autonomous_continue"
        )


class TestNonSpecParityPreservesExistingBehavior:
    """Non-spec-parity items and non-PRODUCT items must NOT be deferred on LLM timeout."""

    def test_product_source_without_spec_parity_keeps_grade(self):
        """PRODUCT_SOURCE without spec-parity keywords → keeps ACCEPTED_WITH_LIMITATIONS."""
        result = _grade_single_item(
            "TEST-NOSPEC-001",
            "PRODUCT_SOURCE",
            "Function must return correct count of rows.",
        )
        grade = result["item_grades"][0]
        assert grade["supervisor_grade"] != "DEFERRED_WITH_REASON", (
            f"Non-spec-parity item must NOT be deferred; got {grade['supervisor_grade']!r}"
        )
        # Should be some form of accepted (no LLM available, so deterministic grade)
        assert grade["supervisor_grade"] in (
            "ACCEPTED_VERIFIED", "ACCEPTED_WITH_LIMITATIONS", "ACCEPTED_WITH_WARNINGS", "UNVERIFIED",
        ), f"Expected accepted grade, got {grade['supervisor_grade']!r}"

    def test_product_test_item_not_deferred(self):
        """PRODUCT_TEST items with spec-parity keywords → NOT deferred (only PRODUCT_SOURCE is affected)."""
        result = _grade_single_item(
            "TEST-PTEST-001",
            "PRODUCT_TEST",
            "Test must verify spec_qname = 'table:table' is present.",
        )
        grade = result["item_grades"][0]
        assert grade["supervisor_grade"] != "DEFERRED_WITH_REASON", (
            f"PRODUCT_TEST items must NOT be deferred; got {grade['supervisor_grade']!r}"
        )

    def test_governance_taskcard_not_deferred(self):
        """GOVERNANCE_TASKCARD items → NOT deferred regardless of keywords."""
        result = _grade_single_item(
            "TEST-GOV-001",
            "GOVERNANCE_TASKCARD",
            "Update spec_parity matrix for FODS format.",
        )
        grade = result["item_grades"][0]
        assert grade["supervisor_grade"] != "DEFERRED_WITH_REASON", (
            f"GOVERNANCE items must NOT be deferred; got {grade['supervisor_grade']!r}"
        )


class TestStructuralC3CodePresent:
    """Verify C3 code structure is present in grade_declared_work.py."""

    def test_spec_parity_keywords_defined(self):
        """grade_declared_work.py must reference the three spec-parity trigger keywords."""
        src = Path(_REPO / "tools" / "supervisor" / "grade_declared_work.py").read_text(encoding="utf-8")
        assert "spec_qname" in src, "spec_qname trigger keyword missing from grade_declared_work.py"
        assert "spec_parity" in src, "spec_parity trigger keyword missing from grade_declared_work.py"
        assert "canonical_class" in src, "canonical_class trigger keyword missing from grade_declared_work.py"

    def test_deferred_items_in_review_output(self):
        """grade_all() must include 'deferred_items' key in its return dict."""
        result = _grade_single_item(
            "TEST-STRUCT-001",
            "PRODUCT_SOURCE",
            "spec_qname claim",
        )
        assert "deferred_items" in result, (
            "grade_all() must return 'deferred_items' field in review dict"
        )

    def test_grading_timeout_note_in_required_rework(self):
        """DEFERRED items must have 'grading_timeout_on_spec_claim' in required_rework."""
        result = _grade_single_item(
            "TEST-STRUCT-002",
            "PRODUCT_SOURCE",
            "Must implement canonical_class with spec_qname mapping.",
        )
        grade = result["item_grades"][0]
        assert grade["supervisor_grade"] == "DEFERRED_WITH_REASON"
        assert "grading_timeout_on_spec_claim" in grade.get("required_rework", ""), (
            "required_rework must contain 'grading_timeout_on_spec_claim' for DEFERRED spec items"
        )
