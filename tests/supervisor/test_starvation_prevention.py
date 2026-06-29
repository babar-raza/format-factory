"""Tests for starvation prevention — TC-DL2-003.

Dedicated test file for hard starvation enforcement behavior.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
from lane_selector import select_lane, check_starvation


def _make_entry(**overrides) -> dict:
    base = {
        "product_id": "FODS-PYTHON", "format": "fods", "runtime": "python",
        "dom_applicability": "FULL", "lane_a_maturity": "A1",
        "lane_b_maturity": "D3", "lane_b_ceiling": "D5",
        "execution_mode": "AUTO", "lane_a_consecutive": 0,
        "lane_b_consecutive": 0, "lane_starvation_threshold": 3,
    }
    base.update(overrides)
    return base


def _write_ledger(entries):
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8")
    yaml.dump(entries, tmp, default_flow_style=False)
    tmp.close()
    return Path(tmp.name)


class TestStarvationPrevention:

    def test_below_threshold_no_switch(self):
        """2 consecutive < threshold of 3 → no switch."""
        lp = _write_ledger([_make_entry(lane_a_consecutive=2)])
        result = check_starvation("fods", lp)
        assert result["must_switch"] is False

    def test_at_threshold_must_switch(self):
        """3 consecutive = threshold → must_switch True."""
        lp = _write_ledger([_make_entry(lane_a_consecutive=3)])
        result = check_starvation("fods", lp)
        assert result["must_switch"] is True

    def test_lane_a_starved_selects_b(self):
        """Lane A starved (3 feature sprints) → selects dom."""
        lp = _write_ledger([_make_entry(lane_a_consecutive=3)])
        result = select_lane("fods", ledger_path=lp)
        assert result["selected_lane"] == "dom"
        assert "starvation_override" in result["reason"]

    def test_lane_b_starved_selects_a(self):
        """Lane B starved (3 dom sprints) → selects feature."""
        lp = _write_ledger([_make_entry(lane_b_consecutive=3)])
        result = select_lane("fods", ledger_path=lp)
        assert result["selected_lane"] == "feature"
        assert "starvation_override" in result["reason"]

    def test_at_ceiling_exempts_starvation(self):
        """At-ceiling lane exempts starvation (can't switch to dom)."""
        lp = _write_ledger([_make_entry(lane_a_consecutive=5, lane_b_maturity="D5", lane_b_ceiling="D5")])
        result = check_starvation("fods", lp)
        assert result["must_switch"] is False
        assert result["advisory_only"] is True

    def test_feature_only_mode_advisory(self):
        """FEATURE_ONLY mode → starvation advisory only, still returns feature."""
        lp = _write_ledger([_make_entry(execution_mode="FEATURE_ONLY", lane_a_consecutive=5)])
        result = check_starvation("fods", lp)
        assert result["must_switch"] is False
        assert result["advisory_only"] is True
        # select_lane should still return feature
        sel = select_lane("fods", ledger_path=lp)
        assert sel["selected_lane"] == "feature"

    def test_dom_only_mode_advisory(self):
        """DOM_ONLY mode → starvation advisory only, still returns dom."""
        lp = _write_ledger([_make_entry(execution_mode="DOM_ONLY", lane_b_consecutive=5)])
        result = check_starvation("fods", lp)
        assert result["must_switch"] is False
        assert result["advisory_only"] is True
        sel = select_lane("fods", ledger_path=lp)
        assert sel["selected_lane"] == "dom"

    def test_starvation_override_resets_pattern(self):
        """After switch, the other lane should be selected (consecutive resets in practice)."""
        # Simulate: lane_a_consecutive=3 → switch to dom → if we then set lane_b_consecutive=1, lane_a=0 → feature
        lp1 = _write_ledger([_make_entry(lane_a_consecutive=3)])
        r1 = select_lane("fods", ledger_path=lp1)
        assert r1["selected_lane"] == "dom"

        lp2 = _write_ledger([_make_entry(lane_a_consecutive=0, lane_b_consecutive=1)])
        r2 = select_lane("fods", ledger_path=lp2)
        assert r2["selected_lane"] != "dom" or "starvation" not in r2.get("reason", "")
