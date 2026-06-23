"""Unit tests for _sync_hard_stops_after_repair() helper (TC-SIGNAL-001).

Covers all branching cases:
- TC-SYNC-001: GOV_BLOCK resolved, rework_items empty → hard_stop cleared
- TC-SYNC-002: rescan failed, rework_items still has GOV_BLOCK → hard_stop retained
- TC-SYNC-003: REJECTED item (no prior GOV_BLOCK) → hard_stop NOT cleared
- TC-SYNC-004: Two GOV_BLOCKs, only one resolved → hard_stop retained
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))

from autonomous_cycle import _sync_hard_stops_after_repair  # noqa: E402


class TestSyncHardStopsAfterRepair:
    def test_sync_clears_hard_stop_when_govblock_resolved(self) -> None:
        """TC-SYNC-001: GOV_BLOCK resolved, rework_items empty → hard_stop cleared."""
        hard_stops = ["critical_rework_blocks_continuation"]
        rework_items: list = []
        prior_blocks = ["GOV_BLOCK:monolith_detection_validator"]
        result = _sync_hard_stops_after_repair(hard_stops, rework_items, prior_blocks)
        assert "critical_rework_blocks_continuation" not in result
        assert result == []

    def test_sync_retains_hard_stop_when_rescan_failed(self) -> None:
        """TC-SYNC-002: rescan failed, rework_items still has GOV_BLOCK → hard_stop retained."""
        hard_stops = ["critical_rework_blocks_continuation"]
        rework_items = ["GOV_BLOCK:monolith_detection_validator [post_repair_rescan:STILL_FAILING]"]
        prior_blocks = ["GOV_BLOCK:monolith_detection_validator"]
        result = _sync_hard_stops_after_repair(hard_stops, rework_items, prior_blocks)
        assert "critical_rework_blocks_continuation" in result

    def test_sync_preserves_hard_stop_when_no_prior_govblocks(self) -> None:
        """TC-SYNC-003: REJECTED item caused exit_code==3 (no prior GOV_BLOCK) → hard_stop NOT cleared."""
        hard_stops = ["critical_rework_blocks_continuation"]
        rework_items: list = []  # empty — but no GOV_BLOCK was the cause
        prior_blocks: list = []  # no prior GOV_BLOCK items
        result = _sync_hard_stops_after_repair(hard_stops, rework_items, prior_blocks)
        assert "critical_rework_blocks_continuation" in result

    def test_sync_retains_hard_stop_when_partial_resolution(self) -> None:
        """TC-SYNC-004: Two GOV_BLOCKs, only one resolved → hard_stop retained."""
        hard_stops = ["critical_rework_blocks_continuation"]
        rework_items = ["GOV_BLOCK:validate_source_architecture"]  # one still active
        prior_blocks = [
            "GOV_BLOCK:monolith_detection_validator",
            "GOV_BLOCK:validate_source_architecture",
        ]
        result = _sync_hard_stops_after_repair(hard_stops, rework_items, prior_blocks)
        assert "critical_rework_blocks_continuation" in result
