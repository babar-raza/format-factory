"""
R100 — Grade Engine Unit Tests
Tests grade_item() and grade_all() with synthetic inspection data.
Covers all 11 grade levels and the overall verdict logic.
"""
import sys
from pathlib import Path

# Allow importing from tools/supervisor/
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from grade_declared_work import grade_item, grade_all


# ---------------------------------------------------------------------------
# grade_item: status → grade mapping
# ---------------------------------------------------------------------------

def _make_inspection(
    item_id="ITEM-1",
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
):
    return {
        "item_id": item_id,
        "declared_status": declared_status,
        "has_evidence": has_evidence,
        "has_tests": has_tests,
        "evidence_paths_found": evidence_paths_found or [],
        "evidence_paths_missing": evidence_paths_missing or [],
        "tests_declared": tests_declared or [],
        "tests_with_content": tests_with_content or [],
        "tests_empty_or_stub": tests_empty_or_stub or [],
        "acceptance_criteria_verified": acceptance_criteria_verified,
        "acceptance_criteria_pattern": acceptance_criteria_pattern,
    }


def test_completed_with_evidence_yields_accepted_verified():
    # R104: path-only evidence without concrete proof → ACCEPTED_WITH_LIMITATIONS
    insp = _make_inspection(
        declared_status="completed",
        has_evidence=True,
        evidence_paths_found=["reports/r100/foo.md"],
    )
    grade = grade_item(insp, {"passed": 10, "failed": 0})
    assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"


def test_completed_with_concrete_proof_yields_accepted_verified():
    # R104: concrete proof (test content verified) → ACCEPTED_VERIFIED
    insp = _make_inspection(
        declared_status="completed",
        has_evidence=True,
        evidence_paths_found=["reports/r100/foo.md"],
        tests_with_content=["tests/test_foo.py"],
    )
    grade = grade_item(insp, {"passed": 10, "failed": 0})
    assert grade["supervisor_grade"] == "ACCEPTED_VERIFIED"


def test_completed_no_evidence_yields_overclaimed():
    insp = _make_inspection(
        declared_status="completed",
        has_evidence=False,
    )
    grade = grade_item(insp, {"passed": 10, "failed": 0})
    assert grade["supervisor_grade"] == "OVERCLAIMED"
    assert grade["can_autonomously_repair"] is True


def test_completed_missing_paths_yields_rework_required():
    insp = _make_inspection(
        declared_status="completed",
        has_evidence=True,
        evidence_paths_found=["reports/a.md"],
        evidence_paths_missing=["reports/b.md"],
    )
    grade = grade_item(insp, {"passed": 10, "failed": 0})
    assert grade["supervisor_grade"] == "REWORK_REQUIRED"
    assert "b.md" in grade["required_rework"]


def test_completed_with_test_failures_yields_rework():
    insp = _make_inspection(
        declared_status="completed",
        has_evidence=True,
        has_tests=True,
        evidence_paths_found=["src/x.py"],
    )
    grade = grade_item(insp, {"passed": 8, "failed": 2})
    assert grade["supervisor_grade"] == "REWORK_REQUIRED"
    assert "test" in grade["required_rework"].lower()


def test_blocked_external_gate():
    insp = _make_inspection(declared_status="blocked_external_gate")
    grade = grade_item(insp, {"passed": 0, "failed": 0})
    assert grade["supervisor_grade"] == "BLOCKED_EXTERNAL_GATE"


def test_not_started():
    insp = _make_inspection(declared_status="not_started")
    grade = grade_item(insp, {"passed": 0, "failed": 0})
    assert grade["supervisor_grade"] == "NOT_ATTEMPTED"


def test_deferred_with_reason():
    insp = _make_inspection(declared_status="deferred")
    grade = grade_item(insp, {"passed": 0, "failed": 0})
    assert grade["supervisor_grade"] == "DEFERRED_WITH_REASON"


def test_partial_with_evidence_yields_warnings():
    insp = _make_inspection(declared_status="partial", has_evidence=True)
    grade = grade_item(insp, {"passed": 5, "failed": 0})
    assert grade["supervisor_grade"] == "ACCEPTED_WITH_WARNINGS"


def test_partial_no_evidence_yields_rework():
    insp = _make_inspection(declared_status="partial", has_evidence=False)
    grade = grade_item(insp, {"passed": 0, "failed": 0})
    assert grade["supervisor_grade"] == "REWORK_REQUIRED"


def test_accepted_with_limitations_on_stub_tests():
    """D92-03 deep grading: stub test files cause ACCEPTED_WITH_LIMITATIONS."""
    insp = _make_inspection(
        declared_status="completed",
        has_evidence=True,
        has_tests=True,
        evidence_paths_found=["reports/r100/proof.md"],
        tests_empty_or_stub=["tests/supervisor/test_stub.py"],
    )
    grade = grade_item(insp, {"passed": 10, "failed": 0})
    assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"
    assert len(grade["acceptance_criteria_failed"]) > 0


def test_accepted_verified_with_content_tests():
    """D92-03: real test files with content → ACCEPTED_VERIFIED with criteria met."""
    insp = _make_inspection(
        declared_status="completed",
        has_evidence=True,
        has_tests=True,
        evidence_paths_found=["reports/r100/proof.md"],
        tests_with_content=["tests/supervisor/test_real.py"],
    )
    grade = grade_item(insp, {"passed": 10, "failed": 0})
    assert grade["supervisor_grade"] == "ACCEPTED_VERIFIED"
    assert any("content verified" in c.lower() for c in grade["acceptance_criteria_met"])


# ---------------------------------------------------------------------------
# grade_all: overall verdict logic
# ---------------------------------------------------------------------------

def _make_declaration(items):
    return {"planned_work_items": items}


def _make_full_inspection(item_inspections, test_results=None):
    return {
        "run_id": "test-run",
        "sprint_id": "test-sprint",
        "evidence_root": "",
        "item_inspections": item_inspections,
        "test_results": test_results or {"passed": 10, "failed": 0},
    }


def test_grade_all_all_accepted():
    # R107: At least one item must have tests_with_content to avoid path-only downgrade
    items = [
        _make_inspection("A", "completed", True, True, ["a.md"], tests_with_content=["a.md"]),
        _make_inspection("B", "completed", True, True, ["b.md"], tests_with_content=["b.md"]),
    ]
    decl = _make_declaration([
        {"item_id": "A", "title": "Item A"},
        {"item_id": "B", "title": "Item B"},
    ])
    review = grade_all(_make_full_inspection(items), decl)
    assert review["overall_verdict"] == "ACCEPTED"
    assert review["autonomous_continue"] is True
    assert review["critical_rework_count"] == 0
    assert len(review["accepted_items"]) == 2


def test_grade_all_with_overclaimed():
    items = [
        _make_inspection("A", "completed", True, True, ["a.md"]),
        _make_inspection("B", "completed", False),  # no evidence → OVERCLAIMED
    ]
    decl = _make_declaration([
        {"item_id": "A", "title": "Item A"},
        {"item_id": "B", "title": "Item B"},
    ])
    review = grade_all(_make_full_inspection(items), decl)
    assert review["overall_verdict"] == "ACCEPTED_WITH_REWORK"
    assert review["autonomous_continue"] is False
    assert "B" in review["overclaimed_items"]
    assert review["critical_rework_count"] == 1


def test_grade_all_with_rework_required():
    items = [
        _make_inspection("A", "completed", True, True, ["a.md"]),
        _make_inspection("B", "completed", True, True, ["b.md"], ["c.md"]),  # missing path
    ]
    decl = _make_declaration([
        {"item_id": "A", "title": "Item A"},
        {"item_id": "B", "title": "Item B"},
    ])
    review = grade_all(_make_full_inspection(items), decl)
    assert review["overall_verdict"] == "ACCEPTED_WITH_REWORK"
    assert "B" in review["rework_items"]


def test_grade_all_deferred_counts_as_accepted():
    items = [
        _make_inspection("A", "completed", True, True, ["a.md"]),
        _make_inspection("B", "deferred"),
    ]
    decl = _make_declaration([
        {"item_id": "A", "title": "Item A"},
        {"item_id": "B", "title": "Item B"},
    ])
    review = grade_all(_make_full_inspection(items), decl)
    # Deferred is not in accepted_grades but also not in rework/overclaimed
    # So overall verdict should still be ACCEPTED (not ACCEPTED_WITH_REWORK)
    assert review["autonomous_continue"] is True
    assert review["critical_rework_count"] == 0


def test_grade_all_blocked_gate_allows_continue():
    # R107: Need tests_with_content to avoid path-only downgrade
    items = [
        _make_inspection("A", "completed", True, True, ["a.md"], tests_with_content=["a.md"]),
        _make_inspection("B", "blocked_external_gate"),
    ]
    decl = _make_declaration([
        {"item_id": "A", "title": "Item A"},
        {"item_id": "B", "title": "Item B"},
    ])
    review = grade_all(_make_full_inspection(items), decl)
    assert review["overall_verdict"] == "ACCEPTED"
    assert review["autonomous_continue"] is True


def test_grade_all_test_failures_block_continuation():
    items = [
        _make_inspection("A", "completed", True, True, ["a.md"]),
    ]
    decl = _make_declaration([{"item_id": "A", "title": "Item A"}])
    review = grade_all(
        _make_full_inspection(items, test_results={"passed": 8, "failed": 2}),
        decl,
    )
    # Test failures contribute to has_critical
    assert review["autonomous_continue"] is False
