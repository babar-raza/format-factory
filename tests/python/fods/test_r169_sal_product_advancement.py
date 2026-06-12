"""
Lane 8: FODS product advancement under SAL gates.

Sprint: FORMAT-FACTORY-SAL-PHASE2-CLOSEOUT-AND-PRODUCT-GATED-ADVANCEMENT-001

New functions (spec-fact-backed):
  workbook_row_count(wb, sheet_index=0)  -- FACT-FODS-005
  workbook_cell_text_at(wb, s, r, c)     -- FACT-FODS-006, FACT-FODS-007
"""
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO / "src" / "python"))

from fods.neutral_model import workbook_row_count, workbook_cell_text_at


def _make_workbook(sheets=None):
    return {"sheets": sheets or []}


def _make_sheet(name="Sheet1", rows=None):
    return {"name": name, "rows": rows or []}


def _make_row(cells=None):
    return {"cells": cells or []}


def _make_cell(value=None, text=None, value_type="string"):
    cell = {}
    if value is not None:
        cell["value"] = value
    if text is not None:
        cell["text"] = text
    if value_type:
        cell["value_type"] = value_type
    return cell


class TestWorkbookRowCount:
    """workbook_row_count: FACT-FODS-005 (rows are table:table-row children)."""

    def test_empty_workbook_returns_zero(self):
        wb = _make_workbook()
        assert workbook_row_count(wb) == 0

    def test_single_row(self):
        wb = _make_workbook(sheets=[_make_sheet(rows=[_make_row()])])
        assert workbook_row_count(wb) == 1

    def test_three_rows(self):
        wb = _make_workbook(sheets=[_make_sheet(rows=[_make_row(), _make_row(), _make_row()])])
        assert workbook_row_count(wb) == 3

    def test_second_sheet_index(self):
        s1 = _make_sheet("S1", rows=[_make_row()])
        s2 = _make_sheet("S2", rows=[_make_row(), _make_row()])
        wb = _make_workbook(sheets=[s1, s2])
        assert workbook_row_count(wb, 0) == 1
        assert workbook_row_count(wb, 1) == 2

    def test_negative_sheet_index_returns_zero(self):
        wb = _make_workbook(sheets=[_make_sheet(rows=[_make_row()])])
        assert workbook_row_count(wb, -1) == 0

    def test_out_of_range_sheet_returns_zero(self):
        wb = _make_workbook(sheets=[_make_sheet(rows=[_make_row()])])
        assert workbook_row_count(wb, 99) == 0

    def test_no_rows_key_returns_zero(self):
        wb = {"sheets": [{"name": "S1"}]}
        assert workbook_row_count(wb) == 0


class TestWorkbookCellTextAt:
    """workbook_cell_text_at: FACT-FODS-006/007 (cells and text:p children)."""

    def _wb_with_cell(self, value=None, text=None):
        cell = _make_cell(value=value, text=text)
        wb = _make_workbook(sheets=[_make_sheet(rows=[_make_row(cells=[cell])])])
        return wb

    def test_string_value_returned(self):
        wb = self._wb_with_cell(value="Hello")
        assert workbook_cell_text_at(wb, 0, 0, 0) == "Hello"

    def test_text_key_takes_precedence_over_value(self):
        wb = self._wb_with_cell(value="val", text="text_content")
        assert workbook_cell_text_at(wb, 0, 0, 0) == "text_content"

    def test_empty_cell_returns_empty_string(self):
        wb = _make_workbook(sheets=[_make_sheet(rows=[_make_row(cells=[{}])])])
        assert workbook_cell_text_at(wb, 0, 0, 0) == ""

    def test_out_of_bounds_row_returns_empty(self):
        wb = self._wb_with_cell(value="x")
        assert workbook_cell_text_at(wb, 0, 99, 0) == ""

    def test_out_of_bounds_col_returns_empty(self):
        wb = self._wb_with_cell(value="x")
        assert workbook_cell_text_at(wb, 0, 0, 99) == ""

    def test_out_of_bounds_sheet_returns_empty(self):
        wb = self._wb_with_cell(value="x")
        assert workbook_cell_text_at(wb, 99, 0, 0) == ""

    def test_numeric_value_converted_to_string(self):
        cell = _make_cell(value=42, value_type="float")
        wb = _make_workbook(sheets=[_make_sheet(rows=[_make_row(cells=[cell])])])
        assert workbook_cell_text_at(wb, 0, 0, 0) == "42"

    def test_none_cell_returns_empty(self):
        wb = _make_workbook(sheets=[_make_sheet(rows=[_make_row(cells=[None])])])
        assert workbook_cell_text_at(wb, 0, 0, 0) == ""

    def test_multi_row_col_grid(self):
        r0 = _make_row(cells=[_make_cell(value="A"), _make_cell(value="B")])
        r1 = _make_row(cells=[_make_cell(value="C"), _make_cell(value="D")])
        wb = _make_workbook(sheets=[_make_sheet(rows=[r0, r1])])
        assert workbook_cell_text_at(wb, 0, 0, 0) == "A"
        assert workbook_cell_text_at(wb, 0, 0, 1) == "B"
        assert workbook_cell_text_at(wb, 0, 1, 0) == "C"
        assert workbook_cell_text_at(wb, 0, 1, 1) == "D"
