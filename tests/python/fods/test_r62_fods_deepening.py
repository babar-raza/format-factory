"""
test_r62_fods_deepening.py — R62 Train H: FODS neutral_model deepening tests.

Tests the two new capabilities added in R62 Train H:
  - workbook_merged_cell_summary(): merged cell detection across all sheets
  - workbook_sheet_order(): ordered list of sheet names

R62 Sprint: FORMAT-FACTORY-R62-AI-ACCELERATED-DELIVERED-SIDECAR-PYTHON-RC-PHASE13-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from fods.neutral_model import workbook_merged_cell_summary, workbook_sheet_order


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_cell(value=None, formula=None, **extra):
    c = {}
    if value is not None:
        c["value"] = value
    if formula is not None:
        c["formula"] = formula
    c.update(extra)
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


# ---------------------------------------------------------------------------
# workbook_merged_cell_summary
# ---------------------------------------------------------------------------

class TestWorkbookMergedCellSummaryEmpty:
    """workbook_merged_cell_summary on empty workbook."""

    def test_empty_workbook_returns_empty_list(self):
        wb = _make_workbook([])
        result = workbook_merged_cell_summary(wb)
        assert result == []

    def test_no_merged_cells_returns_empty_list(self):
        cells = [_make_cell("hello"), _make_cell("world")]
        sheet = _make_sheet("Sheet1", [_make_row(cells)])
        wb = _make_workbook([sheet])
        result = workbook_merged_cell_summary(wb)
        assert result == []

    def test_empty_sheet_no_rows_returns_empty(self):
        sheet = _make_sheet("Sheet1", [])
        wb = _make_workbook([sheet])
        result = workbook_merged_cell_summary(wb)
        assert result == []


class TestWorkbookMergedCellSummaryDetection:
    """workbook_merged_cell_summary detects merged cells via 'merge' key."""

    def test_single_merged_cell_detected(self):
        cell = _make_cell("merged", merge="2x1")
        row = _make_row([cell])
        sheet = _make_sheet("Sheet1", [row])
        wb = _make_workbook([sheet])
        result = workbook_merged_cell_summary(wb)
        assert len(result) == 1
        entry = result[0]
        assert entry["sheet_name"] == "Sheet1"
        assert entry["sheet_index"] == 0
        assert entry["row_index"] == 0
        assert entry["col_index"] == 0
        assert entry["merge_info"] == "2x1"

    def test_span_key_detected(self):
        cell = _make_cell("spanned", span="1x3")
        row = _make_row([cell])
        sheet = _make_sheet("MySheet", [row])
        wb = _make_workbook([sheet])
        result = workbook_merged_cell_summary(wb)
        assert len(result) == 1
        assert result[0]["merge_info"] == "1x3"

    def test_odf_attribute_key_detected(self):
        """ODF table:number-columns-spanned attribute key."""
        cell = _make_cell("odf", **{"table:number-columns-spanned": "3"})
        row = _make_row([cell])
        sheet = _make_sheet("S1", [row])
        wb = _make_workbook([sheet])
        result = workbook_merged_cell_summary(wb)
        assert len(result) == 1
        assert result[0]["merge_info"] == "3"

    def test_multiple_merged_cells_all_detected(self):
        cells = [
            _make_cell("a", merge="2x1"),
            _make_cell("b"),
            _make_cell("c", merge="1x2"),
        ]
        row = _make_row(cells)
        sheet = _make_sheet("Sheet1", [row])
        wb = _make_workbook([sheet])
        result = workbook_merged_cell_summary(wb)
        assert len(result) == 2
        assert result[0]["col_index"] == 0
        assert result[1]["col_index"] == 2

    def test_merged_cells_across_multiple_sheets(self):
        s1 = _make_sheet("Sheet1", [_make_row([_make_cell("x", merge="2x1")])], index=0)
        s2 = _make_sheet("Sheet2", [_make_row([_make_cell("y", merge="1x3")])], index=1)
        wb = _make_workbook([s1, s2])
        result = workbook_merged_cell_summary(wb)
        assert len(result) == 2
        names = [r["sheet_name"] for r in result]
        assert "Sheet1" in names
        assert "Sheet2" in names

    def test_sheet_index_preserved_in_result(self):
        s0 = _make_sheet("Alpha", [_make_row([_make_cell("m", merge="2x2")])], index=0)
        s1 = _make_sheet("Beta", [_make_row([_make_cell("n")])], index=1)
        wb = _make_workbook([s0, s1])
        result = workbook_merged_cell_summary(wb)
        assert result[0]["sheet_index"] == 0

    def test_row_index_preserved_in_result(self):
        r0 = _make_row([_make_cell("a")], index=0)
        r1 = _make_row([_make_cell("b", merge="3x1")], index=1)
        sheet = _make_sheet("Sheet1", [r0, r1])
        wb = _make_workbook([sheet])
        result = workbook_merged_cell_summary(wb)
        assert len(result) == 1
        assert result[0]["row_index"] == 1

    def test_returns_list_of_dicts(self):
        cell = _make_cell("m", merge="2x2")
        sheet = _make_sheet("S", [_make_row([cell])])
        wb = _make_workbook([sheet])
        result = workbook_merged_cell_summary(wb)
        assert isinstance(result, list)
        assert all(isinstance(e, dict) for e in result)

    def test_result_dict_has_required_keys(self):
        cell = _make_cell("m", merge="2x1")
        sheet = _make_sheet("S", [_make_row([cell])])
        wb = _make_workbook([sheet])
        result = workbook_merged_cell_summary(wb)
        entry = result[0]
        for key in ("sheet_name", "sheet_index", "row_index", "col_index", "merge_info"):
            assert key in entry, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# workbook_sheet_order
# ---------------------------------------------------------------------------

class TestWorkbookSheetOrderEmpty:
    """workbook_sheet_order on empty workbook."""

    def test_empty_workbook_returns_empty_list(self):
        wb = _make_workbook([])
        result = workbook_sheet_order(wb)
        assert result == []

    def test_returns_list(self):
        wb = _make_workbook([])
        assert isinstance(workbook_sheet_order(wb), list)


class TestWorkbookSheetOrderSingle:
    """workbook_sheet_order with a single sheet."""

    def test_single_sheet_returns_one_name(self):
        wb = _make_workbook([_make_sheet("MySheet", [])])
        result = workbook_sheet_order(wb)
        assert result == ["MySheet"]

    def test_single_sheet_name_matches(self):
        wb = _make_workbook([_make_sheet("Alpha", [])])
        assert workbook_sheet_order(wb) == ["Alpha"]


class TestWorkbookSheetOrderMultiple:
    """workbook_sheet_order preserves insertion order."""

    def test_multi_sheet_order_preserved(self):
        s1 = _make_sheet("First", [])
        s2 = _make_sheet("Second", [])
        s3 = _make_sheet("Third", [])
        wb = _make_workbook([s1, s2, s3])
        result = workbook_sheet_order(wb)
        assert result == ["First", "Second", "Third"]

    def test_order_not_alphabetically_sorted(self):
        """Sheet order must reflect workbook order, not alphabetical."""
        s1 = _make_sheet("Zebra", [])
        s2 = _make_sheet("Alpha", [])
        s3 = _make_sheet("Mango", [])
        wb = _make_workbook([s1, s2, s3])
        result = workbook_sheet_order(wb)
        assert result == ["Zebra", "Alpha", "Mango"]

    def test_five_sheets_order(self):
        sheets = [_make_sheet(f"Sheet{i}", [], index=i) for i in range(1, 6)]
        wb = _make_workbook(sheets)
        result = workbook_sheet_order(wb)
        assert result == [f"Sheet{i}" for i in range(1, 6)]

    def test_sheet_count_matches_len_of_result(self):
        sheets = [_make_sheet(f"S{i}", []) for i in range(4)]
        wb = _make_workbook(sheets)
        result = workbook_sheet_order(wb)
        assert len(result) == 4

    def test_returns_strings(self):
        sheets = [_make_sheet("A", []), _make_sheet("B", [])]
        wb = _make_workbook(sheets)
        result = workbook_sheet_order(wb)
        assert all(isinstance(n, str) for n in result)


class TestWorkbookSheetOrderDefaultNames:
    """workbook_sheet_order generates default names for unnamed sheets."""

    def test_unnamed_sheet_gets_default_name(self):
        sheet_no_name = {"rows": [], "row_count": 0, "index": 0}
        wb = _make_workbook([sheet_no_name])
        result = workbook_sheet_order(wb)
        assert len(result) == 1
        assert "Sheet1" in result[0] or result[0] != ""
