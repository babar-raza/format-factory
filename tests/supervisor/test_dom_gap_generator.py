"""Tests for dom_gap_generator.py — TC-PCL-001-04 (peppy-crafting-lark)."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))
import dom_gap_generator as gen


# ── Fixture helpers ───────────────────────────────────────────────────────────

def _make_ledger(entries: list[dict], tmp_path: Path) -> Path:
    p = tmp_path / "ledger.yaml"
    p.write_text(yaml.dump(entries), encoding="utf-8")
    return p


def _make_gap_ledger(gaps: list[dict], tmp_path: Path) -> Path:
    p = tmp_path / "gap-ledger.json"
    p.write_text(json.dumps({"schema_version": "1.0", "gaps": gaps, "total_gaps": len(gaps)}))
    return p


def _foss_entry(fmt: str, maturity: str = "D1", ceiling: str = "D5",
                applicability: str = "FULL") -> dict:
    return {
        "format": fmt,
        "runtime": "python",
        "dom_applicability": applicability,
        "lane_b_maturity": maturity,
        "lane_b_ceiling": ceiling,
    }


# ── TC-PCL-001-01: Eligibility filter ────────────────────────────────────────

def test_full_format_included(tmp_path):
    """FULL format below ceiling → appears in output."""
    ledger = _make_ledger([_foss_entry("fods", "D1", "D5")], tmp_path)
    glp = _make_gap_ledger([], tmp_path)
    result = gen.run(ledger_path=ledger, gap_ledger_path=glp, dry_run=True)
    assert result["added"] == 1
    assert result["eligible"] >= 1


def test_flat_format_excluded(tmp_path):
    """FLAT format → never generates a gap."""
    ledger = _make_ledger([
        _foss_entry("csv", "D1", "D1", applicability="FLAT"),
        _foss_entry("tsv", "D1", "D1", applicability="FLAT"),
        _foss_entry("ndjson", "D1", "D1", applicability="FLAT"),
    ], tmp_path)
    glp = _make_gap_ledger([], tmp_path)
    result = gen.run(ledger_path=ledger, gap_ledger_path=glp, dry_run=True)
    assert result["added"] == 0


def test_ceiling_format_excluded(tmp_path):
    """Format at its ceiling → no gap generated."""
    ledger = _make_ledger([_foss_entry("fodt", "D5", "D5")], tmp_path)
    glp = _make_gap_ledger([], tmp_path)
    result = gen.run(ledger_path=ledger, gap_ledger_path=glp, dry_run=True)
    assert result["added"] == 0


def test_dotnet_format_excluded(tmp_path):
    """dotnet runtime entries → not included in foss generator output."""
    ledger = _make_ledger([
        {"format": "fods", "runtime": "dotnet", "dom_applicability": "FULL",
         "lane_b_maturity": "D1", "lane_b_ceiling": "D5"},
    ], tmp_path)
    glp = _make_gap_ledger([], tmp_path)
    result = gen.run(ledger_path=ledger, gap_ledger_path=glp, dry_run=True)
    assert result["added"] == 0


def test_fods_and_fodt_both_included(tmp_path):
    """fods and fodt appear in output (FULL applicability, below ceiling)."""
    ledger = _make_ledger([
        _foss_entry("fods", "D1", "D5"),
        _foss_entry("fodt", "D1", "D5"),
    ], tmp_path)
    glp = _make_gap_ledger([], tmp_path)
    result = gen.run(ledger_path=ledger, gap_ledger_path=glp, dry_run=True)
    assert result["added"] == 2
    assert result["eligible"] == 2


# ── TC-PCL-001-02: Gap entry schema and ID ────────────────────────────────────

def test_deterministic_ids(tmp_path):
    """Gap IDs are identical on two separate runs with same ledger state."""
    ledger = _make_ledger([
        _foss_entry("abw", "D1", "D4"),
        _foss_entry("fods", "D3", "D5"),
    ], tmp_path)
    glp1 = tmp_path / "gl1.json"
    glp2 = tmp_path / "gl2.json"
    glp1.write_text(json.dumps({"schema_version": "1.0", "gaps": [], "total_gaps": 0}))
    glp2.write_text(json.dumps({"schema_version": "1.0", "gaps": [], "total_gaps": 0}))

    gen.run(ledger_path=ledger, gap_ledger_path=glp1)
    gen.run(ledger_path=ledger, gap_ledger_path=glp2)

    gaps1 = json.loads(glp1.read_text())["gaps"]
    gaps2 = json.loads(glp2.read_text())["gaps"]
    ids1 = {g["gap_id"] for g in gaps1}
    ids2 = {g["gap_id"] for g in gaps2}
    assert ids1 == ids2


def test_gap_has_lane_b(tmp_path):
    """Each generated gap has lane='B'."""
    ledger = _make_ledger([_foss_entry("abw", "D1", "D4")], tmp_path)
    glp = _make_gap_ledger([], tmp_path)
    gen.run(ledger_path=ledger, gap_ledger_path=glp)
    data = json.loads(glp.read_text())
    for g in data["gaps"]:
        assert g.get("lane") == "B", f"gap {g['gap_id']} missing lane=B"


def test_gap_id_format_is_correct(tmp_path):
    """Gap IDs follow GAP-{FORMAT}-DOM-{TARGET}-{BEHAVIOR}-001 pattern."""
    ledger = _make_ledger([_foss_entry("abw", "D1", "D4")], tmp_path)
    glp = _make_gap_ledger([], tmp_path)
    gen.run(ledger_path=ledger, gap_ledger_path=glp)
    data = json.loads(glp.read_text())
    gap = data["gaps"][0]
    assert gap["gap_id"].startswith("GAP-ABW-DOM-")
    assert gap["gap_id"].endswith("-001")
    assert "D2" in gap["gap_id"]


# ── TC-PCL-001-03: Idempotency ────────────────────────────────────────────────

def test_idempotent(tmp_path):
    """Running generator twice produces zero new entries on second run."""
    ledger = _make_ledger([
        _foss_entry("fods", "D1", "D5"),
        _foss_entry("fodt", "D1", "D5"),
        _foss_entry("abw", "D1", "D4"),
    ], tmp_path)
    glp = _make_gap_ledger([], tmp_path)

    r1 = gen.run(ledger_path=ledger, gap_ledger_path=glp)
    r2 = gen.run(ledger_path=ledger, gap_ledger_path=glp)

    count_after_1 = len(json.loads(glp.read_text())["gaps"])
    count_after_2 = len(json.loads(glp.read_text())["gaps"])

    assert r1["added"] > 0
    assert r2["added"] == 0
    assert r2["skipped"] == r1["added"]
    assert count_after_1 == count_after_2
