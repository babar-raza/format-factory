"""Lane pipeline integration tests — TC-PCL-011-01/02.

Tests idempotency, determinism, and regression control for the dual-lane
deepening feedback loop components.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = REPO_ROOT / "registry" / "product-deepening-ledger.yaml"
GAP_LEDGER_PATH = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger.json"


# ── TC-PCL-011-01: Idempotency and determinism ─────────────────────────────

def test_dom_gap_generator_idempotent(tmp_path):
    """Running dom_gap_generator twice produces identical gap-ledger output."""
    from dom_gap_generator import run

    policies_path = REPO_ROOT / ".supervisor" / "policies.yaml"
    ledger_yaml = REPO_ROOT / "registry" / "product-deepening-ledger.yaml"

    gap1 = tmp_path / "gaps1.json"
    gap2 = tmp_path / "gaps2.json"
    gap1.write_text(json.dumps({"gaps": []}))
    gap2.write_text(json.dumps({"gaps": []}))

    r1 = run(ledger_yaml, gap1, policies_path, dry_run=False, format_filter=None)
    r2 = run(ledger_yaml, gap2, policies_path, dry_run=False, format_filter=None)

    data1 = json.loads(gap1.read_text())
    data2 = json.loads(gap2.read_text())

    gaps1 = sorted(data1.get("gaps", []), key=lambda g: g.get("gap_id", ""))
    gaps2 = sorted(data2.get("gaps", []), key=lambda g: g.get("gap_id", ""))
    assert gaps1 == gaps2, "Second run should produce identical gaps"

    # Third run with populated ledger should add 0 new gaps
    r3 = run(ledger_yaml, gap1, policies_path, dry_run=False, format_filter=None)
    assert r3.get("added", 0) == 0, "Third run (idempotent) must add 0 new gaps"


def test_lane_selector_deterministic():
    """Running lane_selector for FODS twice with identical ledger gives identical output."""
    r1 = subprocess.run(
        [sys.executable, "tools/supervisor/lane_selector.py", "--format", "fods",
         "--ledger", str(LEDGER_PATH)],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    r2 = subprocess.run(
        [sys.executable, "tools/supervisor/lane_selector.py", "--format", "fods",
         "--ledger", str(LEDGER_PATH)],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    assert r1.returncode == 0
    assert r2.returncode == 0
    assert r1.stdout == r2.stdout, "lane_selector output must be deterministic"


def test_dom_maturity_promoter_fods_returns_d2():
    """assess_dom_maturity for FODS returns computed_level >= D2."""
    from dom_maturity_promoter import assess_dom_maturity
    result = assess_dom_maturity("fods", repo_root=REPO_ROOT)
    level = result.get("computed_level") or "D0"
    levels = {"D0": 0, "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D5": 5}
    assert levels.get(level, 0) >= 2, f"FODS computed_level={level} must be >= D2"


def test_dom_maturity_promoter_fodt_returns_d2():
    """assess_dom_maturity for FODT returns computed_level >= D2."""
    from dom_maturity_promoter import assess_dom_maturity
    result = assess_dom_maturity("fodt", repo_root=REPO_ROOT)
    level = result.get("computed_level") or "D0"
    levels = {"D0": 0, "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D5": 5}
    assert levels.get(level, 0) >= 2, f"FODT computed_level={level} must be >= D2"


# ── TC-PCL-011-02: Lane counter fallback regression ────────────────────────

def _make_single_entry_ledger(tmp_path: Path, fmt: str = "fodt") -> Path:
    entries = [{
        "format": fmt, "runtime": "python", "dom_applicability": "FULL",
        "lane_a_maturity": "A1", "lane_b_maturity": "D2", "lane_b_ceiling": "D5",
        "lane_a_consecutive": 0, "lane_b_consecutive": 0, "lane_starvation_threshold": 3,
    }]
    p = tmp_path / "ledger.yaml"
    p.write_text(yaml.dump(entries))
    return p


def test_counter_update_with_explicit_field(tmp_path):
    """deepening_lane: dom → lane_b_consecutive increments."""
    from autonomous_cycle_extensions import update_lane_counters
    ledger = _make_single_entry_ledger(tmp_path)
    decl = {
        "sprint_id": "R-REG-001",
        "planned_work_items": [{"status": "completed", "format": "fodt", "deepening_lane": "dom"}]
    }
    update_lane_counters(decl, ledger)
    data = yaml.safe_load(ledger.read_text())
    assert data[0]["lane_b_consecutive"] == 1
    assert data[0]["lane_a_consecutive"] == 0


def test_counter_update_with_gap_id_fallback(tmp_path):
    """DOM gap_id without deepening_lane field → lane_b_consecutive increments."""
    from autonomous_cycle_extensions import update_lane_counters
    ledger = _make_single_entry_ledger(tmp_path)
    decl = {
        "sprint_id": "R-REG-002",
        "planned_work_items": [{"status": "completed", "format": "fodt",
                                "gap_id": "GAP-FODT-DOM-D2-MUTATION-AND-ROUNDTRIP-001"}]
    }
    update_lane_counters(decl, ledger)
    data = yaml.safe_load(ledger.read_text())
    assert data[0]["lane_b_consecutive"] == 1


def test_counter_no_change_for_feature_gap(tmp_path):
    """Feature gap_id (no -DOM-) → lane_b_consecutive unchanged, lane_a increments."""
    from autonomous_cycle_extensions import update_lane_counters
    ledger = _make_single_entry_ledger(tmp_path)
    decl = {
        "sprint_id": "R-REG-003",
        "planned_work_items": [{"status": "completed", "format": "fodt",
                                "gap_id": "GAP-FODT-LOAD-BASIC-001"}]
    }
    update_lane_counters(decl, ledger)
    data = yaml.safe_load(ledger.read_text())
    assert data[0]["lane_b_consecutive"] == 0
    assert data[0]["lane_a_consecutive"] == 1
