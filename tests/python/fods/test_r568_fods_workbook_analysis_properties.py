"""R568: FODS workbook analysis properties — has_sheets, total_row_count, max_sheet_rows.

Tests for FodsDocument workbook analysis properties added in R568.
Spec refs: SAL-FODS-00001, SAL-FODS-00002.
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.models import FodsDocument

SAMPLES = Path("samples/by-format/fods")


def _make_doc(sheet_specs=None):
    """Build a minimal FodsDocument from a dict.

    sheet_specs: list of row counts, one per sheet. e.g. [3, 5] means 2 sheets.
    """
    if sheet_specs is None:
        sheet_specs = []
    sheets = []
    for i, row_count in enumerate(sheet_specs):
        rows = [{"cells": [{"value": f"r{r}c0", "value_type": "string", "text": f"r{r}c0"}]}
                for r in range(row_count)]
        sheets.append({"name": f"Sheet{i}", "rows": rows})
    return FodsDocument({"format_id": "fods", "sheets": sheets})


class TestHasSheets:
    def test_one_sheet_has_sheets(self):
        doc = _make_doc(sheet_specs=[2])
        assert doc.has_sheets is True

    def test_multiple_sheets_has_sheets(self):
        doc = _make_doc(sheet_specs=[1, 3])
        assert doc.has_sheets is True

    def test_empty_workbook_no_sheets(self):
        doc = _make_doc(sheet_specs=[])
        assert doc.has_sheets is False

    def test_has_sheets_type(self):
        doc = _make_doc(sheet_specs=[1])
        assert isinstance(doc.has_sheets, bool)

    def test_has_sheets_consistent_with_sheet_count(self):
        for n in range(4):
            doc = _make_doc(sheet_specs=[1] * n)
            assert doc.has_sheets == (n > 0)


class TestTotalRowCount:
    def test_empty_workbook_zero_rows(self):
        doc = _make_doc(sheet_specs=[])
        assert doc.total_row_count == 0

    def test_single_sheet_three_rows(self):
        doc = _make_doc(sheet_specs=[3])
        assert doc.total_row_count == 3

    def test_two_sheets_summed(self):
        doc = _make_doc(sheet_specs=[2, 5])
        assert doc.total_row_count == 7

    def test_zero_rows_in_sheet(self):
        doc = _make_doc(sheet_specs=[0])
        assert doc.total_row_count == 0

    def test_total_row_count_type(self):
        doc = _make_doc(sheet_specs=[2])
        assert isinstance(doc.total_row_count, int)

    def test_three_sheets_varying_rows(self):
        doc = _make_doc(sheet_specs=[1, 2, 3])
        assert doc.total_row_count == 6


class TestMaxSheetRows:
    def test_empty_workbook_returns_zero(self):
        doc = _make_doc(sheet_specs=[])
        assert doc.max_sheet_rows == 0

    def test_single_sheet_max_equals_rows(self):
        doc = _make_doc(sheet_specs=[4])
        assert doc.max_sheet_rows == 4

    def test_two_sheets_returns_max(self):
        doc = _make_doc(sheet_specs=[2, 7])
        assert doc.max_sheet_rows == 7

    def test_three_sheets_returns_max(self):
        doc = _make_doc(sheet_specs=[1, 5, 3])
        assert doc.max_sheet_rows == 5

    def test_equal_sheets_returns_value(self):
        doc = _make_doc(sheet_specs=[4, 4])
        assert doc.max_sheet_rows == 4

    def test_max_sheet_rows_type(self):
        doc = _make_doc(sheet_specs=[2])
        assert isinstance(doc.max_sheet_rows, int)

    def test_max_ge_avg(self):
        doc = _make_doc(sheet_specs=[2, 4, 3])
        avg = doc.total_row_count / doc.sheet_count
        assert doc.max_sheet_rows >= avg


class TestWorkbookAnalysisConsistency:
    def test_has_sheets_implies_not_empty(self):
        doc = _make_doc(sheet_specs=[1])
        assert doc.has_sheets
        assert not doc.is_empty

    def test_total_row_count_ge_max_when_multi_sheet(self):
        doc = _make_doc(sheet_specs=[3, 5])
        assert doc.total_row_count >= doc.max_sheet_rows

    def test_max_sheet_rows_le_total_row_count(self):
        for spec in [[], [3], [2, 4], [1, 3, 2]]:
            doc = _make_doc(sheet_specs=spec)
            assert doc.max_sheet_rows <= doc.total_row_count

    def test_from_file_multi_sheet(self):
        doc = FodsDocument.from_file(SAMPLES / "multi-sheet-basic.fods")
        assert doc.has_sheets is True
        assert isinstance(doc.total_row_count, int)
        assert isinstance(doc.max_sheet_rows, int)
        assert doc.max_sheet_rows <= doc.total_row_count
