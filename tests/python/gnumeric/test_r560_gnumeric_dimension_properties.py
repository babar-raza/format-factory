"""R560: GNUMERIC dimension properties — is_empty, is_single_sheet, is_multi_sheet.

Tests for GnumericDocument dimension properties added in R560.
Spec refs: SAL-GNUMERIC-00001.
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.models import GnumericDocument

SAMPLES = Path("samples/by-format/gnumeric")


def _make_doc(sheet_count=1, cell_count=0):
    """Build a minimal GnumericDocument from a dict."""
    sheets = [{"name": f"Sheet{i+1}", "cell_grid": {}, "row_count": 0, "col_count": 0}
              for i in range(sheet_count)]
    return GnumericDocument({
        "is_gnumeric": True,
        "sheet_count": sheet_count,
        "sheets": sheets,
        "cell_count": cell_count,
    })


class TestIsEmpty:
    def test_zero_cells_is_empty(self):
        doc = _make_doc(cell_count=0)
        assert doc.is_empty is True

    def test_one_cell_not_empty(self):
        doc = _make_doc(cell_count=1)
        assert doc.is_empty is False

    def test_many_cells_not_empty(self):
        doc = _make_doc(cell_count=100)
        assert doc.is_empty is False

    def test_is_empty_type(self):
        doc = _make_doc(cell_count=0)
        assert isinstance(doc.is_empty, bool)


class TestIsSingleSheet:
    def test_one_sheet_is_single(self):
        doc = _make_doc(sheet_count=1)
        assert doc.is_single_sheet is True

    def test_zero_sheets_not_single(self):
        doc = _make_doc(sheet_count=0)
        assert doc.is_single_sheet is False

    def test_two_sheets_not_single(self):
        doc = _make_doc(sheet_count=2)
        assert doc.is_single_sheet is False

    def test_is_single_sheet_type(self):
        doc = _make_doc(sheet_count=1)
        assert isinstance(doc.is_single_sheet, bool)


class TestIsMultiSheet:
    def test_two_sheets_is_multi(self):
        doc = _make_doc(sheet_count=2)
        assert doc.is_multi_sheet is True

    def test_three_sheets_is_multi(self):
        doc = _make_doc(sheet_count=3)
        assert doc.is_multi_sheet is True

    def test_one_sheet_not_multi(self):
        doc = _make_doc(sheet_count=1)
        assert doc.is_multi_sheet is False

    def test_is_multi_sheet_type(self):
        doc = _make_doc(sheet_count=2)
        assert isinstance(doc.is_multi_sheet, bool)


class TestDimensionConsistency:
    def test_single_sheet_mutual_exclusion(self):
        doc = _make_doc(sheet_count=1)
        assert doc.is_single_sheet
        assert not doc.is_multi_sheet

    def test_multi_sheet_mutual_exclusion(self):
        doc = _make_doc(sheet_count=3)
        assert doc.is_multi_sheet
        assert not doc.is_single_sheet

    def test_empty_consistent_with_cell_count(self):
        for n in [0, 1, 5, 100]:
            doc = _make_doc(cell_count=n)
            assert doc.is_empty == (n == 0)

    def test_from_file_minimal_spreadsheet(self):
        doc = GnumericDocument.from_file(SAMPLES / "minimal-spreadsheet.gnumeric")
        assert isinstance(doc.is_empty, bool)
        assert isinstance(doc.is_single_sheet, bool)
        assert isinstance(doc.is_multi_sheet, bool)

    def test_from_file_empty_sheet(self):
        doc = GnumericDocument.from_file(SAMPLES / "empty-sheet.gnumeric")
        assert isinstance(doc.is_empty, bool)
        assert isinstance(doc.is_single_sheet, bool)
