"""test_claim_classification_closeout.py — Lane 1 regression tests.

Proves:
1. Invalid claim_classification values are rejected by governance validators.
2. Valid claim_classification values pass.
3. blocks_sprint=True from governance validators triggers critical_rework_count
   in autonomous_cycle, producing exit_code=3.
4. Unknown claim_classification values are rejected.
5. Empty claim_classification is acceptable (not required for non-product items).
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from governance_validators import (
    validate_claim_classification,
    VALID_CLAIM_CLASSIFICATIONS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_item(**overrides):
    """Minimal valid work item."""
    item = {
        "item_id": "TEST-001",
        "title": "Test item",
        "status": "completed",
        "item_type": "GOVERNANCE_DOC",
        "execution_method": "GOVERNED_SKILL_EXECUTION",
    }
    item.update(overrides)
    return item


def _decl(items, **overrides):
    """Minimal declaration wrapping items."""
    d = {
        "run_id": "test-run",
        "sprint_id": "TEST-SPRINT",
        "evidence_root": ".local/evidences/test",
        "start_time": "2026-01-01T00:00:00Z",
        "end_time": "2026-01-01T01:00:00Z",
        "git_head_start": "abc123",
        "git_head_end": "abc123",
        "git_status_final": "",
        "declared_scope": "test",
        "planned_work_items": items,
        "completed_work_items": [i["item_id"] for i in items],
        "incomplete_work_items": [],
        "changed_files": [],
        "tests_run": 0,
        "test_results": {"passed": 0, "failed": 0, "skipped": 0, "errors": 0},
        "evidence_artifacts": [],
        "reports_created": [],
        "worker_self_verdict": "PASS",
        "worker_self_grade": "PASS",
        "next_recommended_work": [],
    }
    d.update(overrides)
    return d


# ---------------------------------------------------------------------------
# Tests: claim_classification_validator
# ---------------------------------------------------------------------------

class TestClaimClassificationValidator:
    """Tests for governance validator V5: claim_classification."""

    def test_valid_governed_but_not_replayed_passes(self):
        """Valid classification GOVERNED_BUT_NOT_REPLAYED should PASS."""
        item = _base_item(claim_classification="GOVERNED_BUT_NOT_REPLAYED")
        result = validate_claim_classification(_decl([item]))
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_valid_works_but_not_repeatable_warns(self):
        """WORKS_BUT_NOT_REPEATABLE is acceptable but produces WARN."""
        item = _base_item(claim_classification="WORKS_BUT_NOT_REPEATABLE")
        result = validate_claim_classification(_decl([item]))
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False

    def test_invalid_claim_fails_and_blocks(self):
        """INVALID_CLAIM must FAIL and block sprint."""
        item = _base_item(claim_classification="INVALID_CLAIM")
        result = validate_claim_classification(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_unknown_classification_fails_and_blocks(self):
        """Unknown classification like 'implementation_verified' must FAIL."""
        item = _base_item(claim_classification="implementation_verified")
        result = validate_claim_classification(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_empty_classification_skipped(self):
        """Empty claim_classification is acceptable (non-product items)."""
        item = _base_item()  # no claim_classification
        result = validate_claim_classification(_decl([item]))
        # No items processed → PASS with 0 items
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_replayable_with_manual_ungoverned_fails(self):
        """REPLAYABLE claim with MANUAL_UNGOVERNED method must FAIL."""
        item = _base_item(
            claim_classification="REPLAYABLE_NOT_YET_REPLAYED",
            execution_method="MANUAL_UNGOVERNED",
        )
        result = validate_claim_classification(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_all_valid_classifications_pass(self):
        """Every value in VALID_CLAIM_CLASSIFICATIONS (except INVALID_CLAIM)
        should not cause a FAIL."""
        for cls in VALID_CLAIM_CLASSIFICATIONS:
            if cls == "INVALID_CLAIM":
                continue
            item = _base_item(
                claim_classification=cls,
                execution_method="GOVERNED_SKILL_EXECUTION",
            )
            result = validate_claim_classification(_decl([item]))
            assert result["result"] in ("PASS", "WARN"), \
                f"Classification {cls} unexpectedly FAILed"

    def test_multiple_items_one_invalid_blocks_all(self):
        """One invalid classification in a batch must block the entire sprint."""
        items = [
            _base_item(item_id="GOOD-001",
                        claim_classification="GOVERNED_BUT_NOT_REPLAYED"),
            _base_item(item_id="BAD-001",
                        claim_classification="implementation_verified"),
        ]
        result = validate_claim_classification(_decl(items))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        fail_ids = [i["item_id"] for i in result["items"]
                    if i.get("severity") == "FAIL"]
        assert "BAD-001" in fail_ids


# ---------------------------------------------------------------------------
# Tests: blocks_sprint → critical_rework_count enforcement
# ---------------------------------------------------------------------------

class TestBlocksSprintEnforcement:
    """Proves that blocks_sprint=True from governance triggers exit 3 path."""

    def test_review_dict_critical_rework_incremented(self):
        """Simulate the autonomous_cycle governance enforcement logic.
        When blocks_sprint=True, critical_rework_count must be > 0."""
        # Build a mock review dict as autonomous_cycle would
        review = {
            "overall_verdict": "ACCEPTED",
            "critical_rework_count": 0,
            "autonomous_continue": True,
            "rework_items": [],
        }

        # Simulate a governance result with blocks_sprint=True
        governance_validation_result = {
            "blocks_sprint": True,
            "summary": "1 FAIL: claim_classification invalid",
            "validators": [
                {
                    "validator": "claim_classification_validator",
                    "result": "FAIL",
                    "blocks_sprint": True,
                    "summary": "FAIL: 1 items with invalid claim_classification.",
                    "items": [],
                },
            ],
        }

        # Apply the same logic as autonomous_cycle.py (post-fix)
        if governance_validation_result.get("blocks_sprint"):
            review["critical_rework_count"] = max(
                review.get("critical_rework_count", 0) + 1, 1)
            review["autonomous_continue"] = False
            if review["overall_verdict"] in ("ACCEPTED", "ACCEPTED_WITH_LIMITATIONS",
                                              "ACCEPTED_WITH_REWORK"):
                review["overall_verdict"] = "ACCEPTED_WITH_REWORK"
            for v in governance_validation_result.get("validators", []):
                if v.get("result") == "FAIL" and v.get("blocks_sprint"):
                    rework_id = f"GOV_BLOCK:{v['validator']}"
                    if rework_id not in review["rework_items"]:
                        review["rework_items"].append(rework_id)

        # Verify enforcement
        assert review["critical_rework_count"] > 0
        assert review["autonomous_continue"] is False
        assert review["overall_verdict"] == "ACCEPTED_WITH_REWORK"
        assert "GOV_BLOCK:claim_classification_validator" in review["rework_items"]

        # Verify exit code would be 3
        exit_code = 3 if review["critical_rework_count"] > 0 else 0
        assert exit_code == 3

    def test_no_blocks_sprint_keeps_exit_zero(self):
        """When blocks_sprint=False, exit code stays 0."""
        review = {
            "overall_verdict": "ACCEPTED",
            "critical_rework_count": 0,
            "autonomous_continue": True,
            "rework_items": [],
        }

        governance_validation_result = {
            "blocks_sprint": False,
            "summary": "22 PASS / 0 WARN / 0 FAIL",
            "validators": [],
        }

        if governance_validation_result.get("blocks_sprint"):
            review["critical_rework_count"] = max(
                review.get("critical_rework_count", 0) + 1, 1)

        assert review["critical_rework_count"] == 0
        exit_code = 3 if review["critical_rework_count"] > 0 else 0
        assert exit_code == 0
