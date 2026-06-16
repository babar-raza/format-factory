"""Tests for ods_average_cells_per_row and ods_has_empty_rows (Sprint 20)."""
import pytest
from src.python.ods import (
    write_ods, ods_average_cells_per_row, ods_has_empty_rows,
    OdsDocument, OdsSheet, OdsRow, OdsCell,
)


def _make_ods(tmp_path, name, rows):
    cells = []
    for row_data in rows:
        row_cells = [OdsCell(value=v, value_type="string") for v in row_data]
        cells.append(OdsRow(cells=row_cells))
    sheet = OdsSheet(name="Sheet1", rows=cells)
    doc = OdsDocument(sheets=[sheet])
    p = tmp_path / f"{name}.ods"
    write_ods(doc, str(p))
    return str(p)


class TestOdsAverageCellsPerRow:
    def test_single_row(self, tmp_path):
        p = _make_ods(tmp_path, "s1", [["a", "b", "c"]])
        assert ods_average_cells_per_row(p) == 3.0

    def test_multiple_rows(self, tmp_path):
        p = _make_ods(tmp_path, "m1", [["a", "b"], ["c", "d"], ["e", "f"]])
        assert ods_average_cells_per_row(p) == 2.0

    def test_uneven_rows(self, tmp_path):
        p = _make_ods(tmp_path, "u1", [["a", "b", "c"], ["d"]])
        avg = ods_average_cells_per_row(p)
        assert avg >= 1.0

    def test_invalid_sheet_index(self, tmp_path):
        p = _make_ods(tmp_path, "i1", [["x"]])
        assert ods_average_cells_per_row(p, sheet_index=99) == 0.0

    def test_return_type(self, tmp_path):
        p = _make_ods(tmp_path, "t1", [["a"]])
        assert isinstance(ods_average_cells_per_row(p), float)


class TestOdsHasEmptyRows:
    def test_no_empty_rows(self, tmp_path):
        p = _make_ods(tmp_path, "ne1", [["a", "b"], ["c", "d"]])
        assert ods_has_empty_rows(p) is False

    def test_with_empty_values(self, tmp_path):
        p = _make_ods(tmp_path, "ev1", [["a", "b"], ["", ""], ["c", "d"]])
        assert ods_has_empty_rows(p) is True

    def test_single_cell(self, tmp_path):
        p = _make_ods(tmp_path, "sc1", [["x"]])
        assert isinstance(ods_has_empty_rows(p), bool)

    def test_invalid_sheet_index(self, tmp_path):
        p = _make_ods(tmp_path, "is1", [["x"]])
        assert ods_has_empty_rows(p, sheet_index=99) is False

    def test_return_type(self, tmp_path):
        p = _make_ods(tmp_path, "rt1", [["a"]])
        assert isinstance(ods_has_empty_rows(p), bool)
