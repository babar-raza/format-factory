"""Tests for ods_min_cell_value_length and ods_all_sheets_have_data (Sprint 32)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ods import ods_min_cell_value_length, ods_all_sheets_have_data, write_ods
from src.python.ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell


def _make_ods(tmp_path, name, sheets_config):
    """Create ODS file. sheets_config: list of (sheet_name, {(r,c): val})."""
    sheets = []
    for sname, cells in sheets_config:
        max_r = max((r for (r, c) in cells), default=-1) + 1 if cells else 0
        max_c = max((c for (r, c) in cells), default=-1) + 1 if cells else 0
        rows = []
        for ri in range(max_r):
            row_cells = []
            for ci in range(max_c):
                val = cells.get((ri, ci))
                row_cells.append(OdsCell(value=val, value_type="string" if val else ""))
            rows.append(OdsRow(cells=row_cells))
        sheets.append(OdsSheet(name=sname, rows=rows))
    doc = OdsDocument(sheets=sheets)
    path = tmp_path / f"{name}.ods"
    write_ods(doc, str(path))
    return path


class TestOdsMinCellValueLength:
    def test_return_type(self, tmp_path):
        f = _make_ods(tmp_path, "rt", [("S1", {(0, 0): "abc"})])
        assert isinstance(ods_min_cell_value_length(f), int)

    def test_exact_min(self, tmp_path):
        # "abc"(3), "de"(2) -> min = 2
        f = _make_ods(tmp_path, "em", [("S1", {(0, 0): "abc", (0, 1): "de"})])
        assert ods_min_cell_value_length(f) == 2

    def test_single_cell(self, tmp_path):
        f = _make_ods(tmp_path, "sc", [("S1", {(0, 0): "hello"})])
        assert ods_min_cell_value_length(f) == 5

    def test_empty_sheet_returns_zero(self, tmp_path):
        f = _make_ods(tmp_path, "empty", [("S1", {})])
        assert ods_min_cell_value_length(f) == 0

    def test_nonnegative(self, tmp_path):
        f = _make_ods(tmp_path, "nn", [("S1", {(0, 0): "x"})])
        assert ods_min_cell_value_length(f) >= 0


class TestOdsAllSheetsHaveData:
    def test_return_type(self, tmp_path):
        f = _make_ods(tmp_path, "rt2", [("S1", {(0, 0): "x"})])
        assert isinstance(ods_all_sheets_have_data(f), bool)

    def test_single_sheet_with_data_true(self, tmp_path):
        f = _make_ods(tmp_path, "sd", [("S1", {(0, 0): "data"})])
        assert ods_all_sheets_have_data(f) is True

    def test_two_sheets_both_have_data_true(self, tmp_path):
        f = _make_ods(tmp_path, "ts", [("S1", {(0, 0): "a"}), ("S2", {(0, 0): "b"})])
        assert ods_all_sheets_have_data(f) is True

    def test_empty_sheet_returns_false(self, tmp_path):
        f = _make_ods(tmp_path, "es", [("S1", {})])
        assert ods_all_sheets_have_data(f) is False

    def test_one_empty_among_nonempty_returns_false(self, tmp_path):
        # S1 has data, S2 is empty -> False
        f = _make_ods(tmp_path, "mixed", [("S1", {(0, 0): "data"}), ("S2", {})])
        assert ods_all_sheets_have_data(f) is False
