"""
test_r57_fods_stats.py — R57 Train E: workbook_stats() capability tests.

Verifies the new workbook_stats() function added to format-factory-fods neutral_model.py.
Tests cover: empty workbook, single-sheet, multi-sheet, formula cells, per-sheet breakdown.

R57 Sprint: FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from fods.neutral_model import workbook_stats


def _make_cell(value=None, formula=None):
    c = {}
    if value is not None:
        c["value"] = value
    if formula is not None:
        c["formula"] = formula
    return c


def _make_row(cells, index=0):
    return {"index": index, "cells": cells}


def _make_sheet(name, rows, index=0):
    return {"name": name, "index": index, "row_count": len(rows), "rows": rows}


def _make_workbook(sheets):
    return {
        "format_id": "fods",
        "spec_version": "1.0",
        "odf_version_attr": "1.3",
        "mimetype": "application/vnd.oasis.opendocument.spreadsheet-flat-xml",
        "sheet_count": len(sheets),
        "sheets": sheets,
        "warnings": [],
        "unsupported_features": [],
        "parse_errors": [],
    }


class TestWorkbookStatsEmpty:
    """workbook_stats on an empty workbook."""

    def test_empty_workbook_zero_counts(self):
        wb = _make_workbook([])
        stats = workbook_stats(wb)
        assert stats["sheet_count"] == 0
        assert stats["total_rows"] == 0
        assert stats["total_cells"] == 0
        assert stats["non_empty_cells"] == 0
        assert stats["formula_cells"] == 0
        assert stats["per_sheet"] == []

    def test_empty_sheet_zero_counts(self):
        sheet = _make_sheet("Sheet1", [])
        wb = _make_workbook([sheet])
        stats = workbook_stats(wb)
        assert stats["sheet_count"] == 1
        assert stats["total_rows"] == 0
        assert stats["total_cells"] == 0
        assert stats["non_empty_cells"] == 0
        assert stats["formula_cells"] == 0

    def test_empty_sheet_per_sheet_entry(self):
        sheet = _make_sheet("Sheet1", [])
        wb = _make_workbook([sheet])
        stats = workbook_stats(wb)
        assert len(stats["per_sheet"]) == 1
        ps = stats["per_sheet"][0]
        assert ps["name"] == "Sheet1"
        assert ps["row_count"] == 0
        assert ps["total_cells"] == 0

    def test_empty_row_zero_cells(self):
        row = _make_row([])
        sheet = _make_sheet("Sheet1", [row])
        wb = _make_workbook([sheet])
        stats = workbook_stats(wb)
        assert stats["total_rows"] == 1
        assert stats["total_cells"] == 0


class TestWorkbookStatsSingleSheet:
    """workbook_stats on a single-sheet workbook."""

    def test_all_cells_empty(self):
        cells = [_make_cell(), _make_cell(), _make_cell()]
        row = _make_row(cells)
        sheet = _make_sheet("Sheet1", [row])
        wb = _make_workbook([sheet])
        stats = workbook_stats(wb)
        assert stats["total_cells"] == 3
        assert stats["non_empty_cells"] == 0
        assert stats["formula_cells"] == 0

    def test_some_cells_non_empty(self):
        cells = [_make_cell("hello"), _make_cell(42), _make_cell()]
        row = _make_row(cells)
        sheet = _make_sheet("Sheet1", [row])
        wb = _make_workbook([sheet])
        stats = workbook_stats(wb)
        assert stats["total_cells"] == 3
        assert stats["non_empty_cells"] == 2

    def test_formula_cells_counted(self):
        cells = [
            _make_cell(10, formula="of:=[.A1]+[.B1]"),
            _make_cell(20),
            _make_cell(30, formula="of:=SUM([.A1]:[.B1])"),
        ]
        row = _make_row(cells)
        sheet = _make_sheet("Sheet1", [row])
        wb = _make_workbook([sheet])
        stats = workbook_stats(wb)
        assert stats["formula_cells"] == 2

    def test_formula_cell_also_counted_as_non_empty(self):
        cells = [_make_cell(10, formula="of:=[.A1]+1")]
        row = _make_row(cells)
        sheet = _make_sheet("Sheet1", [row])
        wb = _make_workbook([sheet])
        stats = workbook_stats(wb)
        assert stats["non_empty_cells"] == 1
        assert stats["formula_cells"] == 1

    def test_total_rows_across_multiple_rows(self):
        rows = [
            _make_row([_make_cell("a"), _make_cell("b")], index=0),
            _make_row([_make_cell("c")], index=1),
        ]
        sheet = _make_sheet("Sheet1", rows)
        wb = _make_workbook([sheet])
        stats = workbook_stats(wb)
        assert stats["total_rows"] == 2
        assert stats["total_cells"] == 3

    def test_per_sheet_breakdown(self):
        cells = [_make_cell(1), _make_cell(None), _make_cell(3, formula="of:=1+2")]
        row = _make_row(cells)
        sheet = _make_sheet("Data", [row], index=0)
        wb = _make_workbook([sheet])
        stats = workbook_stats(wb)
        ps = stats["per_sheet"][0]
        assert ps["name"] == "Data"
        assert ps["index"] == 0
        assert ps["total_cells"] == 3
        assert ps["non_empty_cells"] == 2
        assert ps["formula_cells"] == 1


class TestWorkbookStatsMultiSheet:
    """workbook_stats on multi-sheet workbooks."""

    def test_sheet_count_correct(self):
        sheets = [
            _make_sheet("Sheet1", [], index=0),
            _make_sheet("Sheet2", [], index=1),
            _make_sheet("Sheet3", [], index=2),
        ]
        wb = _make_workbook(sheets)
        stats = workbook_stats(wb)
        assert stats["sheet_count"] == 3
        assert len(stats["per_sheet"]) == 3

    def test_totals_sum_across_sheets(self):
        row1 = _make_row([_make_cell(1), _make_cell(2)])
        row2 = _make_row([_make_cell(None), _make_cell(4)])
        sheets = [
            _make_sheet("Sheet1", [row1], index=0),
            _make_sheet("Sheet2", [row2], index=1),
        ]
        wb = _make_workbook(sheets)
        stats = workbook_stats(wb)
        assert stats["total_cells"] == 4
        assert stats["non_empty_cells"] == 3
        assert stats["total_rows"] == 2

    def test_formula_cells_across_sheets(self):
        row1 = _make_row([_make_cell(5, formula="of:=1+4")])
        row2 = _make_row([_make_cell(10, formula="of:=2*5"), _make_cell(20)])
        sheets = [
            _make_sheet("Sheet1", [row1], index=0),
            _make_sheet("Sheet2", [row2], index=1),
        ]
        wb = _make_workbook(sheets)
        stats = workbook_stats(wb)
        assert stats["formula_cells"] == 2

    def test_per_sheet_names_correct(self):
        sheets = [
            _make_sheet("Alpha", [], index=0),
            _make_sheet("Beta", [], index=1),
        ]
        wb = _make_workbook(sheets)
        stats = workbook_stats(wb)
        names = [ps["name"] for ps in stats["per_sheet"]]
        assert names == ["Alpha", "Beta"]

    def test_per_sheet_indices_correct(self):
        sheets = [
            _make_sheet("Alpha", [], index=0),
            _make_sheet("Beta", [], index=1),
        ]
        wb = _make_workbook(sheets)
        stats = workbook_stats(wb)
        indices = [ps["index"] for ps in stats["per_sheet"]]
        assert indices == [0, 1]


class TestWorkbookStatsEdgeCases:
    """Edge cases for workbook_stats."""

    def test_missing_sheets_key_returns_empty(self):
        stats = workbook_stats({})
        assert stats["sheet_count"] == 0
        assert stats["per_sheet"] == []

    def test_cell_with_none_value_not_counted_non_empty(self):
        # explicit None value should not count as non-empty
        cells = [{"value": None}]
        row = _make_row(cells)
        sheet = _make_sheet("Sheet1", [row])
        wb = _make_workbook([sheet])
        stats = workbook_stats(wb)
        assert stats["non_empty_cells"] == 0

    def test_cell_with_zero_value_counted_non_empty(self):
        # 0 is a real value, not None
        cells = [{"value": 0}]
        row = _make_row(cells)
        sheet = _make_sheet("Sheet1", [row])
        wb = _make_workbook([sheet])
        stats = workbook_stats(wb)
        assert stats["non_empty_cells"] == 1

    def test_cell_with_empty_string_counted_non_empty(self):
        # "" is not None
        cells = [{"value": ""}]
        row = _make_row(cells)
        sheet = _make_sheet("Sheet1", [row])
        wb = _make_workbook([sheet])
        stats = workbook_stats(wb)
        assert stats["non_empty_cells"] == 1
