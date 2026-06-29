"""Tests for lane counter replay safety — TC-DL2-019."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
from autonomous_cycle_extensions import update_lane_counters


def _make_ledger(fmt="fods", a_consec=0, b_consec=0, b_maturity="D3", b_ceiling="D5"):
    entries = [{
        "product_id": f"{fmt.upper()}-PYTHON", "format": fmt, "runtime": "python",
        "lane_a_consecutive": a_consec, "lane_b_consecutive": b_consec,
        "lane_b_maturity": b_maturity, "lane_b_ceiling": b_ceiling,
    }]
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8")
    yaml.dump(entries, tmp, default_flow_style=False)
    tmp.close()
    return Path(tmp.name)


def _make_declaration(sprint_id, items):
    return {"sprint_id": sprint_id, "planned_work_items": items}


class TestLaneCounterReplay:

    def test_feature_sprint_increments_lane_a(self):
        """Accepted feature sprint → lane_a_consecutive increments, lane_b resets."""
        lp = _make_ledger("fods", a_consec=1, b_consec=2)
        decl = _make_declaration("s001", [
            {"format": "fods", "status": "completed", "deepening_lane": "feature"}
        ])
        update_lane_counters(decl, lp)
        data = yaml.safe_load(lp.read_text(encoding="utf-8"))
        assert data[0]["lane_a_consecutive"] == 2  # was 1, now 2
        assert data[0]["lane_b_consecutive"] == 0  # reset

    def test_dom_sprint_increments_lane_b(self):
        """Accepted DOM sprint → lane_b_consecutive increments, lane_a resets."""
        lp = _make_ledger("fods", a_consec=3, b_consec=0)
        decl = _make_declaration("s002", [
            {"format": "fods", "status": "completed", "deepening_lane": "dom"}
        ])
        update_lane_counters(decl, lp)
        data = yaml.safe_load(lp.read_text(encoding="utf-8"))
        assert data[0]["lane_b_consecutive"] == 1
        assert data[0]["lane_a_consecutive"] == 0  # reset

    def test_rejected_sprint_no_counter_change(self):
        """Rejected sprint (status != completed) → no counter change."""
        lp = _make_ledger("fods", a_consec=2, b_consec=1)
        decl = _make_declaration("s003", [
            {"format": "fods", "status": "rejected", "deepening_lane": "feature"}
        ])
        update_lane_counters(decl, lp)
        data = yaml.safe_load(lp.read_text(encoding="utf-8"))
        assert data[0]["lane_a_consecutive"] == 2  # unchanged
        assert data[0]["lane_b_consecutive"] == 1  # unchanged

    def test_duplicate_replay_double_increments(self):
        """TC-DL2-021: Replay protection — duplicate call with same sprint_id
        does NOT double-increment counters.
        """
        lp = _make_ledger("fods", a_consec=0, b_consec=0)
        decl = _make_declaration("s004", [
            {"format": "fods", "status": "completed", "deepening_lane": "feature"}
        ])
        update_lane_counters(decl, lp)
        update_lane_counters(decl, lp)  # replay — should be idempotent
        data = yaml.safe_load(lp.read_text(encoding="utf-8"))
        assert data[0]["lane_a_consecutive"] == 1  # Fixed: replay protection prevents double-increment

    def test_replay_with_sprint_id_skips_second_call(self):
        """TC-DL2-021: Same sprint_id replayed — counters unchanged after first apply."""
        lp = _make_ledger("fods", a_consec=0, b_consec=0)
        decl = _make_declaration("s005", [
            {"format": "fods", "status": "completed", "deepening_lane": "dom"}
        ])
        update_lane_counters(decl, lp)
        data1 = yaml.safe_load(lp.read_text(encoding="utf-8"))
        assert data1[0]["lane_b_consecutive"] == 1
        update_lane_counters(decl, lp)  # replay
        data2 = yaml.safe_load(lp.read_text(encoding="utf-8"))
        assert data2[0]["lane_b_consecutive"] == 1  # unchanged

    def test_different_sprint_id_updates_normally(self):
        """TC-DL2-021: Different sprint_id → counters update normally."""
        lp = _make_ledger("fods", a_consec=0, b_consec=0)
        decl1 = _make_declaration("s006", [
            {"format": "fods", "status": "completed", "deepening_lane": "feature"}
        ])
        decl2 = _make_declaration("s007", [
            {"format": "fods", "status": "completed", "deepening_lane": "feature"}
        ])
        update_lane_counters(decl1, lp)
        update_lane_counters(decl2, lp)
        data = yaml.safe_load(lp.read_text(encoding="utf-8"))
        assert data[0]["lane_a_consecutive"] == 2  # two different sprints

    def test_missing_sprint_id_falls_back(self):
        """TC-DL2-021: No sprint_id → updates without replay check (backwards compat)."""
        lp = _make_ledger("fods", a_consec=0, b_consec=0)
        decl = {"planned_work_items": [
            {"format": "fods", "status": "completed", "deepening_lane": "feature"}
        ]}  # no sprint_id
        update_lane_counters(decl, lp)
        update_lane_counters(decl, lp)  # no replay protection without sprint_id
        data = yaml.safe_load(lp.read_text(encoding="utf-8"))
        assert data[0]["lane_a_consecutive"] == 2  # no protection without sprint_id

    def test_last_applied_sprint_id_persisted(self):
        """TC-DL2-021: After update, ledger entry contains the sprint_id."""
        lp = _make_ledger("fods", a_consec=0, b_consec=0)
        decl = _make_declaration("s008", [
            {"format": "fods", "status": "completed", "deepening_lane": "feature"}
        ])
        update_lane_counters(decl, lp)
        data = yaml.safe_load(lp.read_text(encoding="utf-8"))
        assert data[0]["last_applied_sprint_id"] == "s008"

    def test_dom_sprint_at_ceiling_does_not_increment_lane_b(self):
        """DOM lane completion at ceiling should not create false starvation history."""
        lp = _make_ledger("fods", a_consec=2, b_consec=2, b_maturity="D5", b_ceiling="D5")
        decl = _make_declaration("s009", [
            {"format": "fods", "status": "completed", "deepening_lane": "dom"}
        ])
        update_lane_counters(decl, lp)
        data = yaml.safe_load(lp.read_text(encoding="utf-8"))
        assert data[0]["lane_a_consecutive"] == 2
        assert data[0]["lane_b_consecutive"] == 2
        assert data[0]["last_applied_sprint_id"] == "s009"

    def test_counters_feed_lane_selector(self):
        """Counters feed the real select_lane() function."""
        from lane_selector import select_lane
        lp = _make_ledger("fods", a_consec=3, b_consec=0)
        result = select_lane("fods", ledger_path=lp)
        assert result["selected_lane"] == "dom"
        assert "starvation" in result["reason"]
