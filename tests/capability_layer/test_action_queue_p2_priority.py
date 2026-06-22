"""TC-COMMIT-001: Regression test — P2 foss_reduced gaps must produce non-advisory actions.

Verifies that _build_action_queue is_machine_executable condition includes P2 priority
(not just P0/P1). Prevents regression of the fix from 2026-06-22 that extended the
condition from ("P0","P1") to ("P0","P1","P2").

The is_machine_executable condition (line ~997-1001 of capability_map_generator.py):
    product_type == "foss_reduced"
    AND priority in ("P0","P1","P2")
    AND not blocks_poc
    AND commercial_impact == "NONE"
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "capability_layer"))

from capability_map_generator import _build_action_queue  # noqa: E402


def _make_gap(
    priority: str,
    product_type: str = "foss_reduced",
    blocks_poc: bool = False,
    commercial_impact: str = "NONE",
    gap_id: str | None = None,
) -> dict:
    """Build a minimal gap dict with all required fields for _build_action_queue."""
    return {
        "gap_id": gap_id or f"GAP-TEST-{priority}-001",
        "capability_id": "CAP-TEST-001",
        "capability_name": "test_capability",
        "format": "FODT",
        "product_type": product_type,
        "priority": priority,
        "status": "open",
        "blocks_poc": blocks_poc,
        "blocks_readiness": False,
        "required_for_poc": False,
        "commercial_impact": commercial_impact,
        "owning_lane": "Lane 7",
        "suggested_taskcard": None,
        "suggested_verification": "pytest",
    }


class TestP2PriorityMachineExecutable:
    """P2-priority foss_reduced gaps must be machine_executable (not advisory-only).

    Regression guard for: `priority in ("P0","P1","P2")` in is_machine_executable.
    """

    def test_p2_foss_reduced_is_machine_executable(self):
        """P2 foss_reduced gap must produce machine_executable=True action."""
        actions = _build_action_queue([_make_gap("P2")], [], [])
        assert len(actions) == 1, f"Expected 1 action, got {len(actions)}: {actions}"
        action = actions[0]
        assert action["machine_executable"] is True, (
            f"P2 foss_reduced gap must be machine_executable=True, got: {action['machine_executable']}"
        )
        assert action["advisory_only"] is False, (
            f"P2 foss_reduced gap must have advisory_only=False, got: {action['advisory_only']}"
        )

    def test_p0_foss_reduced_is_machine_executable(self):
        """P0 foss_reduced gap must produce machine_executable=True (pre-existing behavior)."""
        actions = _build_action_queue([_make_gap("P0")], [], [])
        assert len(actions) == 1
        assert actions[0]["machine_executable"] is True
        assert actions[0]["advisory_only"] is False

    def test_p1_foss_reduced_is_machine_executable(self):
        """P1 foss_reduced gap must produce machine_executable=True (pre-existing behavior)."""
        actions = _build_action_queue([_make_gap("P1")], [], [])
        assert len(actions) == 1
        assert actions[0]["machine_executable"] is True
        assert actions[0]["advisory_only"] is False

    def test_p3_foss_reduced_is_advisory_only(self):
        """P3 foss_reduced gap must NOT be machine_executable (beyond P2 threshold)."""
        actions = _build_action_queue([_make_gap("P3")], [], [])
        assert len(actions) == 1
        assert actions[0]["machine_executable"] is False, (
            "P3 foss_reduced gap must NOT be machine_executable (only P0/P1/P2 qualify)"
        )
        assert actions[0]["advisory_only"] is True

    def test_commercial_p2_is_not_machine_executable(self):
        """P2 commercial (non-foss_reduced) gap must NOT be machine_executable."""
        actions = _build_action_queue([_make_gap("P2", product_type="commercial")], [], [])
        assert len(actions) == 1
        assert actions[0]["machine_executable"] is False, (
            "commercial P2 gap must NOT be machine_executable (foss_reduced product_type required)"
        )

    def test_p2_blocks_poc_is_advisory_only(self):
        """P2 foss_reduced gap that blocks_poc must NOT be machine_executable."""
        actions = _build_action_queue([_make_gap("P2", blocks_poc=True)], [], [])
        assert len(actions) == 1
        assert actions[0]["machine_executable"] is False, (
            "P2 gap with blocks_poc=True must NOT be machine_executable"
        )
        assert actions[0]["advisory_only"] is True

    def test_p2_gap_safe_for_autonomous_when_not_blocking_poc(self):
        """P2 foss_reduced gap not blocking POC must be safe_for_autonomous=True."""
        actions = _build_action_queue([_make_gap("P2", blocks_poc=False)], [], [])
        assert len(actions) == 1
        assert actions[0]["safe_for_autonomous"] is True, (
            f"P2 non-blocking gap must be safe_for_autonomous=True, got: {actions[0]['safe_for_autonomous']}"
        )

    def test_action_queue_reflects_p2_non_advisory_top_level(self):
        """When only P2 foss_reduced gap exists, top-level advisory_only must be False.

        Simulates the live condition that was fixed: previously only P0/P1 set
        machine_executable=True, so all P2 gaps were advisory → top-level advisory_only=True.
        """
        import json
        # Simulate what the generator does: any machine_executable action → top advisory_only=False
        actions = _build_action_queue([_make_gap("P2")], [], [])
        any_machine_executable = any(a.get("machine_executable") for a in actions)
        top_level_advisory = not any_machine_executable
        assert top_level_advisory is False, (
            "With a P2 foss_reduced gap, top-level advisory_only must be False "
            f"(any_machine_executable={any_machine_executable})"
        )
