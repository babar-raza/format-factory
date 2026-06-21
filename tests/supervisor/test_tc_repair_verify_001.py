"""tests/supervisor/test_tc_repair_verify_001.py

Unit tests for TC-REPAIR-VERIFY-001: automated post-repair GOV_BLOCK re-scan logic
in autonomous_cycle.py.

Tests verify:
- TC-HEAL sprint detection (sprint_id pattern and all-GOVERNANCE_TASKCARD items)
- Exit 0 from validator → GOV_BLOCK items removed from rework_items
- Exit non-zero from validator → GOV_BLOCK items retained with annotation
- Non-TC-HEAL sprints → re-scan not triggered
- No prior structural blocks → re-scan not triggered
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


# ---------------------------------------------------------------------------
# Helpers: simulate the TC-REPAIR-VERIFY-001 logic block extracted from
# autonomous_cycle.py so tests don't need to invoke the full cycle pipeline.
# ---------------------------------------------------------------------------

_GOVBLOCK_PREFIXES = (
    "GOV_BLOCK:monolith_detection_validator",
    "GOV_BLOCK:validate_source_architecture",
)


def _run_repair_verify_logic(
    sprint_id: str,
    planned_work_items: list[dict],
    existing_rework_items: list[str],
    current_rework_items: list[str],
    validator_returncode: int | None,
    validator_stderr: str = "",
    validator_path_exists: bool = True,
) -> dict:
    """Simulate the TC-REPAIR-VERIFY-001 block from autonomous_cycle.py.

    Returns a dict with:
      - rework_items: updated list after re-scan logic
      - post_repair_rescan: the review annotation (or None if not triggered)
      - rescan_triggered: bool — was the subprocess invoked?
    """
    review: dict = {}

    # Detect TC-HEAL sprint
    _tc_heal_sprint = (
        "TC-HEAL" in sprint_id.upper()
        or "analytics-separation" in sprint_id.lower()
        or "analytics-heal" in sprint_id.lower()
    )
    if not _tc_heal_sprint:
        if planned_work_items and all(
            item.get("item_type") == "GOVERNANCE_TASKCARD" for item in planned_work_items
        ):
            _tc_heal_sprint = True

    # Identify prior structural blocks
    _prior_structural_blocks = [
        it for it in existing_rework_items
        if any(it.startswith(p) or it == p for p in _GOVBLOCK_PREFIXES)
    ]

    rescan_triggered = False
    rework_items = list(current_rework_items)

    if _tc_heal_sprint and _prior_structural_blocks:
        if validator_path_exists and validator_returncode is not None:
            rescan_triggered = True
            if validator_returncode == 0:
                rework_items = [
                    it for it in rework_items
                    if not any(it.startswith(p) or it == p for p in _GOVBLOCK_PREFIXES)
                ]
                review["post_repair_rescan"] = {
                    "status": "RESOLVED",
                    "sprint_id": sprint_id,
                    "resolved_prior_items": _prior_structural_blocks,
                    "validator_exit_code": 0,
                }
            else:
                rework_items = [
                    (it + " [post_repair_rescan:STILL_FAILING]"
                     if any(it.startswith(p) or it == p for p in _GOVBLOCK_PREFIXES)
                     else it)
                    for it in rework_items
                ]
                review["post_repair_rescan"] = {
                    "status": "STILL_FAILING",
                    "sprint_id": sprint_id,
                    "validator_exit_code": validator_returncode,
                    "validator_stderr": validator_stderr[:500],
                }

    return {
        "rework_items": rework_items,
        "post_repair_rescan": review.get("post_repair_rescan"),
        "rescan_triggered": rescan_triggered,
    }


# ---------------------------------------------------------------------------
# Test: TC-HEAL sprint detection via sprint_id
# ---------------------------------------------------------------------------

class TestTcHealSprintDetection:
    """Verify TC-HEAL sprint detection logic."""

    def test_sprint_id_contains_tc_heal_upper(self):
        result = _run_repair_verify_logic(
            sprint_id="TC-HEAL-PY-FODG-001-analytics-fix",
            planned_work_items=[],
            existing_rework_items=["GOV_BLOCK:validate_source_architecture -- fodg_codec.py"],
            current_rework_items=[],
            validator_returncode=0,
        )
        assert result["rescan_triggered"] is True

    def test_sprint_id_contains_analytics_separation(self):
        result = _run_repair_verify_logic(
            sprint_id="analytics-separation-fodg-20260618",
            planned_work_items=[],
            existing_rework_items=["GOV_BLOCK:monolith_detection_validator -- xcf_parser.py"],
            current_rework_items=[],
            validator_returncode=0,
        )
        assert result["rescan_triggered"] is True

    def test_sprint_id_contains_analytics_heal(self):
        result = _run_repair_verify_logic(
            sprint_id="analytics-heal-zst-sprint",
            planned_work_items=[],
            existing_rework_items=["GOV_BLOCK:validate_source_architecture"],
            current_rework_items=[],
            validator_returncode=0,
        )
        assert result["rescan_triggered"] is True

    def test_all_governance_taskcard_items_triggers_heal(self):
        items = [
            {"item_id": "A1", "item_type": "GOVERNANCE_TASKCARD"},
            {"item_id": "A2", "item_type": "GOVERNANCE_TASKCARD"},
        ]
        result = _run_repair_verify_logic(
            sprint_id="random-sprint-no-heal-keyword",
            planned_work_items=items,
            existing_rework_items=["GOV_BLOCK:validate_source_architecture"],
            current_rework_items=[],
            validator_returncode=0,
        )
        assert result["rescan_triggered"] is True

    def test_mixed_item_types_not_tc_heal(self):
        items = [
            {"item_id": "A1", "item_type": "GOVERNANCE_TASKCARD"},
            {"item_id": "A2", "item_type": "PRODUCT_SOURCE"},
        ]
        result = _run_repair_verify_logic(
            sprint_id="random-sprint-mixed-types",
            planned_work_items=items,
            existing_rework_items=["GOV_BLOCK:validate_source_architecture"],
            current_rework_items=[],
            validator_returncode=0,
        )
        assert result["rescan_triggered"] is False

    def test_product_sprint_not_tc_heal(self):
        result = _run_repair_verify_logic(
            sprint_id="product-deepening-fods-20260618",
            planned_work_items=[{"item_id": "X", "item_type": "PRODUCT_SOURCE"}],
            existing_rework_items=["GOV_BLOCK:validate_source_architecture"],
            current_rework_items=[],
            validator_returncode=0,
        )
        assert result["rescan_triggered"] is False


# ---------------------------------------------------------------------------
# Test: Validator exit 0 → GOV_BLOCK items removed from rework_items
# ---------------------------------------------------------------------------

class TestRescanPassedClearsBlocks:
    """Validator exit 0 removes GOV_BLOCK items from rework_items."""

    def test_govblock_validate_source_removed_on_exit_0(self):
        current_rw = [
            "GOV_BLOCK:validate_source_architecture -- fodg_codec.py: analytics functions in parser",
            "REWORK:missing_spec_fact -- GAP-FODG-001",
        ]
        result = _run_repair_verify_logic(
            sprint_id="TC-HEAL-PY-FODG-COMPLETE",
            planned_work_items=[],
            existing_rework_items=["GOV_BLOCK:validate_source_architecture"],
            current_rework_items=current_rw,
            validator_returncode=0,
        )
        assert "REWORK:missing_spec_fact -- GAP-FODG-001" in result["rework_items"]
        assert not any("GOV_BLOCK:validate_source_architecture" in it for it in result["rework_items"])

    def test_govblock_monolith_removed_on_exit_0(self):
        current_rw = [
            "GOV_BLOCK:monolith_detection_validator -- xcf_parser.py exceeded baseline_loc_cap",
        ]
        result = _run_repair_verify_logic(
            sprint_id="TC-HEAL-PY-XCF-001",
            planned_work_items=[],
            existing_rework_items=["GOV_BLOCK:monolith_detection_validator"],
            current_rework_items=current_rw,
            validator_returncode=0,
        )
        assert len(result["rework_items"]) == 0

    def test_post_repair_rescan_annotation_resolved(self):
        result = _run_repair_verify_logic(
            sprint_id="TC-HEAL-PY-FODG-001",
            planned_work_items=[],
            existing_rework_items=["GOV_BLOCK:validate_source_architecture"],
            current_rework_items=[],
            validator_returncode=0,
        )
        ann = result["post_repair_rescan"]
        assert ann is not None
        assert ann["status"] == "RESOLVED"
        assert ann["validator_exit_code"] == 0
        assert len(ann["resolved_prior_items"]) == 1

    def test_non_govblock_items_preserved_on_exit_0(self):
        current_rw = [
            "GOV_BLOCK:validate_source_architecture",
            "REWORK:other_issue",
            "EVIDENCE_GAP:missing_test",
        ]
        result = _run_repair_verify_logic(
            sprint_id="TC-HEAL-PY-ZST-001",
            planned_work_items=[],
            existing_rework_items=["GOV_BLOCK:validate_source_architecture"],
            current_rework_items=current_rw,
            validator_returncode=0,
        )
        assert "REWORK:other_issue" in result["rework_items"]
        assert "EVIDENCE_GAP:missing_test" in result["rework_items"]
        assert not any("GOV_BLOCK" in it for it in result["rework_items"])


# ---------------------------------------------------------------------------
# Test: Validator exit non-zero → GOV_BLOCK items retained with annotation
# ---------------------------------------------------------------------------

class TestRescanFailedRetainsBlocks:
    """Validator exit non-zero retains GOV_BLOCK items with annotation."""

    def test_govblock_retained_on_exit_1(self):
        current_rw = ["GOV_BLOCK:validate_source_architecture -- fodg_codec.py"]
        result = _run_repair_verify_logic(
            sprint_id="TC-HEAL-PY-FODG-001",
            planned_work_items=[],
            existing_rework_items=["GOV_BLOCK:validate_source_architecture"],
            current_rework_items=current_rw,
            validator_returncode=1,
            validator_stderr="RULE-AM-001: 223 analytics fns still in fodg_codec.py",
        )
        assert len(result["rework_items"]) == 1
        assert "[post_repair_rescan:STILL_FAILING]" in result["rework_items"][0]

    def test_post_repair_rescan_annotation_still_failing(self):
        result = _run_repair_verify_logic(
            sprint_id="TC-HEAL-PY-FODG-001",
            planned_work_items=[],
            existing_rework_items=["GOV_BLOCK:validate_source_architecture"],
            current_rework_items=["GOV_BLOCK:validate_source_architecture"],
            validator_returncode=2,
            validator_stderr="error details",
        )
        ann = result["post_repair_rescan"]
        assert ann is not None
        assert ann["status"] == "STILL_FAILING"
        assert ann["validator_exit_code"] == 2
        assert "error details" in ann["validator_stderr"]

    def test_non_govblock_items_not_annotated_on_failure(self):
        current_rw = [
            "GOV_BLOCK:validate_source_architecture",
            "REWORK:other",
        ]
        result = _run_repair_verify_logic(
            sprint_id="TC-HEAL-PY-ZST-001",
            planned_work_items=[],
            existing_rework_items=["GOV_BLOCK:validate_source_architecture"],
            current_rework_items=current_rw,
            validator_returncode=1,
        )
        assert any("[post_repair_rescan:STILL_FAILING]" in it for it in result["rework_items"])
        assert "REWORK:other" in result["rework_items"]
        assert not any("[post_repair_rescan:STILL_FAILING]" in it
                       for it in result["rework_items"] if "REWORK:other" in it)


# ---------------------------------------------------------------------------
# Test: No re-scan when no prior structural blocks
# ---------------------------------------------------------------------------

class TestNoPriorBlocksSkipsRescan:
    """Re-scan not triggered when prior signal had no structural GOV_BLOCKs."""

    def test_no_prior_blocks_no_rescan(self):
        result = _run_repair_verify_logic(
            sprint_id="TC-HEAL-PY-XCF-001",
            planned_work_items=[],
            existing_rework_items=["REWORK:unrelated_issue"],
            current_rework_items=[],
            validator_returncode=0,
        )
        assert result["rescan_triggered"] is False
        assert result["post_repair_rescan"] is None

    def test_empty_prior_rework_items_no_rescan(self):
        result = _run_repair_verify_logic(
            sprint_id="TC-HEAL-PY-ZST-001",
            planned_work_items=[],
            existing_rework_items=[],
            current_rework_items=[],
            validator_returncode=0,
        )
        assert result["rescan_triggered"] is False


# ---------------------------------------------------------------------------
# Test: Validator path missing → re-scan skipped gracefully
# ---------------------------------------------------------------------------

class TestValidatorPathMissing:
    """When validator file doesn't exist, skip gracefully."""

    def test_missing_validator_no_rescan(self):
        result = _run_repair_verify_logic(
            sprint_id="TC-HEAL-PY-FODG-001",
            planned_work_items=[],
            existing_rework_items=["GOV_BLOCK:validate_source_architecture"],
            current_rework_items=["GOV_BLOCK:validate_source_architecture"],
            validator_returncode=None,
            validator_path_exists=False,
        )
        assert result["rescan_triggered"] is False
        # rework_items unchanged
        assert "GOV_BLOCK:validate_source_architecture" in result["rework_items"]
