"""Deterministic gap selection regression tests.

TC-SAL-HARD-002: Verify capability_queue_consumer selects gaps deterministically
with priority ordering and assigned-gap tracking.
"""

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from capability_queue_consumer import _priority_sort_key, _PRIORITY_ORDER


class TestPrioritySortKey:
    """_priority_sort_key produces deterministic, priority-ordered keys."""

    def test_p0_before_p1(self):
        g0 = {"priority": "P0", "gap_id": "GAP-A"}
        g1 = {"priority": "P1", "gap_id": "GAP-A"}
        assert _priority_sort_key(g0) < _priority_sort_key(g1)

    def test_p1_before_p2(self):
        g1 = {"priority": "P1", "gap_id": "GAP-A"}
        g2 = {"priority": "P2", "gap_id": "GAP-A"}
        assert _priority_sort_key(g1) < _priority_sort_key(g2)

    def test_same_priority_alphabetical(self):
        ga = {"priority": "P1", "gap_id": "GAP-AAA"}
        gb = {"priority": "P1", "gap_id": "GAP-BBB"}
        assert _priority_sort_key(ga) < _priority_sort_key(gb)

    def test_missing_priority_defaults_to_p4(self):
        g_no_p = {"gap_id": "GAP-X"}
        g_p4 = {"priority": "P4", "gap_id": "GAP-X"}
        assert _priority_sort_key(g_no_p) == _priority_sort_key(g_p4)

    def test_deterministic_sort(self):
        """Sorting the same list twice produces identical results."""
        gaps = [
            {"priority": "P2", "gap_id": "GAP-C"},
            {"priority": "P0", "gap_id": "GAP-B"},
            {"priority": "P1", "gap_id": "GAP-A"},
            {"priority": "P0", "gap_id": "GAP-A"},
            {"priority": "P1", "gap_id": "GAP-B"},
        ]
        sorted1 = sorted(gaps, key=_priority_sort_key)
        sorted2 = sorted(gaps, key=_priority_sort_key)
        ids1 = [g["gap_id"] for g in sorted1]
        ids2 = [g["gap_id"] for g in sorted2]
        assert ids1 == ids2
        # P0 gaps first, then P1, then P2
        assert ids1 == ["GAP-A", "GAP-B", "GAP-A", "GAP-B", "GAP-C"]

    def test_all_priority_levels_ordered(self):
        """All defined priority levels sort in order P0 < P1 < ... < P5."""
        gaps = [{"priority": f"P{i}", "gap_id": "GAP"} for i in range(6)]
        sorted_gaps = sorted(gaps, key=_priority_sort_key)
        priorities = [g["priority"] for g in sorted_gaps]
        assert priorities == ["P0", "P1", "P2", "P3", "P4", "P5"]


class TestPriorityOrderMap:
    """_PRIORITY_ORDER contains expected entries."""

    def test_has_p0_through_p5(self):
        for i in range(6):
            assert f"P{i}" in _PRIORITY_ORDER

    def test_values_are_ascending(self):
        values = [_PRIORITY_ORDER[f"P{i}"] for i in range(6)]
        assert values == sorted(values)
