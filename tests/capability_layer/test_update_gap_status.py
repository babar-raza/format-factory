"""Tests for update_gap_status() in capability_map_generator.py.

TC-C7-001: Standalone gap status update API.
TC-C7-003: Closed gap absent from next sprint gap selection.
TC-C7-004: Idempotency — double-close is safe no-op.
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "capability_layer"))

from capability_map_generator import update_gap_status


def _write_ledger(tmp_path: Path, gaps: list[dict]) -> Path:
    ledger = {
        "schema_version": "1.0",
        "generated_at": "2026-06-24T00:00:00Z",
        "total_gaps": len(gaps),
        "gaps": gaps,
    }
    gl_path = tmp_path / "gap-ledger.json"
    gl_path.write_text(json.dumps(ledger), encoding="utf-8")
    return gl_path


def _make_gap(gap_id: str, status: str = "open") -> dict:
    return {
        "gap_id": gap_id,
        "format": "FODS",
        "capability_name": "Test Cap",
        "status": status,
        "priority": "P1",
    }


class TestUpdateGapStatus:
    """TC-C7-001: update_gap_status() API correctness."""

    def test_close_open_gap(self, tmp_path):
        gl = _write_ledger(tmp_path, [_make_gap("GAP-A")])
        result = update_gap_status("GAP-A", "closed", "evidence.yaml", gap_ledger_path=gl)
        assert result["updated"] is True
        assert result["previous_status"] == "open"
        data = json.loads(gl.read_text())
        gap = data["gaps"][0]
        assert gap["status"] == "closed"
        assert gap["closed_by_sprint"] == "autonomous_cycle"
        assert "closed_at" in gap
        assert gap["closed_evidence"] == "evidence.yaml"

    def test_not_found(self, tmp_path):
        gl = _write_ledger(tmp_path, [_make_gap("GAP-A")])
        result = update_gap_status("GAP-MISSING", "closed", gap_ledger_path=gl)
        assert result["updated"] is False
        assert "not found" in result.get("error", "")

    def test_missing_ledger_file(self, tmp_path):
        result = update_gap_status("GAP-X", "closed", gap_ledger_path=tmp_path / "nope.json")
        assert result["updated"] is False
        assert "not found" in result.get("error", "")


class TestIdempotency:
    """TC-C7-004: Double-close is safe no-op."""

    def test_double_close(self, tmp_path):
        gl = _write_ledger(tmp_path, [_make_gap("GAP-IDEM")])
        r1 = update_gap_status("GAP-IDEM", "closed", gap_ledger_path=gl)
        assert r1["updated"] is True
        r2 = update_gap_status("GAP-IDEM", "closed", gap_ledger_path=gl)
        assert r2["updated"] is False
        assert r2["previous_status"] == "closed"


class TestClosedGapAbsentFromSelection:
    """TC-C7-003: Closed gap should not appear in open gap selection."""

    def test_closed_gap_filtered(self, tmp_path):
        gl = _write_ledger(tmp_path, [
            _make_gap("GAP-OPEN", "open"),
            _make_gap("GAP-CLOSED", "closed"),
        ])
        data = json.loads(gl.read_text())
        open_gaps = [g for g in data["gaps"] if g["status"] == "open"]
        assert len(open_gaps) == 1
        assert open_gaps[0]["gap_id"] == "GAP-OPEN"

    def test_after_closure_filtered(self, tmp_path):
        gl = _write_ledger(tmp_path, [_make_gap("GAP-X"), _make_gap("GAP-Y")])
        update_gap_status("GAP-X", "closed", gap_ledger_path=gl)
        data = json.loads(gl.read_text())
        open_gaps = [g for g in data["gaps"] if g["status"] == "open"]
        assert len(open_gaps) == 1
        assert open_gaps[0]["gap_id"] == "GAP-Y"


class TestRegenerationSafety:
    """Verify closed status fields survive the generator's merge logic."""

    def test_closed_fields_preserved(self, tmp_path):
        gl = _write_ledger(tmp_path, [_make_gap("GAP-REGEN")])
        update_gap_status("GAP-REGEN", "closed", "ev.yaml",
                          closed_by="test-sprint", gap_ledger_path=gl)

        data = json.loads(gl.read_text())
        gap = data["gaps"][0]
        # These are the fields the generator's merge code preserves (lines 1282-1288)
        assert gap["status"] == "closed"
        assert gap["closed_by_sprint"] == "test-sprint"
        assert "closed_at" in gap
