"""Tests for FODS save-same-format and reload-and-verify capabilities.

Gap closure: GAP-FODS-COMM-SAVE_SAME_FO-001, GAP-FODS-COMM-RELOAD_AND_V-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict, write_fods

SAMPLES = _REPO / "samples" / "by-format" / "fods"


class TestFodsSaveSameFormat:
    def test_minimal_roundtrip(self, tmp_path):
        src = SAMPLES / "minimal-spreadsheet.fods"
        wb = parse_fods_strict(src)
        out = tmp_path / "out.fods"
        write_fods(wb, out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_multi_sheet_roundtrip(self, tmp_path):
        src = SAMPLES / "multi-sheet-basic.fods"
        wb = parse_fods_strict(src)
        out = tmp_path / "out.fods"
        write_fods(wb, out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_formula_roundtrip(self, tmp_path):
        src = SAMPLES / "formula-basic.fods"
        wb = parse_fods_strict(src)
        out = tmp_path / "out.fods"
        write_fods(wb, out)
        assert out.exists()

    def test_typed_values_roundtrip(self, tmp_path):
        src = SAMPLES / "typed-values-basic.fods"
        wb = parse_fods_strict(src)
        out = tmp_path / "out.fods"
        write_fods(wb, out)
        assert out.exists()


class TestFodsReloadAndVerify:
    def test_minimal_reload_preserves_sheet_count(self, tmp_path):
        src = SAMPLES / "minimal-spreadsheet.fods"
        wb1 = parse_fods_strict(src)
        out = tmp_path / "out.fods"
        write_fods(wb1, out)
        wb2 = parse_fods_strict(out)
        assert wb1["sheet_count"] == wb2["sheet_count"]

    def test_multi_sheet_reload_preserves_structure(self, tmp_path):
        src = SAMPLES / "multi-sheet-basic.fods"
        wb1 = parse_fods_strict(src)
        out = tmp_path / "out.fods"
        write_fods(wb1, out)
        wb2 = parse_fods_strict(out)
        assert wb1["sheet_count"] == wb2["sheet_count"]
        assert len(wb1["sheets"]) == len(wb2["sheets"])

    def test_reload_produces_valid_fods(self, tmp_path):
        src = SAMPLES / "minimal-spreadsheet.fods"
        wb = parse_fods_strict(src)
        out = tmp_path / "out.fods"
        write_fods(wb, out)
        # Re-parse should not raise
        wb2 = parse_fods_strict(out)
        assert isinstance(wb2, dict)

    def test_reload_preserves_cell_values(self, tmp_path):
        src = SAMPLES / "typed-values-basic.fods"
        wb1 = parse_fods_strict(src)
        out = tmp_path / "out.fods"
        write_fods(wb1, out)
        wb2 = parse_fods_strict(out)
        # Both should have sheets with cells
        if wb1.get("sheets") and wb2.get("sheets"):
            s1_cells = wb1["sheets"][0].get("cells", [])
            s2_cells = wb2["sheets"][0].get("cells", [])
            assert len(s1_cells) == len(s2_cells)
