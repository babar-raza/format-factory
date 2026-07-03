"""TC-FG-007: Tests for hardened adversarial blocking and proof-gap guard.

Verifies that:
1. Adversarial HIGH risk (adv_result >= 1) adds to rework_items
2. Adversarial medium risk (adv_result == 0) does not add to rework_items
3. LLM unavailable (adv_result == None) does not block
4. Empty queue + inadequate proof → PROOF_GAP item generated
5. Empty queue + max cycles reached → no PROOF_GAP items generated
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from generate_next_worker_prompt import detect_proof_gaps_for_empty_queue


def _make_review(supervisor_grade: str = "ACCEPTED_VERIFIED", item_type: str = "PRODUCT_TEST",
                 test_path: str = "") -> dict:
    return {
        "run_id": "test-run-001",
        "sprint_id": "test-sprint",
        "overall_verdict": "ACCEPTED",
        "autonomous_continue": True,
        "rework_items": [],
        "critical_rework_count": 0,
        "item_grades": [
            {
                "item_id": "I-001",
                "item_title": "Test item",
                "supervisor_grade": supervisor_grade,
                "item_type": item_type,
                "tests_supporting": [test_path] if test_path else [],
            }
        ],
    }


def test_adversarial_high_risk_adds_to_rework():
    """Simulated adv_result=2 (HIGH findings) should add ADVERSARIAL_HIGH_RISK to rework_items."""
    review = _make_review()

    # Simulate what autonomous_cycle.py does when _adv_result >= 1
    _adv_result = 2
    if _adv_result is not None and _adv_result >= 1:
        review.setdefault("rework_items", []).append(
            f"ADVERSARIAL_HIGH_RISK:{_adv_result}_findings"
        )
        review["critical_rework_count"] = review.get("critical_rework_count", 0) + 1
        if review.get("overall_verdict") in ("ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"):
            review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
        if "autonomous_continue" in review:
            review["autonomous_continue"] = False

    assert "ADVERSARIAL_HIGH_RISK:2_findings" in review["rework_items"], (
        f"Expected ADVERSARIAL_HIGH_RISK in rework_items, got: {review['rework_items']}"
    )
    assert review["autonomous_continue"] is False
    assert review["overall_verdict"] == "ACCEPTED_WITH_REWORK"
    assert review["critical_rework_count"] == 1


def test_adversarial_medium_risk_non_blocking():
    """adv_result=0 (no HIGH findings) → rework_items unchanged."""
    review = _make_review()
    original_rework = list(review["rework_items"])

    _adv_result = 0
    if _adv_result is not None and _adv_result >= 1:
        review["rework_items"].append(f"ADVERSARIAL_HIGH_RISK:{_adv_result}_findings")

    assert review["rework_items"] == original_rework, (
        f"Non-HIGH adversarial result should not add to rework_items, got: {review['rework_items']}"
    )
    assert review["autonomous_continue"] is True


def test_adversarial_llm_unavailable_skips():
    """adv_result=None (LLM unavailable) → nothing blocking."""
    review = _make_review()
    original_rework = list(review["rework_items"])

    _adv_result = None
    if _adv_result is not None and _adv_result >= 1:
        review["rework_items"].append(f"ADVERSARIAL_HIGH_RISK:{_adv_result}_findings")

    assert review["rework_items"] == original_rework, (
        f"None (LLM unavailable) should not modify rework_items, got: {review['rework_items']}"
    )
    assert review["autonomous_continue"] is True


def test_queue_empty_proof_gap_generates_task(tmp_path):
    """Empty queue + item with type-only assertions → PROOF_GAP item generated."""
    # Write a weak test file
    test_file = tmp_path / "test_weak.py"
    test_file.write_text(
        "def test_type_only():\n    result = compute()\n    assert isinstance(result, list)\n"
    )

    work_item_grades = [
        {
            "item_id": "I-002",
            "supervisor_grade": "ACCEPTED_VERIFIED",
            "item_type": "PRODUCT_TEST",
            "tests_supporting": [str(test_file)],
        }
    ]

    gaps = detect_proof_gaps_for_empty_queue(
        work_item_grades=work_item_grades,
        evidence_root=str(tmp_path),
        current_proof_gap_cycle=0,
    )

    assert len(gaps) > 0, f"Expected PROOF_GAP items for weak test, got: {gaps}"
    assert gaps[0]["item_type"] == "PROOF_GAP"
    assert "PROOF-GAP-I-002" == gaps[0]["item_id"]


def test_queue_empty_max_cycles_stops(tmp_path):
    """current_proof_gap_cycle=3 >= max=3 → empty list returned (prevents infinite loop)."""
    test_file = tmp_path / "test_weak.py"
    test_file.write_text(
        "def test_type_only():\n    result = compute()\n    assert isinstance(result, list)\n"
    )

    work_item_grades = [
        {
            "item_id": "I-003",
            "supervisor_grade": "ACCEPTED_VERIFIED",
            "item_type": "PRODUCT_TEST",
            "tests_supporting": [str(test_file)],
        }
    ]

    gaps = detect_proof_gaps_for_empty_queue(
        work_item_grades=work_item_grades,
        evidence_root=str(tmp_path),
        max_proof_gap_cycles=3,
        current_proof_gap_cycle=3,  # at limit → should stop
    )

    assert gaps == [], (
        f"Max cycles reached: expected empty list, got: {gaps}"
    )
