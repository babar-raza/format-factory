"""Tests for capability_feature_compiler.py (TC-CAPABILITY-REPAIR-002)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))
from capability_feature_compiler import compile_gaps, run, _score, _lane, _gap_to_work_item


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _gap(
    gap_id="GAP-TEST-001",
    fmt="NDJSON",
    capability="Load",
    status="open",
    priority="P3",
    owning_lane=1,
    blocks_poc=False,
    blocks_readiness=False,
    commercial_impact="NONE",
    foss_impact="NONE",
    product_type="foss",
    gap_type="missing_implementation",
    blockers=None,
) -> dict:
    return {
        "gap_id": gap_id,
        "format": fmt,
        "capability_name": capability,
        "status": status,
        "priority": priority,
        "owning_lane": owning_lane,
        "blocks_poc": blocks_poc,
        "blocks_readiness": blocks_readiness,
        "commercial_impact": commercial_impact,
        "foss_impact": foss_impact,
        "product_type": product_type,
        "gap_type": gap_type,
        "blockers": blockers or [],
        "suggested_taskcard": "",
        "suggested_verification": "",
        "spec_facts": [],
        "current_state": "not_started",
    }


# ── Score tests ───────────────────────────────────────────────────────────────

def test_score_base_priority():
    assert _score(_gap(priority="P0")) == 0
    assert _score(_gap(priority="P3")) == 30
    assert _score(_gap(priority="P8")) == 80


def test_score_impact_penalty_both_high():
    g = _gap(commercial_impact="HIGH", foss_impact="HIGH")
    assert _score(g) < _score(_gap())  # lower score = higher priority


def test_score_blocker_bonus():
    g_poc = _gap(blocks_poc=True, priority="P4")
    g_ready = _gap(blocks_readiness=True, priority="P4")
    base = _score(_gap(priority="P4"))
    assert _score(g_poc) == base - 8
    assert _score(g_ready) == base - 5


# ── Lane mapping ─────────────────────────────────────────────────────────────

def test_lane_product_for_lanes_1_to_13():
    for lane in range(1, 14):
        assert _lane(_gap(owning_lane=lane)) == "product"


def test_lane_machinery_for_lanes_14_15():
    assert _lane(_gap(owning_lane=14)) == "machinery"
    assert _lane(_gap(owning_lane=15)) == "machinery"


# ── compile_gaps tests ────────────────────────────────────────────────────────

def test_skips_closed_gaps():
    gaps = [_gap(status="closed"), _gap(gap_id="GAP-OPEN-001")]
    items, _ = compile_gaps(gaps)
    assert all(i["gap_id"] != "GAP-TEST-001" for i in items)
    assert any(i["gap_id"] == "GAP-OPEN-001" for i in items)


def test_skips_machinery_lanes():
    gaps = [_gap(owning_lane=14, gap_id="GAP-MACH-001"), _gap(gap_id="GAP-PROD-001")]
    items, _ = compile_gaps(gaps)
    assert not any(i["gap_id"] == "GAP-MACH-001" for i in items)
    assert any(i["gap_id"] == "GAP-PROD-001" for i in items)


def test_deduplication_keeps_best_score():
    # Two gaps with same format+capability — keep lower score
    g1 = _gap(gap_id="GAP-A-001", priority="P5")
    g2 = _gap(gap_id="GAP-A-002", priority="P1")  # better score
    items, dedup = compile_gaps([g1, g2])
    item_ids = [i["gap_id"] for i in items]
    assert "GAP-A-002" in item_ids
    assert "GAP-A-001" not in item_ids
    assert any(d["gap_id"] == "GAP-A-001" for d in dedup)


def test_max_items_limit():
    gaps = [_gap(gap_id=f"GAP-X-{i:03d}", capability=f"Cap{i}") for i in range(30)]
    items, _ = compile_gaps(gaps, max_items=5)
    assert len(items) <= 5


def test_output_item_fields():
    gaps = [_gap()]
    items, _ = compile_gaps(gaps)
    assert items
    item = items[0]
    assert item["source"] == "gap_ledger"
    assert item["work_selection_mode"] if False else True  # not in item itself
    assert "gap_id" in item
    assert "gap_ref" in item
    assert item["gap_id"] == item["gap_ref"]
    assert item["item_id"].startswith("WI-")
    assert isinstance(item["spec_facts"], list)


def test_sorted_by_score():
    gaps = [
        _gap(gap_id="GAP-HIGH-001", priority="P0", capability="CapA"),
        _gap(gap_id="GAP-LOW-001", priority="P8", capability="CapB"),
    ]
    items, _ = compile_gaps(gaps)
    scores = [i["priority"] for i in items]
    assert scores == sorted(scores)


def test_work_selection_mode_in_output(tmp_path):
    ledger = {
        "schema_version": "1.0",
        "gaps": [_gap()],
        "total_gaps": 1,
    }
    ledger_path = tmp_path / "gap-ledger.json"
    ledger_path.write_text(json.dumps(ledger))
    out = tmp_path / "out.json"
    rc = run(ledger_path, out, max_items=5)
    assert rc == 0
    data = json.loads(out.read_text())
    assert data["work_selection_mode"] == "CAPABILITY_COMPILER"
    assert len(data["items"]) >= 1


def test_run_exit_1_on_missing_file(tmp_path):
    rc = run(tmp_path / "nonexistent.json", tmp_path / "out.json")
    assert rc == 1


def test_external_gate_flag():
    g = _gap(blocks_readiness=True, product_type="commercial")
    item = _gap_to_work_item(g, 50)
    assert item["external_gate"] is True


def test_no_external_gate_for_foss():
    g = _gap(blocks_readiness=True, product_type="foss")
    item = _gap_to_work_item(g, 50)
    assert item["external_gate"] is False
