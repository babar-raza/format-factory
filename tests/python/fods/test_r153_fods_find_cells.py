"""
test_r153_fods_find_cells.py

Sprint: FORMAT-FACTORY-AUTHORITY-GATED-PRODUCT-PROGRESS-AND-FORMAT-BACKFILL-MEGA-TRAIN-001
Added: 2026-06-09

Tests for new FODS API:
- workbook_find_cells(workbook, value, case_sensitive=False) -> list[dict]

Authority: P6 (SAL-FODS-00001: ODF 1.3 spreadsheet MIME type
application/vnd.oasis.opendocument.spreadsheet-flat-xml)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.neutral_model import workbook_find_cells


def _cell(value=None):
    if value is None:
        return {"value": None}
    return {"value": value}


def _row(cells):
    return {"cells": cells}


def _sheet(name, rows):
    return {"name": name, "rows": rows}


def _workbook(sheets):
    return {"sheets": sheets}


class TestWorkbookFindCellsBasic:
    """workbook_find_cells: basic search behavior."""

    def test_empty_workbook_returns_empty(self):
        wb = _workbook([])
        result = workbook_find_cells(wb, "x")
        assert result == []

    def test_finds_string_cell(self):
        wb = _workbook([_sheet("Sheet1", [_row([_cell("hello"), _cell("world")])])])
        result = workbook_find_cells(wb, "hello")
        assert len(result) == 1
        assert result[0]["value"] == "hello"

    def test_finds_numeric_cell(self):
        wb = _workbook([_sheet("Sheet1", [_row([_cell(42), _cell(100)])])])
        result = workbook_find_cells(wb, 42)
        assert len(result) == 1
        assert result[0]["value"] == 42

    def test_no_match_returns_empty(self):
        wb = _workbook([_sheet("Sheet1", [_row([_cell("a"), _cell("b")])])])
        result = workbook_find_cells(wb, "z")
        assert result == []

    def test_none_cells_not_matched(self):
        wb = _workbook([_sheet("Sheet1", [_row([_cell(None), _cell(None)])])])
        result = workbook_find_cells(wb, None)
        assert result == []

    def test_result_dict_has_required_keys(self):
        wb = _workbook([_sheet("Data", [_row([_cell("target")])])])
        result = workbook_find_cells(wb, "target")
        assert len(result) == 1
        entry = result[0]
        assert "sheet_name" in entry
        assert "row_index" in entry
        assert "col_index" in entry
        assert "value" in entry

    def test_result_has_correct_indices(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("a"), _cell("b"), _cell("c")]),
            _row([_cell("d"), _cell("target"), _cell("f")]),
        ])])
        result = workbook_find_cells(wb, "target")
        assert len(result) == 1
        assert result[0]["row_index"] == 1
        assert result[0]["col_index"] == 1

    def test_result_has_sheet_name(self):
        wb = _workbook([_sheet("MySheet", [_row([_cell("needle")])])])
        result = workbook_find_cells(wb, "needle")
        assert result[0]["sheet_name"] == "MySheet"


class TestWorkbookFindCellsMultipleMatches:
    """workbook_find_cells: multiple matches across sheets and rows."""

    def test_finds_multiple_cells_in_same_sheet(self):
        wb = _workbook([_sheet("Sheet1", [
            _row([_cell("alpha"), _cell("beta")]),
            _row([_cell("alpha"), _cell("gamma")]),
        ])])
        result = workbook_find_cells(wb, "alpha")
        assert len(result) == 2

    def test_finds_cells_across_sheets(self):
        wb = _workbook([
            _sheet("Sheet1", [_row([_cell("common")])]),
            _sheet("Sheet2", [_row([_cell("common")])]),
        ])
        result = workbook_find_cells(wb, "common")
        assert len(result) == 2
        sheet_names = {r["sheet_name"] for r in result}
        assert "Sheet1" in sheet_names
        assert "Sheet2" in sheet_names


class TestWorkbookFindCellsCaseSensitivity:
    """workbook_find_cells: case sensitivity for string search."""

    def test_case_insensitive_by_default(self):
        wb = _workbook([_sheet("S1", [_row([_cell("Hello")])])])
        result = workbook_find_cells(wb, "hello")
        assert len(result) == 1

    def test_case_sensitive_no_match(self):
        wb = _workbook([_sheet("S1", [_row([_cell("Hello")])])])
        result = workbook_find_cells(wb, "hello", case_sensitive=True)
        assert result == []

    def test_case_sensitive_match(self):
        wb = _workbook([_sheet("S1", [_row([_cell("Hello")])])])
        result = workbook_find_cells(wb, "Hello", case_sensitive=True)
        assert len(result) == 1

    def test_exported_from_package(self):
        """workbook_find_cells must be importable from fods package."""
        from src.python.fods import workbook_find_cells as wfc
        assert callable(wfc)
