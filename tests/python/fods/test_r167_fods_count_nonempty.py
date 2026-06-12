"""Tests for FODS workbook_count_nonempty_cells function (rnext33)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.neutral_model import workbook_count_nonempty_cells


def _make_workbook(rows_per_sheet):
    """Build a minimal workbook dict."""
    sheets = []
    for sheet_rows in rows_per_sheet:
        rows = []
        for row_vals in sheet_rows:
            cells = [{"value": v} for v in row_vals]
            rows.append({"cells": cells})
        sheets.append({"rows": rows})
    return {"sheets": sheets}


class TestWorkbookCountNonemptyCells:
    def test_basic_count(self):
        wb = _make_workbook([[["A", "B"], ["C", None]]])
        assert workbook_count_nonempty_cells(wb) == 3

    def test_all_empty(self):
        wb = _make_workbook([[[None, None], [None, ""]]])
        assert workbook_count_nonempty_cells(wb) == 0

    def test_all_filled(self):
        wb = _make_workbook([[[1, 2], [3, 4]]])
        assert workbook_count_nonempty_cells(wb) == 4

    def test_empty_sheet(self):
        wb = _make_workbook([[]])
        assert workbook_count_nonempty_cells(wb) == 0

    def test_no_sheets(self):
        wb = {"sheets": []}
        assert workbook_count_nonempty_cells(wb) == 0

    def test_second_sheet(self):
        wb = _make_workbook([[["X"]], [["A", "B", "C"]]])
        assert workbook_count_nonempty_cells(wb, sheet_index=1) == 3

    def test_bad_sheet_index(self):
        wb = _make_workbook([[["X"]]])
        assert workbook_count_nonempty_cells(wb, sheet_index=5) == 0

    def test_numeric_values(self):
        wb = _make_workbook([[[0, 1.5, -3]]])
        # 0 is not None and not "" — counts as non-empty
        assert workbook_count_nonempty_cells(wb) == 3
