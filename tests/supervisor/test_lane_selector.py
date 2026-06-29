"""Tests for lane_selector.py — TC-DL2-001."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml

# Minimal ledger entry factory
def _make_entry(
    fmt: str = "fods",
    dom_applicability: str = "FULL",
    lane_b_maturity: str = "D3",
    lane_b_ceiling: str = "D5",
    lane_a_maturity: str = "A1",
    execution_mode: str = "AUTO",
    lane_a_consecutive: int = 0,
    lane_b_consecutive: int = 0,
    lane_starvation_threshold: int = 3,
) -> dict:
    return {
        "product_id": f"{fmt.upper()}-PYTHON",
        "format": fmt,
        "runtime": "python",
        "dom_applicability": dom_applicability,
        "lane_a_maturity": lane_a_maturity,
        "lane_b_maturity": lane_b_maturity,
        "lane_b_ceiling": lane_b_ceiling,
        "execution_mode": execution_mode,
        "lane_a_consecutive": lane_a_consecutive,
        "lane_b_consecutive": lane_b_consecutive,
        "lane_starvation_threshold": lane_starvation_threshold,
    }


def _write_ledger(entries: list[dict]) -> Path:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8")
    yaml.dump(entries, tmp, default_flow_style=False)
    tmp.close()
    return Path(tmp.name)


# ── Import ──
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
from lane_selector import select_lane, check_starvation


class TestSelectLane:
    """Test select_lane() for all 7 modes."""

    def test_auto_selects_dom_when_b_gap_larger(self):
        """AUTO mode selects 'dom' when B gap > A gap."""
        ledger = _write_ledger([_make_entry(lane_b_maturity="D1", lane_b_ceiling="D5", lane_a_maturity="A4")])
        result = select_lane("fods", ledger_path=ledger)
        assert result["selected_lane"] == "dom"
        assert "dom_gap_larger" in result["reason"]

    def test_auto_selects_feature_when_a_gap_larger(self):
        """AUTO mode selects 'feature' when A gap > B gap."""
        ledger = _write_ledger([_make_entry(lane_b_maturity="D4", lane_b_ceiling="D5", lane_a_maturity="A0")])
        result = select_lane("fods", ledger_path=ledger)
        assert result["selected_lane"] == "feature"
        assert "feature_gap_larger" in result["reason"]

    def test_feature_only_always_feature(self):
        """FEATURE_ONLY mode always returns 'feature'."""
        ledger = _write_ledger([_make_entry(execution_mode="FEATURE_ONLY")])
        result = select_lane("fods", ledger_path=ledger)
        assert result["selected_lane"] == "feature"
        assert result["mode"] == "FEATURE_ONLY"

    def test_dom_only_always_dom(self):
        """DOM_ONLY mode always returns 'dom'."""
        ledger = _write_ledger([_make_entry(execution_mode="DOM_ONLY")])
        result = select_lane("fods", ledger_path=ledger)
        assert result["selected_lane"] == "dom"

    def test_balanced_alternates(self):
        """BALANCED mode alternates based on consecutive counters."""
        ledger = _write_ledger([_make_entry(execution_mode="BALANCED", lane_a_consecutive=2, lane_b_consecutive=0)])
        result = select_lane("fods", ledger_path=ledger)
        assert result["selected_lane"] == "dom"

    def test_at_ceiling_returns_feature(self):
        """Format at DOM ceiling → always 'feature'."""
        ledger = _write_ledger([_make_entry(lane_b_maturity="D5", lane_b_ceiling="D5")])
        result = select_lane("fods", ledger_path=ledger)
        assert result["selected_lane"] == "feature"
        assert "at_dom_ceiling" in result["reason"]

    def test_flat_format_returns_feature(self):
        """FLAT format → always 'feature' in AUTO mode."""
        ledger = _write_ledger([_make_entry(fmt="csv", dom_applicability="FLAT")])
        result = select_lane("csv", ledger_path=ledger)
        assert result["selected_lane"] == "feature"
        assert "dom_not_applicable" in result["reason"]

    def test_metrics_only_returns_feature(self):
        """METRICS_ONLY format → always 'feature' in AUTO mode."""
        ledger = _write_ledger([_make_entry(fmt="zst", dom_applicability="METRICS_ONLY")])
        result = select_lane("zst", ledger_path=ledger)
        assert result["selected_lane"] == "feature"

    def test_starvation_override_forces_switch(self):
        """When consecutive >= threshold, starvation override forces switch."""
        ledger = _write_ledger([_make_entry(lane_a_consecutive=3, lane_b_consecutive=0)])
        result = select_lane("fods", ledger_path=ledger)
        assert result["selected_lane"] == "dom"
        assert "starvation_override" in result["reason"]

    def test_missing_format_returns_error(self):
        """Missing format returns error dict gracefully."""
        ledger = _write_ledger([_make_entry(fmt="fods")])
        result = select_lane("nonexistent", ledger_path=ledger)
        assert result.get("error") is not None
        assert result["selected_lane"] is None

    def test_parallel_returns_list(self):
        """PARALLEL returns list of both lanes."""
        ledger = _write_ledger([_make_entry(execution_mode="PARALLEL")])
        result = select_lane("fods", ledger_path=ledger)
        assert isinstance(result["selected_lane"], list)
        assert "feature" in result["selected_lane"]
        assert "dom" in result["selected_lane"]

    def test_sequential_dom_then_feature(self):
        """SEQUENTIAL_DOM_THEN_FEATURE transitions correctly."""
        # Below ceiling → dom
        ledger = _write_ledger([_make_entry(execution_mode="SEQUENTIAL_DOM_THEN_FEATURE", lane_b_maturity="D2")])
        result = select_lane("fods", ledger_path=ledger)
        assert result["selected_lane"] == "dom"

        # At ceiling → feature (handled by early ceiling check)
        ledger2 = _write_ledger([_make_entry(execution_mode="SEQUENTIAL_DOM_THEN_FEATURE", lane_b_maturity="D5", lane_b_ceiling="D5")])
        result2 = select_lane("fods", ledger_path=ledger2)
        assert result2["selected_lane"] == "feature"


class TestCheckStarvation:
    """Test check_starvation() behavior."""

    def test_below_threshold_no_switch(self):
        """2 consecutive < threshold of 3 → no switch."""
        ledger = _write_ledger([_make_entry(lane_a_consecutive=2)])
        result = check_starvation("fods", ledger)
        assert result["must_switch"] is False

    def test_at_threshold_must_switch(self):
        """3 consecutive = threshold → must_switch True."""
        ledger = _write_ledger([_make_entry(lane_a_consecutive=3)])
        result = check_starvation("fods", ledger)
        assert result["must_switch"] is True
        assert result["starved_lane"] == "dom"

    def test_lane_b_starved_selects_feature(self):
        """Lane B starved → starved_lane = feature."""
        ledger = _write_ledger([_make_entry(lane_b_consecutive=3)])
        result = check_starvation("fods", ledger)
        assert result["must_switch"] is True
        assert result["starved_lane"] == "feature"

    def test_at_ceiling_exempts_starvation(self):
        """At-ceiling format → can't switch to dom, must_switch=False."""
        ledger = _write_ledger([_make_entry(lane_a_consecutive=5, lane_b_maturity="D5", lane_b_ceiling="D5")])
        result = check_starvation("fods", ledger)
        assert result["must_switch"] is False
        assert result["advisory_only"] is True

    def test_feature_only_mode_advisory(self):
        """FEATURE_ONLY mode → starvation advisory only."""
        ledger = _write_ledger([_make_entry(execution_mode="FEATURE_ONLY", lane_a_consecutive=5)])
        result = check_starvation("fods", ledger)
        assert result["must_switch"] is False
        assert result["advisory_only"] is True
