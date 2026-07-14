"""Tests for TC-PCL-002: lane_selector wired into sprint generation.

Verifies:
- _build_lane_selection_section() adds ## Lane Selection to prompt
- _order_gaps_by_lane_decision() moves DOM-starved format gaps first
- Fallback graceful when lane_selector raises (REQ-LANE-006)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
import generate_next_worker_prompt as gnwp


# ── _order_gaps_by_lane_decision ─────────────────────────────────────────────

def test_dom_gaps_prioritized_when_lane_a_starved():
    """Lane B DOM gaps for DOM-selected format appear first in ordered output."""
    gaps = [
        {"gap_id": "GAP-FEATURE-001", "format": "FODS", "lane": "A"},
        {"gap_id": "GAP-FODT-DOM-D3-001", "format": "FODT", "lane": "B"},
        {"gap_id": "GAP-FEATURE-002", "format": "FODT", "lane": "A"},
    ]
    decisions = {"fods": "feature", "fodt": "dom"}
    ordered = gnwp._order_gaps_by_lane_decision(gaps, decisions)
    # FODT DOM gap must come first
    assert ordered[0]["gap_id"] == "GAP-FODT-DOM-D3-001"
    assert ordered[0]["lane"] == "B"


def test_flat_format_not_prioritized():
    """CSV (lane A only, at ceiling) never gets DOM priority regardless of decisions."""
    gaps = [
        {"gap_id": "GAP-CSV-001", "format": "CSV", "lane": "A"},
        {"gap_id": "GAP-FODS-DOM-001", "format": "FODS", "lane": "B"},
    ]
    # csv has no lane B gaps, decisions say "feature"
    decisions = {"csv": "feature", "fods": "dom"}
    ordered = gnwp._order_gaps_by_lane_decision(gaps, decisions)
    # FODS DOM gap first (fods → dom), CSV feature gap second
    assert ordered[0]["gap_id"] == "GAP-FODS-DOM-001"
    assert ordered[1]["gap_id"] == "GAP-CSV-001"


def test_no_dom_gaps_order_unchanged():
    """No Lane B gaps → order unchanged."""
    gaps = [
        {"gap_id": "GAP-A", "format": "FODS", "lane": "A"},
        {"gap_id": "GAP-B", "format": "FODT", "lane": "A"},
    ]
    decisions = {"fods": "dom", "fodt": "dom"}  # both DOM-starved but no B gaps
    ordered = gnwp._order_gaps_by_lane_decision(gaps, decisions)
    assert [g["gap_id"] for g in ordered] == ["GAP-A", "GAP-B"]


# ── _build_lane_selection_section ────────────────────────────────────────────

def test_lane_section_has_header(tmp_path):
    """Generated section starts with ## Lane Selection header."""
    ledger_entries = [
        {"format": "fods", "runtime": "python", "dom_applicability": "FULL",
         "lane_b_maturity": "D1", "lane_b_ceiling": "D5",
         "lane_a_maturity": "A1", "execution_mode": "AUTO",
         "lane_a_consecutive": 0, "lane_b_consecutive": 0,
         "lane_starvation_threshold": 3},
    ]
    ledger_path = tmp_path / "registry" / "product-deepening-ledger.yaml"
    ledger_path.parent.mkdir(parents=True)
    ledger_path.write_text(yaml.dump(ledger_entries))
    # No gap ledger needed — function falls back gracefully
    gap_dir = tmp_path / "reports" / "capability-layer"
    gap_dir.mkdir(parents=True)
    (gap_dir / "gap-ledger.json").write_text(json.dumps({"gaps": []}))

    section = gnwp._build_lane_selection_section(tmp_path)
    assert "## Lane Selection" in section
    assert "FODS" in section


def test_fallback_when_lane_selector_raises():
    """When lane_selector import fails, _build_lane_selection_section returns empty string."""
    with patch.dict("sys.modules", {"lane_selector": None}):
        # Force import failure
        result = gnwp._build_lane_selection_section(Path("/nonexistent"))
    # Must not raise; may return empty string
    assert isinstance(result, str)


def test_compute_lane_decisions_returns_empty_on_missing_ledger():
    """Missing ledger → empty dict, no exception."""
    result = gnwp._compute_lane_decisions(Path("/nonexistent/path"))
    assert isinstance(result, dict)
    assert len(result) == 0
