"""Tests for update_lane_counters() gap_id fallback — TC-PCL-004-05."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
from autonomous_cycle_extensions import update_lane_counters


def _make_ledger(tmp_path: Path, fmt: str = "fodt") -> Path:
    entries = [{
        "format": fmt, "runtime": "python", "dom_applicability": "FULL",
        "lane_a_maturity": "A1", "lane_b_maturity": "D2", "lane_b_ceiling": "D5",
        "lane_a_consecutive": 0, "lane_b_consecutive": 0, "lane_starvation_threshold": 3,
    }]
    p = tmp_path / "ledger.yaml"
    p.write_text(yaml.dump(entries))
    return p


def _make_declaration(fmt: str, lane: str = None, gap_id: str = "") -> dict:
    item = {
        "item_id": "WI-001",
        "title": "test item",
        "status": "completed",
        "format": fmt,
    }
    if lane:
        item["deepening_lane"] = lane
    if gap_id:
        item["gap_id"] = gap_id
    return {"sprint_id": "R-TEST-001", "planned_work_items": [item]}


# ── TC-PCL-004-02: gap_id fallback ───────────────────────────────────────────

def test_explicit_dom_field_increments_counter(tmp_path):
    """Explicit deepening_lane=dom → lane_b_consecutive increments."""
    ledger = _make_ledger(tmp_path, "fodt")
    decl = _make_declaration("fodt", lane="dom")
    update_lane_counters(decl, ledger)
    data = yaml.safe_load(ledger.read_text())
    assert data[0]["lane_b_consecutive"] == 1
    assert data[0]["lane_a_consecutive"] == 0


def test_gap_id_fallback_increments_counter(tmp_path):
    """No deepening_lane but gap_id contains -DOM- → lane_b_consecutive increments."""
    ledger = _make_ledger(tmp_path, "fodt")
    decl = _make_declaration("fodt", gap_id="GAP-FODT-DOM-D3-NESTED-TRAVERSAL-MUTATION-001")
    update_lane_counters(decl, ledger)
    data = yaml.safe_load(ledger.read_text())
    assert data[0]["lane_b_consecutive"] == 1
    assert data[0]["lane_a_consecutive"] == 0


def test_feature_gap_id_increments_lane_a(tmp_path):
    """No deepening_lane, gap_id without -DOM- → lane_a_consecutive increments."""
    ledger = _make_ledger(tmp_path, "fodt")
    decl = _make_declaration("fodt", gap_id="GAP-FODT-FEATURE-LOAD-001")
    update_lane_counters(decl, ledger)
    data = yaml.safe_load(ledger.read_text())
    assert data[0]["lane_a_consecutive"] == 1
    assert data[0]["lane_b_consecutive"] == 0


def test_explicit_field_beats_gap_id(tmp_path):
    """Explicit deepening_lane=feature takes precedence over DOM gap_id."""
    ledger = _make_ledger(tmp_path, "fodt")
    decl = _make_declaration("fodt", lane="feature",
                              gap_id="GAP-FODT-DOM-D2-MUTATION-AND-ROUNDTRIP-001")
    update_lane_counters(decl, ledger)
    data = yaml.safe_load(ledger.read_text())
    # Explicit field wins: lane_a increments, not lane_b
    assert data[0]["lane_a_consecutive"] == 1
    assert data[0]["lane_b_consecutive"] == 0


def test_three_consecutive_dom_sets_threshold(tmp_path):
    """Three DOM declarations for FODT → lane_b_consecutive==3."""
    ledger = _make_ledger(tmp_path, "fodt")
    for i in range(3):
        decl = _make_declaration("fodt", gap_id="GAP-FODT-DOM-D3-001")
        decl["sprint_id"] = f"R-TEST-{i:03d}"  # different sprint_ids
        update_lane_counters(decl, ledger)
    data = yaml.safe_load(ledger.read_text())
    assert data[0]["lane_b_consecutive"] == 3
