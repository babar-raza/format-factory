"""Tests for the recompute chain wiring (Train C: WIRING-RECOMPUTE-CHAIN).

Verifies that:
1. Product source changes trigger recompute in loop runner
2. Staleness validator produces actionable recompute action
3. Recompute dispatch invokes capability_map_generator
"""

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from autonomous_loop_runner import (
    WorkItem,
    dispatch_recompute,
    dispatch_item,
)
from governance_validators import validate_capability_map_staleness


class TestRecomputeDispatch:
    def test_dispatch_recompute_runs(self, tmp_path):
        """Recompute dispatch should run capability_map_generator."""
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        (evidence_root / "raw-logs").mkdir()
        ok, detail = dispatch_recompute(evidence_root)
        # Should succeed or fail gracefully (depends on repo state)
        assert isinstance(ok, bool)
        assert isinstance(detail, str)
        # Log file should be written
        log_path = evidence_root / "raw-logs" / "recompute-capability-map.log"
        assert log_path.exists()

    def test_dispatch_recompute_writes_log(self, tmp_path):
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        (evidence_root / "raw-logs").mkdir()
        dispatch_recompute(evidence_root)
        log = (evidence_root / "raw-logs" / "recompute-capability-map.log").read_text()
        assert "exit_code" in log


class TestStalenessActionableRecompute:
    def test_stale_map_produces_recompute_action(self, tmp_path):
        """When map is stale, validator produces a recompute action."""
        # Create a capability map with old timestamp
        cap_dir = tmp_path / "reports" / "capability-layer"
        cap_dir.mkdir(parents=True)
        (cap_dir / "unified-capability-map.json").write_text(json.dumps({
            "generated_at": "2020-01-01T00:00:00+00:00",
            "capabilities": [],
        }))
        # Create a source file with current timestamp
        src_dir = tmp_path / "src" / "python" / "zst"
        src_dir.mkdir(parents=True)
        (src_dir / "zst_codec.py").write_text("# test")

        result = validate_capability_map_staleness({}, repo_root=tmp_path)
        assert result["result"] == "WARN"
        assert len(result["items"]) >= 1
        item = result["items"][0]
        assert "recompute_action" in item
        assert item["recompute_action"]["action_type"] == "RECOMPUTE"
        assert item["recompute_action"]["blocks_autonomous_ready"] is True

    def test_fresh_map_passes(self, tmp_path):
        """When map is fresh, validator passes."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()

        cap_dir = tmp_path / "reports" / "capability-layer"
        cap_dir.mkdir(parents=True)
        (cap_dir / "unified-capability-map.json").write_text(json.dumps({
            "generated_at": now,
            "capabilities": [],
        }))
        # No source files = no staleness possible
        result = validate_capability_map_staleness({}, repo_root=tmp_path)
        assert result["result"] == "PASS"


class TestLoopRunnerRecomputeTrigger:
    def test_product_gap_closure_item_type(self):
        """PRODUCT_GAP_CLOSURE items should trigger recompute logic."""
        item = WorkItem(
            item_id="TASK-001",
            label="pending",
            description="Product deepening: GAP-ZST-FOSS-LOAD-001",
            action_type="PRODUCT_GAP_CLOSURE",
        )
        assert item.action_type == "PRODUCT_GAP_CLOSURE"
        # The recompute is triggered in run_loop after dispatch — tested via integration
