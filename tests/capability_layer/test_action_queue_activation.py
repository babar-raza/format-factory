"""Tests for action queue activation (Stage 3) — advisory_only removal + consumer.

TC-FL-009: Phase 3 of the feedback loop redesign (pure-knitting-dusk plan).
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "capability_layer"))

from capability_map_generator import _build_action_queue


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_gap(gap_id: str, product_type: str = "foss_reduced",
              priority: str = "P0", blocks_poc: bool = False,
              commercial_impact: str = "NONE", status: str = "open",
              **kwargs) -> dict:
    base = {
        "gap_id": gap_id,
        "format": "CSV",
        "capability_name": "Probe Csv",
        "status": status,
        "priority": priority,
        "product_type": product_type,
        "owning_lane": 1,
        "commercial_impact": commercial_impact,
        "blocks_poc": blocks_poc,
        "suggested_taskcard": "",
        "suggested_verification": "pytest tests/python/csv/ -v",
    }
    base.update(kwargs)
    return base


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestFossP0BecomesExecutable:
    """FOSS P0 gap without blockers → machine_executable=True, advisory_only=False."""

    def test_executable(self):
        gaps = [_make_gap("GAP-CSV-001", product_type="foss_reduced", priority="P0")]
        actions = _build_action_queue(gaps, [], [])
        assert len(actions) >= 1
        a = actions[0]
        assert a["machine_executable"] is True
        assert a["advisory_only"] is False


class TestCommercialStaysAdvisory:
    """Commercial product_type → advisory_only=True regardless of priority."""

    def test_advisory(self):
        gaps = [_make_gap("GAP-FODS-001", product_type="commercial", priority="P0")]
        actions = _build_action_queue(gaps, [], [])
        assert len(actions) >= 1
        a = actions[0]
        assert a["machine_executable"] is False
        assert a["advisory_only"] is True


class TestLowPriorityStaysAdvisory:
    """FOSS but P4 priority → advisory_only=True."""

    def test_advisory(self):
        gaps = [_make_gap("GAP-CSV-002", product_type="foss_reduced", priority="P4")]
        actions = _build_action_queue(gaps, [], [])
        assert len(actions) >= 1
        a = actions[0]
        assert a["machine_executable"] is False
        assert a["advisory_only"] is True


class TestBlocksPocStaysAdvisory:
    """FOSS P0 but blocks_poc=True → advisory_only=True."""

    def test_advisory(self):
        gaps = [_make_gap("GAP-CSV-003", product_type="foss_reduced",
                          priority="P0", blocks_poc=True)]
        actions = _build_action_queue(gaps, [], [])
        assert len(actions) >= 1
        a = actions[0]
        assert a["machine_executable"] is False
        assert a["advisory_only"] is True


class TestCommercialImpactStaysAdvisory:
    """FOSS P0 but commercial_impact=HIGH → advisory_only=True."""

    def test_advisory(self):
        gaps = [_make_gap("GAP-CSV-004", product_type="foss_reduced",
                          priority="P1", commercial_impact="HIGH")]
        actions = _build_action_queue(gaps, [], [])
        assert len(actions) >= 1
        a = actions[0]
        assert a["machine_executable"] is False
        assert a["advisory_only"] is True


class TestClosedGapsExcluded:
    """Closed gaps should not appear in action queue."""

    def test_excluded(self):
        gaps = [_make_gap("GAP-CLOSED-001", status="closed")]
        actions = _build_action_queue(gaps, [], [])
        assert len(actions) == 0


class TestMixedGaps:
    """Mix of executable and advisory gaps."""

    def test_mixed(self):
        gaps = [
            _make_gap("GAP-EXEC-1", product_type="foss_reduced", priority="P0"),
            _make_gap("GAP-ADV-1", product_type="commercial", priority="P0"),
            _make_gap("GAP-EXEC-2", product_type="foss_reduced", priority="P2"),
        ]
        actions = _build_action_queue(gaps, [], [])
        exec_actions = [a for a in actions if a["machine_executable"]]
        adv_actions = [a for a in actions if not a["machine_executable"]]
        assert len(exec_actions) == 2
        assert len(adv_actions) == 1
        # All executable actions should have advisory_only=False
        for a in exec_actions:
            assert a["advisory_only"] is False
        # Advisory actions should have advisory_only=True
        for a in adv_actions:
            assert a["advisory_only"] is True
