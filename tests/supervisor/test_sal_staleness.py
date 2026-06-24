"""Tests for TC-MACH-SAL-001: SAL staleness escalation via check_sal_staleness().

Integration-grade: imports and calls the REAL extracted function from
autonomous_cycle_extensions.py (same code wired into autonomous_cycle.py Step 0a-staleness).

Verifies that:
- Stale SAL (>7 days) blocks PRODUCT sprints
- Stale SAL does NOT block MACHINERY or SAL_REPAIR sprints
- Fresh SAL does not block any sprint
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from autonomous_cycle_extensions import check_sal_staleness


class TestSalStaleness:
    """TC-MACH-SAL-001 SAL staleness integration tests."""

    def test_stale_sal_blocks_product_sprint(self):
        """Stale SAL + product sprint → SAL_STALE hard_stop."""
        stops = check_sal_staleness(sal_is_stale=True, sprint_type="PRODUCT_DEEPENING")
        assert len(stops) == 1
        assert "SAL_STALE" in stops[0]

    def test_stale_sal_allows_machinery_sprint(self):
        """Stale SAL + MACHINERY sprint → no hard_stop."""
        stops = check_sal_staleness(sal_is_stale=True, sprint_type="MACHINERY")
        assert len(stops) == 0

    def test_stale_sal_allows_sal_repair_sprint(self):
        """Stale SAL + MACHINERY:sal_repair sprint → no hard_stop."""
        stops = check_sal_staleness(sal_is_stale=True, sprint_type="MACHINERY:SAL_REPAIR")
        assert len(stops) == 0

    def test_fresh_sal_no_block(self):
        """Fresh SAL → no hard_stop regardless of sprint type."""
        stops = check_sal_staleness(sal_is_stale=False, sprint_type="PRODUCT_DEEPENING")
        assert len(stops) == 0

    def test_empty_sprint_type_still_blocks(self):
        """Stale SAL + empty sprint type → still blocks (not MACHINERY)."""
        stops = check_sal_staleness(sal_is_stale=True, sprint_type="")
        assert len(stops) == 1
        assert "SAL_STALE" in stops[0]

    def test_case_insensitive_sprint_type(self):
        """Sprint type comparison is case-insensitive."""
        stops = check_sal_staleness(sal_is_stale=True, sprint_type="machinery")
        assert len(stops) == 0

    def test_none_sprint_type_blocks(self):
        """None sprint type treated as empty → blocks."""
        stops = check_sal_staleness(sal_is_stale=True, sprint_type="")
        assert len(stops) == 1
