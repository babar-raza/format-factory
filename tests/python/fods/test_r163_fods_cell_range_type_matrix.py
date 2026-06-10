"""
test_r163_fods_cell_range_type_matrix.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT26-001
Added: 2026-06-10

Tests for FODS APIs:
- workbook_cell_range(workbook, sheet_index, row_start, row_end, col_start, col_end)
- workbook_cell_type_matrix(workbook) -> list[dict]
- workbook_merged_cell_summary(workbook) -> list[dict]

Authority: P6 (FACT-FODS-001: ODF 1.3 spreadsheet MIME type)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.neutral_model import (
    workbook_cell_range,
    workbook_cell_type_matrix,
    workbook_merged_cell_summary,
)


def _cell(value=None, value_type="string", formula=None, merge=None):
    c = {"value": value, "value_type": value_type}
    if formula is not None:
        c["formula"] = formula
    if merge is not None:
        c["merge"] = merge
    return c


def _row(cells):
    return {"cells": cells}


def _sheet(name, rows, index=0):
    return {"name": name, "rows": rows, "index": index}


def _workbook(sheets):
    return {"sheets": sheets}


# ── workbook_cell_range ─────────────────────────────────────────────────

class TestWorkbookCellRange:

    def test_empty_workbook(self):
        assert workbook_cell_range(_workbook([]), sheet_index=0) == []

    def test_invalid_sheet_index(self):
        wb = _workbook([_sheet("S1", [_row([_cell("a")])])])
        assert workbook_cell_range(wb, sheet_index=5) == []

    def test_full_range(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("a"), _cell("b")]),
            _row([_cell("c"), _cell("d")]),
        ])])
        result = workbook_cell_range(wb)
        assert result == [["a", "b"], ["c", "d"]]

    def test_row_subset(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("r0")]),
            _row([_cell("r1")]),
            _row([_cell("r2")]),
        ])])
        result = workbook_cell_range(wb, row_start=1, row_end=1)
        assert result == [["r1"]]

    def test_col_subset(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("a"), _cell("b"), _cell("c")]),
        ])])
        result = workbook_cell_range(wb, col_start=1, col_end=1)
        assert result == [["b"]]

    def test_rectangular_range(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("00"), _cell("01"), _cell("02")]),
            _row([_cell("10"), _cell("11"), _cell("12")]),
            _row([_cell("20"), _cell("21"), _cell("22")]),
        ])])
        result = workbook_cell_range(wb, row_start=0, row_end=1, col_start=1, col_end=2)
        assert result == [["01", "02"], ["11", "12"]]

    def test_none_values(self):
        wb = _workbook([_sheet("S1", [_row([_cell(None)])])])
        result = workbook_cell_range(wb)
        assert result == [[None]]

    def test_second_sheet(self):
        wb = _workbook([
            _sheet("A", [_row([_cell("a1")])]),
            _sheet("B", [_row([_cell("b1")])]),
        ])
        result = workbook_cell_range(wb, sheet_index=1)
        assert result == [["b1"]]


# ── workbook_cell_type_matrix ───────────────────────────────────────────

class TestWorkbookCellTypeMatrix:

    def test_empty_workbook(self):
        assert workbook_cell_type_matrix(_workbook([])) == []

    def test_text_cells(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("hello", "string"), _cell("world", "string")]),
        ])])
        result = workbook_cell_type_matrix(wb)
        assert len(result) == 1
        assert result[0]["by_type"]["text"] == 2
        assert result[0]["total_cells"] == 2

    def test_numeric_cells(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("42", "float"), _cell("90%", "percentage")]),
        ])])
        result = workbook_cell_type_matrix(wb)
        assert result[0]["by_type"]["numeric"] == 2

    def test_formula_cells(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("10", "float", formula="=SUM(A1)")]),
        ])])
        result = workbook_cell_type_matrix(wb)
        assert result[0]["by_type"]["formula"] == 1

    def test_mixed_types(self):
        wb = _workbook([_sheet("S1", [
            _row([
                _cell("hi", "string"),
                _cell("42", "float"),
                _cell("true", "boolean"),
            ]),
        ])])
        result = workbook_cell_type_matrix(wb)
        assert result[0]["by_type"]["text"] == 1
        assert result[0]["by_type"]["numeric"] == 1
        assert result[0]["by_type"]["boolean"] == 1
        assert result[0]["total_cells"] == 3

    def test_empty_cells_not_counted_in_total(self):
        wb = _workbook([_sheet("S1", [_row([{"value": None}])])])
        result = workbook_cell_type_matrix(wb)
        assert result[0]["total_cells"] == 0
        assert result[0]["by_type"]["empty"] == 1

    def test_multi_sheet(self):
        wb = _workbook([
            _sheet("A", [_row([_cell("x", "string")])]),
            _sheet("B", [_row([_cell("1", "float")])]),
        ])
        result = workbook_cell_type_matrix(wb)
        assert len(result) == 2
        assert result[0]["sheet_name"] == "A"
        assert result[1]["sheet_name"] == "B"


# ── workbook_merged_cell_summary ────────────────────────────────────────

class TestWorkbookMergedCellSummary:

    def test_empty_workbook(self):
        assert workbook_merged_cell_summary(_workbook([])) == []

    def test_no_merges(self):
        wb = _workbook([_sheet("S1", [_row([_cell("a")])])])
        assert workbook_merged_cell_summary(wb) == []

    def test_single_merge(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("merged", merge={"cols": 2, "rows": 1})]),
        ])])
        result = workbook_merged_cell_summary(wb)
        assert len(result) == 1
        assert result[0]["sheet_name"] == "S1"
        assert result[0]["row_index"] == 0
        assert result[0]["col_index"] == 0
        assert result[0]["merge_info"] == {"cols": 2, "rows": 1}

    def test_multiple_merges(self):
        wb = _workbook([_sheet("S1", [
            _row([_cell("a", merge="2:1"), _cell("b")]),
            _row([_cell("c"), _cell("d", merge="1:2")]),
        ])])
        result = workbook_merged_cell_summary(wb)
        assert len(result) == 2
