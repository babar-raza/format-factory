"""
test_r60_fods_deepening.py — R60 Train G: FODS product deepening tests.

Tests for 2 new R60 capabilities:
1. workbook_sheet_summary(workbook) — compact per-sheet summary
2. workbook_empty_rows(workbook)    — empty-row statistics

R60 Sprint: FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from fods.neutral_model import workbook_sheet_summary, workbook_empty_rows


def _make_workbook(sheets):
    return {
        "format_id": "fods",
        "spec_version": "1.0",
        "odf_version_attr": "1.2",
        "mimetype": None,
        "sheet_count": len(sheets),
        "sheets": sheets,
        "warnings": [],
        "unsupported_features": [],
        "parse_errors": [],
    }


def _make_sheet(name, rows, idx=0):
    return {"name": name, "index": idx, "row_count": len(rows), "rows": rows}


def _make_row(cells, idx=0):
    return {"index": idx, "cells": cells}


def _make_cell(value=None, value_type=None, formula=None):
    c = {}
    if value is not None:
        c["value"] = value
    if value_type is not None:
        c["value_type"] = value_type
    if formula is not None:
        c["formula"] = formula
    return c


# ===========================================================================
# workbook_sheet_summary
# ===========================================================================

class TestWorkbookSheetSummary:
    def test_empty_workbook_returns_empty_list(self):
        wb = _make_workbook([])
        result = workbook_sheet_summary(wb)
        assert result == []

    def test_single_sheet_basic(self):
        rows = [_make_row([_make_cell("hello"), _make_cell(42)])]
        wb = _make_workbook([_make_sheet("Sheet1", rows, 0)])
        result = workbook_sheet_summary(wb)
        assert len(result) == 1
        s = result[0]
        assert s["name"] == "Sheet1"
        assert s["index"] == 0
        assert s["row_count"] == 1
        assert s["cell_count"] == 2
        assert s["non_empty_count"] == 2
        assert s["formula_count"] == 0

    def test_formula_cells_counted(self):
        rows = [_make_row([_make_cell(10, "float", "=SUM(A1:A2)"), _make_cell(None)])]
        wb = _make_workbook([_make_sheet("Sheet1", rows, 0)])
        result = workbook_sheet_summary(wb)
        assert result[0]["formula_count"] == 1
        assert result[0]["non_empty_count"] == 1

    def test_multi_sheet_summary(self):
        s1 = _make_sheet("Alpha", [_make_row([_make_cell("a"), _make_cell("b")])], 0)
        s2 = _make_sheet("Beta", [
            _make_row([_make_cell(1), _make_cell(None), _make_cell(3)]),
            _make_row([_make_cell(None)]),
        ], 1)
        wb = _make_workbook([s1, s2])
        result = workbook_sheet_summary(wb)
        assert len(result) == 2
        assert result[0]["name"] == "Alpha"
        assert result[0]["cell_count"] == 2
        assert result[0]["non_empty_count"] == 2
        assert result[1]["name"] == "Beta"
        assert result[1]["row_count"] == 2
        assert result[1]["cell_count"] == 4
        assert result[1]["non_empty_count"] == 2

    def test_empty_rows_produce_zero_counts(self):
        rows = [_make_row([]), _make_row([])]
        wb = _make_workbook([_make_sheet("Empty", rows, 0)])
        result = workbook_sheet_summary(wb)
        assert result[0]["cell_count"] == 0
        assert result[0]["non_empty_count"] == 0
        assert result[0]["formula_count"] == 0

    def test_all_empty_cells(self):
        rows = [_make_row([_make_cell(None), _make_cell(None)])]
        wb = _make_workbook([_make_sheet("Empty", rows, 0)])
        result = workbook_sheet_summary(wb)
        assert result[0]["cell_count"] == 2
        assert result[0]["non_empty_count"] == 0

    def test_index_matches_sheet_index(self):
        s1 = _make_sheet("A", [], 0)
        s2 = _make_sheet("B", [], 1)
        s3 = _make_sheet("C", [], 2)
        wb = _make_workbook([s1, s2, s3])
        result = workbook_sheet_summary(wb)
        for i, entry in enumerate(result):
            assert entry["index"] == i

    def test_returns_list_of_dicts(self):
        wb = _make_workbook([_make_sheet("X", [_make_row([_make_cell("v")])], 0)])
        result = workbook_sheet_summary(wb)
        assert isinstance(result, list)
        assert isinstance(result[0], dict)

    def test_multiple_formulas_and_non_empty(self):
        rows = [_make_row([
            _make_cell(5, "float", "=A1*2"),
            _make_cell(3, "float"),
            _make_cell(None),
            _make_cell(0, "float", "=MAX(A1:A3)"),
        ])]
        wb = _make_workbook([_make_sheet("Sheet1", rows, 0)])
        result = workbook_sheet_summary(wb)
        assert result[0]["cell_count"] == 4
        assert result[0]["non_empty_count"] == 3
        assert result[0]["formula_count"] == 2


# ===========================================================================
# workbook_empty_rows
# ===========================================================================

class TestWorkbookEmptyRows:
    def test_empty_workbook(self):
        wb = _make_workbook([])
        result = workbook_empty_rows(wb)
        assert result["total_empty_rows"] == 0
        assert result["per_sheet"] == []

    def test_no_empty_rows(self):
        rows = [_make_row([_make_cell("a")]), _make_row([_make_cell("b")])]
        wb = _make_workbook([_make_sheet("S", rows, 0)])
        result = workbook_empty_rows(wb)
        assert result["total_empty_rows"] == 0
        assert result["per_sheet"][0]["empty_row_count"] == 0

    def test_all_empty_rows(self):
        rows = [_make_row([_make_cell(None)]), _make_row([_make_cell(None), _make_cell(None)])]
        wb = _make_workbook([_make_sheet("S", rows, 0)])
        result = workbook_empty_rows(wb)
        assert result["total_empty_rows"] == 2
        assert result["per_sheet"][0]["empty_row_count"] == 2

    def test_row_with_no_cells_is_empty(self):
        rows = [_make_row([]), _make_row([_make_cell("x")])]
        wb = _make_workbook([_make_sheet("S", rows, 0)])
        result = workbook_empty_rows(wb)
        assert result["total_empty_rows"] == 1

    def test_mixed_empty_and_non_empty(self):
        rows = [
            _make_row([_make_cell("data")]),   # non-empty
            _make_row([_make_cell(None)]),      # empty
            _make_row([_make_cell(1), _make_cell(None)]),  # non-empty (has value)
            _make_row([]),                      # empty (no cells)
        ]
        wb = _make_workbook([_make_sheet("S", rows, 0)])
        result = workbook_empty_rows(wb)
        assert result["total_empty_rows"] == 2

    def test_multi_sheet_totals(self):
        s1 = _make_sheet("A", [_make_row([_make_cell(None)]), _make_row([_make_cell(1)])], 0)
        s2 = _make_sheet("B", [_make_row([]), _make_row([]), _make_row([_make_cell("x")])], 1)
        wb = _make_workbook([s1, s2])
        result = workbook_empty_rows(wb)
        assert result["total_empty_rows"] == 3  # 1 from A + 2 from B
        assert result["per_sheet"][0]["empty_row_count"] == 1
        assert result["per_sheet"][1]["empty_row_count"] == 2

    def test_per_sheet_total_row_count(self):
        rows = [_make_row([_make_cell(None)]), _make_row([_make_cell(None)]), _make_row([_make_cell(1)])]
        wb = _make_workbook([_make_sheet("S", rows, 0)])
        result = workbook_empty_rows(wb)
        assert result["per_sheet"][0]["total_row_count"] == 3
        assert result["per_sheet"][0]["empty_row_count"] == 2

    def test_per_sheet_names_and_indices(self):
        s1 = _make_sheet("Alpha", [], 0)
        s2 = _make_sheet("Beta", [_make_row([])], 1)
        wb = _make_workbook([s1, s2])
        result = workbook_empty_rows(wb)
        assert result["per_sheet"][0]["name"] == "Alpha"
        assert result["per_sheet"][0]["index"] == 0
        assert result["per_sheet"][1]["name"] == "Beta"
        assert result["per_sheet"][1]["index"] == 1

    def test_result_has_required_keys(self):
        wb = _make_workbook([_make_sheet("S", [], 0)])
        result = workbook_empty_rows(wb)
        assert "total_empty_rows" in result
        assert "per_sheet" in result
        assert "empty_row_count" in result["per_sheet"][0]
        assert "total_row_count" in result["per_sheet"][0]
