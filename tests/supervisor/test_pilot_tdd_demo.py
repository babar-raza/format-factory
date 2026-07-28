"""Pilot TDD demo (test-driven-development skill pilot, 2026-07-14).

Marked as pilot work per the pilot task instructions — not mixed into the
existing test_capability_queue_consumer.py file.

Target under test: capability_queue_consumer._priority_sort_key — a small
pure function (no I/O, deterministic) that had no direct test coverage
before this pilot. It is exercised indirectly via load_foss_gaps() but had
no unit-level test asserting its own tuple-construction and default/
tie-break behavior.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from capability_queue_consumer import _priority_sort_key


class TestPrioritySortKey:
    def test_known_priority_maps_to_its_rank(self):
        gap = {"priority": "P0", "gap_id": "GAP-A"}
        assert _priority_sort_key(gap) == (0, "GAP-A")

    def test_missing_priority_defaults_to_p4_rank(self):
        gap = {"gap_id": "GAP-B"}  # no "priority" key at all
        assert _priority_sort_key(gap) == (4, "GAP-B")

    def test_unrecognized_priority_string_defaults_to_rank_4(self):
        gap = {"priority": "P9", "gap_id": "GAP-C"}
        assert _priority_sort_key(gap) == (4, "GAP-C")

    def test_missing_gap_id_defaults_to_empty_string(self):
        gap = {"priority": "P2"}
        assert _priority_sort_key(gap) == (2, "")

    def test_sorted_orders_by_priority_then_gap_id(self):
        gaps = [
            {"priority": "P1", "gap_id": "GAP-ZEBRA"},
            {"priority": "P0", "gap_id": "GAP-B"},
            {"priority": "P0", "gap_id": "GAP-A"},
            {"priority": "P4", "gap_id": "GAP-LAST"},
        ]
        ordered = sorted(gaps, key=_priority_sort_key)
        ordered_ids = [g["gap_id"] for g in ordered]
        assert ordered_ids == ["GAP-A", "GAP-B", "GAP-ZEBRA", "GAP-LAST"]
