"""Tests for dom_maturity_gap_generator.py (TC-VPR-002, serialized-petting-crab)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from dom_maturity_gap_generator import (  # noqa: E402
    GenerationResult,
    _make_gap_id,
    _next_boundary,
    generate_dom_gaps,
)


def _minimal_ledger(entries: list[dict]) -> list[dict]:
    """Return a minimal ledger list with only the required fields."""
    return [
        {
            "format": e["format"],
            "dom_applicability": e.get("dom_applicability", "FULL"),
            "lane_b_maturity": e.get("lane_b_maturity", "D1"),
            "lane_b_ceiling": e.get("lane_b_ceiling", "D4"),
        }
        for e in entries
    ]


def _write_ledger(tmp_path: Path, entries: list[dict]) -> Path:
    """Write a minimal YAML ledger file and return its path."""
    import yaml
    ledger = _minimal_ledger(entries)
    p = tmp_path / "ledger.yaml"
    p.write_text(yaml.dump(ledger), encoding="utf-8")
    return p


def _write_gap_ledger(tmp_path: Path, gaps: list[dict] | None = None) -> Path:
    """Write a gap-ledger.json with optional pre-existing gaps."""
    p = tmp_path / "gap-ledger.json"
    p.write_text(json.dumps({"gaps": gaps or []}), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------


def test_generates_one_gap_per_format_at_immediate_next_boundary(tmp_path):
    """ABW at D1, ceiling D4 → emits GAP-ABW-DOM-MATURITY-D2-001."""
    ledger_p = _write_ledger(tmp_path, [
        {"format": "abw", "dom_applicability": "FULL", "lane_b_maturity": "D1", "lane_b_ceiling": "D4"},
    ])
    gap_p = _write_gap_ledger(tmp_path)

    result = generate_dom_gaps(
        ledger_path=ledger_p, gap_ledger_path=gap_p, dry_run=False
    )

    assert result.added == 1, f"Expected 1 added, got {result.added}"
    assert result.errors == []
    data = json.loads(gap_p.read_text(encoding="utf-8"))
    gap_ids = [g["gap_id"] for g in data["gaps"]]
    assert "GAP-ABW-DOM-MATURITY-D2-001" in gap_ids


def test_supplemental_true_on_all_generated_gaps(tmp_path):
    """All generated gaps must have supplemental=True."""
    ledger_p = _write_ledger(tmp_path, [
        {"format": "fodg", "dom_applicability": "FULL", "lane_b_maturity": "D1", "lane_b_ceiling": "D4"},
        {"format": "sylk", "dom_applicability": "PARTIAL", "lane_b_maturity": "D1", "lane_b_ceiling": "D3"},
    ])
    gap_p = _write_gap_ledger(tmp_path)

    generate_dom_gaps(ledger_path=ledger_p, gap_ledger_path=gap_p, dry_run=False)

    data = json.loads(gap_p.read_text(encoding="utf-8"))
    for gap in data["gaps"]:
        assert gap.get("supplemental") is True, f"Gap {gap['gap_id']} missing supplemental=True"


def test_deepening_lane_dom_on_all_generated_gaps(tmp_path):
    """All generated gaps must have deepening_lane='dom'."""
    ledger_p = _write_ledger(tmp_path, [
        {"format": "fodt", "dom_applicability": "FULL", "lane_b_maturity": "D2", "lane_b_ceiling": "D5"},
    ])
    gap_p = _write_gap_ledger(tmp_path)

    generate_dom_gaps(ledger_path=ledger_p, gap_ledger_path=gap_p, dry_run=False)

    data = json.loads(gap_p.read_text(encoding="utf-8"))
    for gap in data["gaps"]:
        assert gap.get("deepening_lane") == "dom", f"Gap {gap['gap_id']} has wrong lane"


def test_idempotent_rerun_produces_no_changes(tmp_path):
    """Run twice — second run returns added=0, updated=0, closed=0, unchanged=N."""
    ledger_p = _write_ledger(tmp_path, [
        {"format": "ods", "dom_applicability": "FULL", "lane_b_maturity": "D2", "lane_b_ceiling": "D5"},
    ])
    gap_p = _write_gap_ledger(tmp_path)

    first = generate_dom_gaps(ledger_path=ledger_p, gap_ledger_path=gap_p, dry_run=False)
    assert first.added == 1

    second = generate_dom_gaps(ledger_path=ledger_p, gap_ledger_path=gap_p, dry_run=False)
    assert second.added == 0
    assert second.updated == 0
    assert second.closed == 0
    assert second.unchanged == 1


def test_format_at_ceiling_emits_no_gap(tmp_path):
    """Format at its ceiling → no new gap emitted."""
    ledger_p = _write_ledger(tmp_path, [
        {"format": "fods", "dom_applicability": "FULL", "lane_b_maturity": "D5", "lane_b_ceiling": "D5"},
    ])
    gap_p = _write_gap_ledger(tmp_path)

    result = generate_dom_gaps(ledger_path=ledger_p, gap_ledger_path=gap_p, dry_run=False)
    assert result.added == 0
    data = json.loads(gap_p.read_text(encoding="utf-8"))
    assert len(data["gaps"]) == 0


def test_format_non_applicable_emits_no_gap(tmp_path):
    """CSV (FLAT applicability) → no gap emitted."""
    ledger_p = _write_ledger(tmp_path, [
        {"format": "csv", "dom_applicability": "FLAT", "lane_b_maturity": "D1", "lane_b_ceiling": "D1"},
    ])
    gap_p = _write_gap_ledger(tmp_path)

    result = generate_dom_gaps(ledger_path=ledger_p, gap_ledger_path=gap_p, dry_run=False)
    assert result.added == 0
    data = json.loads(gap_p.read_text(encoding="utf-8"))
    assert len(data["gaps"]) == 0


def test_does_not_modify_non_supplemental_existing_gaps(tmp_path):
    """Non-supplemental gaps in the ledger must not be touched."""
    existing_gap = {
        "gap_id": "GAP-FODS-FEATURE-001",
        "format": "FODS",
        "deepening_lane": "feature",
        "supplemental": False,
        "status": "open",
        "dom_maturity_boundary": None,
    }
    ledger_p = _write_ledger(tmp_path, [
        {"format": "fods", "dom_applicability": "FULL", "lane_b_maturity": "D3", "lane_b_ceiling": "D5"},
    ])
    gap_p = _write_gap_ledger(tmp_path, gaps=[existing_gap])

    generate_dom_gaps(ledger_path=ledger_p, gap_ledger_path=gap_p, dry_run=False)

    data = json.loads(gap_p.read_text(encoding="utf-8"))
    # Original non-supplemental gap must be present and unmodified
    orig = next(g for g in data["gaps"] if g["gap_id"] == "GAP-FODS-FEATURE-001")
    assert orig["status"] == "open"
    assert orig["deepening_lane"] == "feature"


def test_gap_id_stable_across_reruns(tmp_path):
    """Same format+boundary always produces same gap_id."""
    assert _make_gap_id("abw", "D2") == "GAP-ABW-DOM-MATURITY-D2-001"
    assert _make_gap_id("FODS", "D4") == "GAP-FODS-DOM-MATURITY-D4-001"
    assert _make_gap_id("ods", "D3") == "GAP-ODS-DOM-MATURITY-D3-001"


def test_next_boundary_correct():
    """_next_boundary returns the immediate next level, None at ceiling."""
    assert _next_boundary("D1", "D4") == "D2"
    assert _next_boundary("D3", "D5") == "D4"
    assert _next_boundary("D4", "D4") is None
    assert _next_boundary("D5", "D5") is None
    assert _next_boundary("D0", "D2") == "D1"


def test_maturity_advancement_closes_old_gap(tmp_path):
    """If format advances past a boundary, the old D2 gap is closed, new D3 gap added."""
    # Simulate: ABW had a D2 gap open, now maturity advanced to D2 → close D2, open D3
    old_d2_gap = {
        "gap_id": "GAP-ABW-DOM-MATURITY-D2-001",
        "format": "ABW",
        "deepening_lane": "dom",
        "supplemental": True,
        "status": "open",
        "dom_maturity_boundary": "D2",
    }
    ledger_p = _write_ledger(tmp_path, [
        {"format": "abw", "dom_applicability": "FULL", "lane_b_maturity": "D2", "lane_b_ceiling": "D4"},
    ])
    gap_p = _write_gap_ledger(tmp_path, gaps=[old_d2_gap])

    result = generate_dom_gaps(ledger_path=ledger_p, gap_ledger_path=gap_p, dry_run=False)

    assert result.closed == 1  # old D2 gap closed
    assert result.added == 1   # new D3 gap added

    data = json.loads(gap_p.read_text(encoding="utf-8"))
    gap_map = {g["gap_id"]: g for g in data["gaps"]}
    assert gap_map["GAP-ABW-DOM-MATURITY-D2-001"]["status"] == "closed"
    assert gap_map["GAP-ABW-DOM-MATURITY-D3-001"]["status"] == "open"


def test_dry_run_does_not_write_to_ledger(tmp_path):
    """dry_run=True must not modify gap-ledger.json."""
    ledger_p = _write_ledger(tmp_path, [
        {"format": "odt", "dom_applicability": "FULL", "lane_b_maturity": "D1", "lane_b_ceiling": "D5"},
    ])
    gap_p = _write_gap_ledger(tmp_path)
    original_content = gap_p.read_text(encoding="utf-8")

    result = generate_dom_gaps(ledger_path=ledger_p, gap_ledger_path=gap_p, dry_run=True)

    assert result.added == 1
    assert gap_p.read_text(encoding="utf-8") == original_content, "dry_run must not modify gap-ledger.json"


def test_format_filter_restricts_to_single_format(tmp_path):
    """--format FODS only generates gaps for FODS, not other formats."""
    ledger_p = _write_ledger(tmp_path, [
        {"format": "fods", "dom_applicability": "FULL", "lane_b_maturity": "D3", "lane_b_ceiling": "D5"},
        {"format": "ods", "dom_applicability": "FULL", "lane_b_maturity": "D2", "lane_b_ceiling": "D5"},
    ])
    gap_p = _write_gap_ledger(tmp_path)

    result = generate_dom_gaps(
        ledger_path=ledger_p, gap_ledger_path=gap_p,
        dry_run=False, format_filter="FODS"
    )

    assert result.added == 1
    data = json.loads(gap_p.read_text(encoding="utf-8"))
    gap_ids = [g["gap_id"] for g in data["gaps"]]
    assert any("FODS" in gid for gid in gap_ids)
    assert not any("ODS" in gid and "FODS" not in gid for gid in gap_ids)
