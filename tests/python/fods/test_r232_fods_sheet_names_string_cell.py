"""Tests for fods_sheet_names and fods_string_cell_count (Sprint 20)."""
import os, tempfile, pytest
from src.python.fods import parse_fods_strict, fods_sheet_names, fods_string_cell_count, write_fods


def _make_wb(sheets):
    """Build a minimal FODS workbook dict."""
    wb = {"sheets": []}
    for name, rows in sheets:
        sheet = {"name": name, "rows": []}
        for row_cells in rows:
            cells = []
            for val in row_cells:
                if isinstance(val, (int, float)):
                    cells.append({"value": str(val), "value_type": "float"})
                else:
                    cells.append({"value": val, "value_type": "string"})
            sheet["rows"].append({"cells": cells})
        wb["sheets"].append(sheet)
    return wb


class TestFodsSheetNames:
    def test_single_sheet(self):
        wb = _make_wb([("Sheet1", [["a"]])])
        assert fods_sheet_names(wb) == ["Sheet1"]

    def test_multiple_sheets(self):
        wb = _make_wb([("A", []), ("B", []), ("C", [])])
        assert fods_sheet_names(wb) == ["A", "B", "C"]

    def test_empty_workbook(self):
        assert fods_sheet_names({"sheets": []}) == []

    def test_return_type(self):
        wb = _make_wb([("X", [])])
        result = fods_sheet_names(wb)
        assert isinstance(result, list)
        assert all(isinstance(n, str) for n in result)

    def test_preserves_order(self):
        wb = _make_wb([("Z", []), ("A", []), ("M", [])])
        assert fods_sheet_names(wb) == ["Z", "A", "M"]


class TestFodsStringCellCount:
    def test_all_strings(self):
        wb = _make_wb([("S1", [["a", "b", "c"]])])
        assert fods_string_cell_count(wb) == 3

    def test_mixed_types(self):
        wb = _make_wb([("S1", [["a", 1, "b", 2]])])
        assert fods_string_cell_count(wb) == 2

    def test_no_strings(self):
        wb = _make_wb([("S1", [[1, 2, 3]])])
        assert fods_string_cell_count(wb) == 0

    def test_empty_workbook(self):
        assert fods_string_cell_count({"sheets": []}) == 0

    def test_return_type(self):
        wb = _make_wb([("S1", [["x"]])])
        assert isinstance(fods_string_cell_count(wb), int)
