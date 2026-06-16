"""Tests for ods_merged_cell_count and ods_avg_cells_per_sheet (Sprint 24)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import ods_merged_cell_count, ods_avg_cells_per_sheet, write_ods, OdsDocument, OdsSheet, OdsRow, OdsCell


def _make_ods(tmp_path, name, rows_data):
    cells = []
    for row_data in rows_data:
        row_cells = [OdsCell(value=v, value_type="string") for v in row_data]
        cells.append(OdsRow(cells=row_cells))
    sheet = OdsSheet(name="Sheet1", rows=cells)
    doc = OdsDocument(sheets=[sheet])
    p = tmp_path / f"{name}.ods"
    write_ods(doc, str(p))
    return str(p)


class TestOdsMergedCellCount:
    def test_return_type(self, tmp_path):
        p = _make_ods(tmp_path, "rt", [["a", "b"]])
        result = ods_merged_cell_count(p)
        assert isinstance(result, int)

    def test_no_merged_cells(self, tmp_path):
        p = _make_ods(tmp_path, "nm", [["a", "b"], ["c", "d"]])
        result = ods_merged_cell_count(p)
        assert result == 0

    def test_nonnegative(self, tmp_path):
        p = _make_ods(tmp_path, "nn", [["x"]])
        assert ods_merged_cell_count(p) >= 0

    def test_empty_sheet(self, tmp_path):
        p = _make_ods(tmp_path, "es", [])
        result = ods_merged_cell_count(p)
        assert result == 0

    def test_single_cell(self, tmp_path):
        p = _make_ods(tmp_path, "sc", [["only"]])
        assert ods_merged_cell_count(p) == 0


class TestOdsAvgCellsPerSheet:
    def test_return_type(self, tmp_path):
        p = _make_ods(tmp_path, "rt2", [["a", "b"]])
        result = ods_avg_cells_per_sheet(p)
        assert isinstance(result, float)

    def test_two_cells_one_sheet(self, tmp_path):
        p = _make_ods(tmp_path, "tc", [["a", "b"]])
        result = ods_avg_cells_per_sheet(p)
        assert result == 2.0

    def test_nonnegative(self, tmp_path):
        p = _make_ods(tmp_path, "nn2", [["x"]])
        assert ods_avg_cells_per_sheet(p) >= 0.0

    def test_empty_returns_zero(self, tmp_path):
        p = _make_ods(tmp_path, "ez", [])
        result = ods_avg_cells_per_sheet(p)
        assert result == 0.0

    def test_four_cells(self, tmp_path):
        p = _make_ods(tmp_path, "fc", [["a", "b"], ["c", "d"]])
        result = ods_avg_cells_per_sheet(p)
        assert result == 4.0
