"""Tests for check_lane_conflicts() and MULTI_LANE lane awareness.

WI-TC-S55-003: Sprint declarations for multi-lane work should declare lane: MULTI_LANE
to avoid LANE_ENFORCEMENT violations.

Extracted to separate file to keep test_governance_validators.py under LOC cap.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


class TestMultiLaneDeclaration:
    """Tests for check_lane_conflicts() and MULTI_LANE lane awareness (WI-TC-S55-003)."""

    def _get_fn(self):
        from autonomous_cycle_extensions import check_lane_conflicts
        return check_lane_conflicts

    def test_multi_lane_returns_no_conflicts(self):
        """MULTI_LANE declared lane: no conflicts regardless of files touched."""
        fn = self._get_fn()
        conflicts = fn(
            declared_lane="MULTI_LANE",
            changed_files=["src/python/csv/models.py", "tools/supervisor/governance_validators.py"],
        )
        assert conflicts == [], f"MULTI_LANE must return empty conflicts, got: {conflicts}"

    def test_multi_lane_case_insensitive(self):
        """multi_lane (lowercase) also returns no conflicts."""
        fn = self._get_fn()
        conflicts = fn(
            declared_lane="multi_lane",
            changed_files=["src/python/foo.py", "tests/supervisor/bar.py"],
        )
        assert conflicts == []

    def test_empty_lane_returns_no_conflicts(self):
        """Empty declared lane: no conflicts possible."""
        fn = self._get_fn()
        conflicts = fn(declared_lane="", changed_files=["src/python/foo.py"])
        assert conflicts == []

    def test_single_lane_same_files_no_conflict(self):
        """Declaring SUPERVISOR lane with only supervisor files: no conflict."""
        fn = self._get_fn()
        conflicts = fn(
            declared_lane="SUPERVISOR",
            changed_files=["tools/supervisor/governance_validators.py"],
        )
        assert conflicts == []

    def test_single_lane_cross_lane_file_produces_conflict(self):
        """Declaring SUPERVISOR lane but changing a PYTHON_PRODUCT file: conflict."""
        fn = self._get_fn()
        conflicts = fn(
            declared_lane="SUPERVISOR",
            changed_files=["src/python/csv/models.py"],
        )
        assert len(conflicts) > 0, "Cross-lane file must produce conflict"
        assert any("CRITICAL" in c or "LANE_CONFLICT" in c for c in conflicts)

    def test_critical_product_file_in_governance_lane(self):
        """Product source file in GOVERNANCE lane is flagged CRITICAL."""
        fn = self._get_fn()
        conflicts = fn(
            declared_lane="GOVERNANCE",
            changed_files=["src/python/csv/models.py"],
        )
        assert any("CRITICAL" in c for c in conflicts), (
            f"Expected CRITICAL in conflicts for product file in GOVERNANCE lane: {conflicts}"
        )

    def test_global_exempt_paths_not_flagged(self):
        """Gap-ledger and reports/ are exempt — SUPERVISOR declaration with them has no conflict."""
        fn = self._get_fn()
        conflicts = fn(
            declared_lane="SUPERVISOR",
            changed_files=[
                "tools/supervisor/governance_validators.py",
                "reports/capability-layer/gap-ledger.json",
                "registry/source-structure-baseline.json",
            ],
        )
        assert conflicts == [], (
            f"Exempt paths must not trigger conflicts: {conflicts}"
        )
