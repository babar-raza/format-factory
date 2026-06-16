"""Tests for ods_total_cell_count and ods_sheet_count.

Product deepening: ODS analytics — TC-H3-002-ODS / PDC-ODS-TOTAL-CELL-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ods import (
    ods_total_cell_count,
    ods_sheet_count,
    parse_ods_strict,
    write_ods,
    set_cell_value,
    add_sheet,
)


def _make_ods(tmp_path, name, sheets_config):
    """Create an ODS file. sheets_config: list of (sheet_name, {(r,c): val})."""
    doc = parse_ods_strict.__wrapped__ if hasattr(parse_ods_strict, '__wrapped__') else None
    # Build from scratch using the writer API
    from src.python.ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell
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


class TestOdsTotalCellCount:
    def test_single_cell(self, tmp_path):
        f = _make_ods(tmp_path, "one", [("Sheet1", {(0, 0): "a"})])
        assert ods_total_cell_count(f) == 1

    def test_2x3_grid(self, tmp_path):
        cells = {(r, c): f"v{r}{c}" for r in range(2) for c in range(3)}
        f = _make_ods(tmp_path, "grid", [("Sheet1", cells)])
        assert ods_total_cell_count(f) == 6

    def test_empty_sheet(self, tmp_path):
        f = _make_ods(tmp_path, "empty", [("Sheet1", {})])
        assert ods_total_cell_count(f) == 0

    def test_returns_int(self, tmp_path):
        f = _make_ods(tmp_path, "type", [("Sheet1", {(0, 0): "x"})])
        assert isinstance(ods_total_cell_count(f), int)

    def test_invalid_sheet_index(self, tmp_path):
        f = _make_ods(tmp_path, "inv", [("Sheet1", {(0, 0): "a"})])
        assert ods_total_cell_count(f, sheet_index=5) == 0

    def test_ragged_rows(self, tmp_path):
        cells = {(0, 0): "a", (0, 1): "b", (1, 0): "c"}
        f = _make_ods(tmp_path, "ragged", [("Sheet1", cells)])
        result = ods_total_cell_count(f)
        assert result >= 3


class TestOdsSheetCount:
    def test_single_sheet(self, tmp_path):
        f = _make_ods(tmp_path, "one_s", [("Sheet1", {(0, 0): "a"})])
        assert ods_sheet_count(f) == 1

    def test_two_sheets(self, tmp_path):
        f = _make_ods(tmp_path, "two_s", [
            ("Sheet1", {(0, 0): "a"}),
            ("Sheet2", {(0, 0): "b"}),
        ])
        assert ods_sheet_count(f) == 2

    def test_three_sheets(self, tmp_path):
        f = _make_ods(tmp_path, "three_s", [
            ("A", {(0, 0): "1"}),
            ("B", {(0, 0): "2"}),
            ("C", {(0, 0): "3"}),
        ])
        assert ods_sheet_count(f) == 3

    def test_returns_int(self, tmp_path):
        f = _make_ods(tmp_path, "type_s", [("S", {(0, 0): "x"})])
        assert isinstance(ods_sheet_count(f), int)
