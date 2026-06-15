"""
test_rnext_fods_workbook_stats.py -- Dedicated test coverage for workbook_stats.

Gap: GAP-FODS-FOSS-WORKBOOK_STA-001 (missing_test_coverage)
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.neutral_model import workbook_stats


def _wb(sheets=None):
    return {"sheets": sheets or []}


def _sheet(name="Sheet1", rows=None):
    return {"name": name, "rows": rows or []}


def _row(cells=None):
    return {"cells": cells or []}


def _cell(value="", value_type="string"):
    return {"value": value, "value_type": value_type}


class TestWorkbookStatsBasic:
    def test_returns_dict(self):
        result = workbook_stats(_wb())
        assert isinstance(result, dict)

    def test_empty_workbook(self):
        result = workbook_stats(_wb())
        assert result["sheet_count"] == 0
        assert result["total_cells"] == 0

    def test_single_sheet_count(self):
        result = workbook_stats(_wb([_sheet()]))
        assert result["sheet_count"] == 1

    def test_multi_sheet_count(self):
        result = workbook_stats(_wb([_sheet("A"), _sheet("B"), _sheet("C")]))
        assert result["sheet_count"] == 3

    def test_cell_count(self):
        sheet = _sheet("S1", [_row([_cell("a"), _cell("b")])])
        result = workbook_stats(_wb([sheet]))
        assert result["total_cells"] >= 2

    def test_non_empty_cells(self):
        sheet = _sheet("S1", [_row([_cell("data"), _cell("")])])
        result = workbook_stats(_wb([sheet]))
        assert result["non_empty_cells"] >= 1

    def test_total_rows(self):
        sheet = _sheet("S1", [_row(), _row(), _row()])
        result = workbook_stats(_wb([sheet]))
        assert result["total_rows"] >= 3

    def test_has_per_sheet(self):
        result = workbook_stats(_wb([_sheet("A")]))
        assert "per_sheet" in result
        assert isinstance(result["per_sheet"], list)

    def test_formula_cells_zero_without_formulas(self):
        sheet = _sheet("S1", [_row([_cell("42", "float")])])
        result = workbook_stats(_wb([sheet]))
        assert result["formula_cells"] == 0
