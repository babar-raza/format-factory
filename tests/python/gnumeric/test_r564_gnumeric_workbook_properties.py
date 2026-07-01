"""R564: Gnumeric workbook analysis properties — has_cells, avg_cells_per_sheet, is_sparse.

Tests for GnumericDocument workbook properties added in R564.
Spec refs: FACT-GNUMERIC-001 (gnumeric:workbook), FACT-GNUMERIC-002 (gnumeric:sheet),
           FACT-GNUMERIC-003 (gnumeric:cell).
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.models import GnumericDocument

SAMPLES = Path("samples/by-format/gnumeric")


def _make_doc(sheet_count=0, cell_count=0):
    """Build a minimal GnumericDocument from counts."""
    sheets = [{"name": f"Sheet{i}", "rows": []} for i in range(sheet_count)]
    data = {
        "is_gnumeric": True,
        "sheet_count": sheet_count,
        "sheets": sheets,
        "cell_count": cell_count,
    }
    return GnumericDocument(data)


class TestHasCells:
    def test_no_cells(self):
        doc = _make_doc(sheet_count=1, cell_count=0)
        assert doc.has_cells is False

    def test_one_cell(self):
        doc = _make_doc(sheet_count=1, cell_count=1)
        assert doc.has_cells is True

    def test_many_cells(self):
        doc = _make_doc(sheet_count=2, cell_count=100)
        assert doc.has_cells is True

    def test_empty_workbook_no_cells(self):
        doc = _make_doc(sheet_count=0, cell_count=0)
        assert doc.has_cells is False

    def test_has_cells_type(self):
        doc = _make_doc(sheet_count=1, cell_count=5)
        assert isinstance(doc.has_cells, bool)

    def test_has_cells_inverse_of_is_empty(self):
        doc = _make_doc(sheet_count=0, cell_count=0)
        assert doc.is_empty is True
        assert doc.has_cells is False


class TestAvgCellsPerSheet:
    def test_no_sheets_returns_zero(self):
        doc = _make_doc(sheet_count=0, cell_count=0)
        assert doc.avg_cells_per_sheet == 0.0

    def test_one_sheet_10_cells(self):
        doc = _make_doc(sheet_count=1, cell_count=10)
        assert doc.avg_cells_per_sheet == pytest.approx(10.0)

    def test_two_sheets_20_cells(self):
        doc = _make_doc(sheet_count=2, cell_count=20)
        assert doc.avg_cells_per_sheet == pytest.approx(10.0)

    def test_three_sheets_9_cells(self):
        doc = _make_doc(sheet_count=3, cell_count=9)
        assert doc.avg_cells_per_sheet == pytest.approx(3.0)

    def test_avg_cells_per_sheet_type(self):
        doc = _make_doc(sheet_count=1, cell_count=5)
        assert isinstance(doc.avg_cells_per_sheet, float)

    def test_avg_consistent_with_counts(self):
        doc = _make_doc(sheet_count=4, cell_count=12)
        assert doc.avg_cells_per_sheet == doc.cell_count / doc.sheet_count


class TestIsSparse:
    def test_no_sheets_not_sparse(self):
        doc = _make_doc(sheet_count=0, cell_count=0)
        assert doc.is_sparse is False

    def test_sheet_with_cells_not_sparse(self):
        doc = _make_doc(sheet_count=1, cell_count=5)
        assert doc.is_sparse is False

    def test_sheet_with_no_cells_is_sparse(self):
        doc = _make_doc(sheet_count=1, cell_count=0)
        assert doc.is_sparse is True

    def test_multiple_sheets_no_cells_is_sparse(self):
        doc = _make_doc(sheet_count=3, cell_count=0)
        assert doc.is_sparse is True

    def test_is_sparse_type(self):
        doc = _make_doc(sheet_count=1, cell_count=0)
        assert isinstance(doc.is_sparse, bool)


class TestWorkbookPropertyConsistency:
    def test_has_cells_implies_not_sparse(self):
        doc = _make_doc(sheet_count=2, cell_count=5)
        assert doc.has_cells is True
        assert doc.is_sparse is False

    def test_is_sparse_implies_no_cells(self):
        doc = _make_doc(sheet_count=1, cell_count=0)
        assert doc.is_sparse is True
        assert doc.has_cells is False

    def test_empty_workbook_no_cells_not_sparse(self):
        doc = _make_doc(sheet_count=0, cell_count=0)
        assert doc.is_empty is True
        assert doc.has_cells is False
        assert doc.is_sparse is False

    def test_from_file(self):
        doc = GnumericDocument.from_file(SAMPLES / "minimal-spreadsheet.gnumeric")
        assert isinstance(doc.has_cells, bool)
        assert isinstance(doc.avg_cells_per_sheet, float)
        assert isinstance(doc.is_sparse, bool)
        if doc.sheet_count > 0:
            assert doc.avg_cells_per_sheet == doc.cell_count / doc.sheet_count
