"""Tests for TC-MACH-LANE-001: Preventive lane guard via check_lane_conflicts().

Integration-grade: imports and calls the REAL extracted function from
autonomous_cycle_extensions.py (same code wired into autonomous_cycle.py Step 1c).

Verifies that:
- MACHINERY sprint touching src/python/ or src/net/ → LANE_CONFLICT hard_stop
- PRODUCT sprint touching tools/supervisor/ → LANE_CONFLICT hard_stop
- MACHINERY sprint touching only tools/ → no conflict
- Grace period suppresses conflict to warning
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from autonomous_cycle_extensions import check_lane_conflicts


class TestLaneGuard:
    """TC-MACH-LANE-001 lane guard integration tests."""

    def test_machinery_touching_product_source_blocked(self):
        """MACHINERY sprint with src/python/ file → LANE_CONFLICT."""
        stops = check_lane_conflicts(
            "MACHINERY",
            ["tools/supervisor/capability_compiler.py", "src/python/fods/models.py"],
        )
        assert len(stops) == 1
        assert "LANE_CONFLICT" in stops[0]
        assert "MACHINERY" in stops[0]

    def test_machinery_touching_dotnet_source_blocked(self):
        """MACHINERY sprint with src/net/ file → LANE_CONFLICT."""
        stops = check_lane_conflicts(
            "MACHINERY",
            ["src/net/fods/FodsDocument.cs"],
        )
        assert len(stops) == 1
        assert "LANE_CONFLICT" in stops[0]

    def test_product_touching_supervisor_blocked(self):
        """PRODUCT sprint with tools/supervisor/ file → LANE_CONFLICT."""
        stops = check_lane_conflicts(
            "PRODUCT",
            ["src/python/fods/models.py", "tools/supervisor/autonomous_cycle.py"],
        )
        assert len(stops) == 1
        assert "LANE_CONFLICT" in stops[0]
        assert "PRODUCT" in stops[0]

    def test_product_touching_test_file_allowed(self):
        """PRODUCT sprint with tools/supervisor/*_test.py → no conflict."""
        stops = check_lane_conflicts(
            "PRODUCT",
            ["src/python/fods/models.py", "tools/supervisor/some_test.py"],
        )
        assert len(stops) == 0

    def test_machinery_only_tools_no_conflict(self):
        """MACHINERY sprint touching only tools/ → no conflict."""
        stops = check_lane_conflicts(
            "MACHINERY",
            ["tools/supervisor/capability_compiler.py", "tools/backfill/inventory.py"],
        )
        assert len(stops) == 0

    def test_grace_period_suppresses_conflict(self, tmp_path):
        """Grace period active → no hard_stop even with violations."""
        policies = tmp_path / "policies.yaml"
        policies.write_text("lanes_grace_period_until: '2099-12-31'\n")
        stops = check_lane_conflicts(
            "MACHINERY",
            ["src/python/fods/models.py"],
            policies_path=policies,
        )
        assert len(stops) == 0

    def test_expired_grace_period_does_not_suppress(self, tmp_path):
        """Expired grace period → conflict fires normally."""
        policies = tmp_path / "policies.yaml"
        policies.write_text("lanes_grace_period_until: '2020-01-01'\n")
        stops = check_lane_conflicts(
            "MACHINERY",
            ["src/python/fods/models.py"],
            policies_path=policies,
        )
        assert len(stops) == 1
        assert "LANE_CONFLICT" in stops[0]

    def test_no_lane_declared_no_conflict(self):
        """No lane declared → no conflict check fires."""
        stops = check_lane_conflicts(
            "",
            ["src/python/fods/models.py", "tools/supervisor/autonomous_cycle.py"],
        )
        assert len(stops) == 0

    def test_none_policies_path_no_grace(self):
        """policies_path=None means no grace period lookup."""
        stops = check_lane_conflicts(
            "MACHINERY",
            ["src/python/fods/models.py"],
            policies_path=None,
        )
        assert len(stops) == 1
        assert "LANE_CONFLICT" in stops[0]
