"""
test_r84_fods_csv_export.py

R84 Train G: Tests for new FODS APIs:
- workbook_to_csv(workbook, sheet_name=None)
- workbook_get_cell_value(workbook, sheet_name, row_index, col_index)

Sprint: FORMAT-FACTORY-R84-BROAD-CLOSURE-RAW-LOGS-FINAL-AUTHORITY-FODS-FODT-ZST-NEXTFORMAT-ADVANCEMENT-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.neutral_model import workbook_to_csv, workbook_get_cell_value


def _make_cell(value, value_type="string"):
    return {"value": value, "value_type": value_type}


def _make_row(cells):
    return {"cells": cells}


def _make_sheet(name, rows=None):
    return {"name": name, "rows": rows or []}


def _make_workbook(sheets=None):
    return {"sheets": sheets or []}


class TestWorkbookToCsv:
    def test_empty_workbook_returns_empty_string(self):
        wb = _make_workbook()
        result = workbook_to_csv(wb)
        assert result == ""

    def test_single_cell_sheet(self):
        wb = _make_workbook([
            _make_sheet("Sheet1", [_make_row([_make_cell("hello")])])
        ])
        result = workbook_to_csv(wb)
        assert "hello" in result

    def test_csv_uses_crlf_endings(self):
        wb = _make_workbook([
            _make_sheet("Sheet1", [
                _make_row([_make_cell("a"), _make_cell("b")]),
                _make_row([_make_cell("c"), _make_cell("d")]),
            ])
        ])
        result = workbook_to_csv(wb)
        assert "\r\n" in result

    def test_multiple_rows_each_on_own_line(self):
        wb = _make_workbook([
            _make_sheet("Sheet1", [
                _make_row([_make_cell("r1c1"), _make_cell("r1c2")]),
                _make_row([_make_cell("r2c1"), _make_cell("r2c2")]),
            ])
        ])
        result = workbook_to_csv(wb)
        lines = [l for l in result.split("\r\n") if l]
        assert len(lines) == 2

    def test_named_sheet_selected(self):
        wb = _make_workbook([
            _make_sheet("Sheet1", [_make_row([_make_cell("from_sheet1")])]),
            _make_sheet("Sheet2", [_make_row([_make_cell("from_sheet2")])]),
        ])
        result = workbook_to_csv(wb, sheet_name="Sheet2")
        assert "from_sheet2" in result
        assert "from_sheet1" not in result

    def test_missing_sheet_name_returns_empty(self):
        wb = _make_workbook([_make_sheet("Sheet1", [])])
        result = workbook_to_csv(wb, sheet_name="NoSuchSheet")
        assert result == ""

    def test_first_sheet_used_when_no_name(self):
        wb = _make_workbook([
            _make_sheet("First", [_make_row([_make_cell("first_val")])]),
            _make_sheet("Second", [_make_row([_make_cell("second_val")])]),
        ])
        result = workbook_to_csv(wb)
        assert "first_val" in result
        assert "second_val" not in result

    def test_numeric_cell(self):
        wb = _make_workbook([
            _make_sheet("Sheet1", [_make_row([_make_cell(42, "numeric")])])
        ])
        result = workbook_to_csv(wb)
        assert "42" in result


class TestWorkbookGetCellValue:
    def test_get_first_cell(self):
        wb = _make_workbook([
            _make_sheet("Sheet1", [_make_row([_make_cell("target")])])
        ])
        result = workbook_get_cell_value(wb, "Sheet1", 0, 0)
        assert result == "target"

    def test_get_second_column(self):
        wb = _make_workbook([
            _make_sheet("Sheet1", [_make_row([_make_cell("a"), _make_cell("b")])])
        ])
        result = workbook_get_cell_value(wb, "Sheet1", 0, 1)
        assert result == "b"

    def test_out_of_range_row_returns_none(self):
        wb = _make_workbook([_make_sheet("Sheet1", [])])
        result = workbook_get_cell_value(wb, "Sheet1", 99, 0)
        assert result is None

    def test_missing_sheet_returns_none(self):
        wb = _make_workbook([_make_sheet("Sheet1", [])])
        result = workbook_get_cell_value(wb, "NoSheet", 0, 0)
        assert result is None

    def test_named_sheet_lookup(self):
        wb = _make_workbook([
            _make_sheet("Sheet1", [_make_row([_make_cell("s1")])]),
            _make_sheet("Sheet2", [_make_row([_make_cell("s2")])]),
        ])
        result = workbook_get_cell_value(wb, "Sheet2", 0, 0)
        assert result == "s2"
