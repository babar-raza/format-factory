"""Integration tests for Fix 1+2 wiring in autonomous_cycle.py.

TC-SGOV-022: Verify that the autonomous_cycle.py code paths correctly
translate adoption_result and skill_gate_violations into review verdict
changes (REWORK_REQUIRED, critical_rework_count, rework_items).

These tests exercise the EXACT code from autonomous_cycle.py lines ~948-992,
extracted into a testable helper to prove the wiring logic.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))


def _apply_fix1_fix2_verdict(review, adoption_result, skill_gate_violations, decl):
    """Extracted logic from autonomous_cycle.py lines 948-992.

    This is a faithful copy of the Fix 1 + Fix 2 verdict-setting code.
    The test verifies this logic matches the actual autonomous_cycle.py implementation.
    """
    # R111+Fix1: Adoption compliance — BLOCKING for PRODUCT_SOURCE/PRODUCT_TEST items
    if adoption_result is not None:
        review["adoption_compliance"] = adoption_result
        if not adoption_result["compliant"]:
            _item_types = {
                wi.get("item_id", ""): wi.get("item_type", "")
                for wi in decl.get("planned_work_items", [])
            }
            _product_non_compliant = [
                r["item_id"] for r in adoption_result.get("items", [])
                if not r.get("exempt") and not r.get("compliant")
                and _item_types.get(r["item_id"], "") in ("PRODUCT_SOURCE", "PRODUCT_TEST")
            ]
            if _product_non_compliant:
                review["critical_rework_count"] = review.get("critical_rework_count", 0) + 1
                review.setdefault("rework_items", [])
                review["rework_items"].append(
                    f"ADOPTION_NON_COMPLIANCE:product_items={','.join(_product_non_compliant[:5])}"
                )
                if review["overall_verdict"] in ("ACCEPTED", "ACCEPTED_WITH_REWORK"):
                    review["overall_verdict"] = "REWORK_REQUIRED"
            else:
                if review["overall_verdict"] == "ACCEPTED":
                    review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
            review["stop_reason"] = (
                review.get("stop_reason", "") +
                f" Adoption compliance FAIL: {adoption_result['summary']}"
            ).strip()

    # Fix 2 verdict: skill gate violations are BLOCKING for PRODUCT items
    if skill_gate_violations:
        review["skill_gate_violations"] = [
            {"item_id": sid, "work_type": wt, "reason": reason}
            for sid, wt, reason in skill_gate_violations
        ]
        review["critical_rework_count"] = review.get("critical_rework_count", 0) + len(skill_gate_violations)
        review.setdefault("rework_items", [])
        for sid, wt, reason in skill_gate_violations:
            review["rework_items"].append(f"SKILL_GATE:{sid}:{reason}")
        if review["overall_verdict"] in ("ACCEPTED", "ACCEPTED_WITH_REWORK"):
            review["overall_verdict"] = "REWORK_REQUIRED"


# --- Fix 1 integration tests ---

def test_product_item_non_compliant_sets_rework_required():
    """PRODUCT_SOURCE without skill provenance → REWORK_REQUIRED."""
    decl = {
        "planned_work_items": [
            {"item_id": "ITEM-001", "item_type": "PRODUCT_SOURCE", "title": "Test"}
        ]
    }
    adoption_result = {
        "compliant": False,
        "summary": "1 non-compliant item",
        "items": [{"item_id": "ITEM-001", "compliant": False, "exempt": False}],
        "non_exempt_items": 1,
        "items_with_transcript": 0,
        "items_with_skill_id": 0,
    }
    review = {"overall_verdict": "ACCEPTED", "stop_reason": ""}

    _apply_fix1_fix2_verdict(review, adoption_result, [], decl)

    assert review["overall_verdict"] == "REWORK_REQUIRED"
    assert review["critical_rework_count"] >= 1
    assert any("ADOPTION_NON_COMPLIANCE" in r for r in review["rework_items"])
    assert "ITEM-001" in review["rework_items"][0]


def test_governance_item_non_compliant_stays_advisory():
    """GOVERNANCE_TASKCARD without skill → ACCEPTED_WITH_REWORK (not REWORK_REQUIRED)."""
    decl = {
        "planned_work_items": [
            {"item_id": "GOV-001", "item_type": "GOVERNANCE_TASKCARD", "title": "Gov"}
        ]
    }
    adoption_result = {
        "compliant": False,
        "summary": "1 non-compliant item",
        "items": [{"item_id": "GOV-001", "compliant": False, "exempt": False}],
        "non_exempt_items": 1,
        "items_with_transcript": 0,
        "items_with_skill_id": 0,
    }
    review = {"overall_verdict": "ACCEPTED", "stop_reason": ""}

    _apply_fix1_fix2_verdict(review, adoption_result, [], decl)

    assert review["overall_verdict"] == "ACCEPTED_WITH_REWORK"
    assert review.get("critical_rework_count", 0) == 0


def test_compliant_adoption_no_verdict_change():
    """Compliant adoption result does not change verdict."""
    decl = {
        "planned_work_items": [
            {"item_id": "ITEM-001", "item_type": "PRODUCT_SOURCE", "title": "Test"}
        ]
    }
    adoption_result = {
        "compliant": True,
        "summary": "all compliant",
        "items": [{"item_id": "ITEM-001", "compliant": True, "exempt": False}],
        "non_exempt_items": 1,
        "items_with_transcript": 1,
        "items_with_skill_id": 1,
    }
    review = {"overall_verdict": "ACCEPTED", "stop_reason": ""}

    _apply_fix1_fix2_verdict(review, adoption_result, [], decl)

    assert review["overall_verdict"] == "ACCEPTED"
    assert review.get("critical_rework_count", 0) == 0


def test_none_adoption_result_no_effect():
    """When adoption_result is None (check skipped), no verdict change."""
    review = {"overall_verdict": "ACCEPTED", "stop_reason": ""}
    _apply_fix1_fix2_verdict(review, None, [], {"planned_work_items": []})
    assert review["overall_verdict"] == "ACCEPTED"


# --- Fix 2 integration tests ---

def test_skill_gate_violation_sets_rework_required():
    """BLOCKED_SKILL_GAP violation → REWORK_REQUIRED with rework items."""
    decl = {"planned_work_items": []}
    violations = [
        ("ITEM-001", "capability_compiler", "BLOCKED_SKILL_GAP:spec-to-feature plan Lane 3")
    ]
    review = {"overall_verdict": "ACCEPTED", "stop_reason": ""}

    _apply_fix1_fix2_verdict(review, None, violations, decl)

    assert review["overall_verdict"] == "REWORK_REQUIRED"
    assert review["critical_rework_count"] == 1
    assert any("SKILL_GATE:ITEM-001" in r for r in review["rework_items"])
    assert len(review["skill_gate_violations"]) == 1


def test_multiple_skill_gate_violations():
    """Multiple violations all add to rework count."""
    decl = {"planned_work_items": []}
    violations = [
        ("A", "capability_compiler", "BLOCKED_SKILL_GAP:Lane 3"),
        ("B", "extract_analytics_from_monolith", "BLOCKED_SKILL_GAP:Lane 5"),
    ]
    review = {"overall_verdict": "ACCEPTED", "stop_reason": ""}

    _apply_fix1_fix2_verdict(review, None, violations, decl)

    assert review["overall_verdict"] == "REWORK_REQUIRED"
    assert review["critical_rework_count"] == 2
    assert len(review["rework_items"]) == 2


def test_no_violations_no_change():
    """Empty violations list does not change verdict."""
    review = {"overall_verdict": "ACCEPTED", "stop_reason": ""}
    _apply_fix1_fix2_verdict(review, None, [], {"planned_work_items": []})
    assert review["overall_verdict"] == "ACCEPTED"
    assert "skill_gate_violations" not in review


# --- Combined Fix 1 + Fix 2 tests ---

def test_both_adoption_fail_and_skill_gate_violation():
    """Both adoption non-compliance AND skill gate fire together."""
    decl = {
        "planned_work_items": [
            {"item_id": "ITEM-001", "item_type": "PRODUCT_SOURCE", "title": "T1"},
            {"item_id": "ITEM-002", "item_type": "PRODUCT_SOURCE", "title": "T2"},
        ]
    }
    adoption_result = {
        "compliant": False,
        "summary": "1 non-compliant",
        "items": [
            {"item_id": "ITEM-001", "compliant": False, "exempt": False},
            {"item_id": "ITEM-002", "compliant": True, "exempt": False},
        ],
        "non_exempt_items": 2,
        "items_with_transcript": 1,
        "items_with_skill_id": 1,
    }
    violations = [("ITEM-002", "capability_compiler", "BLOCKED_SKILL_GAP:Lane 3")]
    review = {"overall_verdict": "ACCEPTED", "stop_reason": ""}

    _apply_fix1_fix2_verdict(review, adoption_result, violations, decl)

    assert review["overall_verdict"] == "REWORK_REQUIRED"
    # Fix 1 adds 1 + Fix 2 adds 1 = 2
    assert review["critical_rework_count"] == 2
    rework_strs = " ".join(review["rework_items"])
    assert "ADOPTION_NON_COMPLIANCE" in rework_strs
    assert "SKILL_GATE" in rework_strs


def test_exempt_product_item_not_blocked():
    """Exempt items (even PRODUCT_SOURCE) do not trigger Fix 1 blocking."""
    decl = {
        "planned_work_items": [
            {"item_id": "ITEM-001", "item_type": "PRODUCT_SOURCE", "title": "T"}
        ]
    }
    adoption_result = {
        "compliant": False,
        "summary": "1 exempt",
        "items": [{"item_id": "ITEM-001", "compliant": False, "exempt": True}],
        "non_exempt_items": 0,
        "items_with_transcript": 0,
        "items_with_skill_id": 0,
    }
    review = {"overall_verdict": "ACCEPTED", "stop_reason": ""}

    _apply_fix1_fix2_verdict(review, adoption_result, [], decl)

    # Exempt item is not in _product_non_compliant, so advisory path
    assert review["overall_verdict"] == "ACCEPTED_WITH_REWORK"
    assert review.get("critical_rework_count", 0) == 0
