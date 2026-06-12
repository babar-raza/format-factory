"""Tests for FODS workbook_max_column_count function (rnext41)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.neutral_model import workbook_max_column_count


def _make_workbook(sheets_data: list[list[list]]) -> dict:
    sheets = []
    for sheet_rows in sheets_data:
        rows = []
        for row_vals in sheet_rows:
            rows.append({"cells": [{"value": v} for v in row_vals]})
        sheets.append({"name": "Sheet", "rows": rows})
    return {"format": "fods", "sheets": sheets}


class TestWorkbookMaxColumnCount:
    def test_empty_workbook(self):
        wb = {"format": "fods", "sheets": []}
        assert workbook_max_column_count(wb) == 0

    def test_single_sheet_single_row(self):
        wb = _make_workbook([[[1, 2, 3]]])
        assert workbook_max_column_count(wb) == 3

    def test_multiple_rows_different_widths(self):
        wb = _make_workbook([[[1, 2], [3, 4, 5, 6]]])
        assert workbook_max_column_count(wb) == 4

    def test_multiple_sheets(self):
        wb = _make_workbook([[[1, 2]], [[1, 2, 3, 4, 5]]])
        assert workbook_max_column_count(wb) == 5

    def test_returns_int(self):
        wb = _make_workbook([[[1, 2, 3]]])
        result = workbook_max_column_count(wb)
        assert isinstance(result, int)
