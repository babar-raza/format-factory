"""Tests for R1231: GnumericDocument workbook scale and content classification properties.

Properties under test:
    is_large_workbook — cell_count > 10000
    has_many_sheets   — sheet_count > 5
    is_cell_dense     — avg_cells_per_sheet > 1000

spec_fact_ref: SAL-GNUMERIC-00001
"""

import pytest
from gnumeric.models import GnumericDocument


def _make_doc(sheet_count: int, cell_count: int) -> GnumericDocument:
    """Build a GnumericDocument stub with the given sheet and cell counts."""
    sheets = [{"name": f"Sheet{i+1}", "cell_grid": {}} for i in range(sheet_count)]
    data = {
        "is_gnumeric": True,
        "sheet_count": sheet_count,
        "sheets": sheets,
        "cell_count": cell_count,
    }
    return GnumericDocument(data)


# ── is_large_workbook ─────────────────────────────────────────────────────────

class TestIsLargeWorkbook:
    def test_over_10000_cells_is_large(self):
        doc = _make_doc(1, 10001)
        assert doc.is_large_workbook is True

    def test_exactly_10000_not_large(self):
        doc = _make_doc(1, 10000)  # not > 10000
        assert doc.is_large_workbook is False

    def test_below_10000_not_large(self):
        doc = _make_doc(1, 5000)
        assert doc.is_large_workbook is False

    def test_zero_cells_not_large(self):
        doc = _make_doc(0, 0)
        assert doc.is_large_workbook is False

    def test_very_large_workbook(self):
        doc = _make_doc(10, 100000)
        assert doc.is_large_workbook is True

    def test_boundary_10001_is_large(self):
        doc = _make_doc(2, 10001)
        assert doc.is_large_workbook is True


# ── has_many_sheets ───────────────────────────────────────────────────────────

class TestHasManySheets:
    def test_over_5_sheets_has_many(self):
        doc = _make_doc(6, 0)
        assert doc.has_many_sheets is True

    def test_exactly_5_not_many(self):
        doc = _make_doc(5, 0)  # not > 5
        assert doc.has_many_sheets is False

    def test_below_5_not_many(self):
        doc = _make_doc(3, 0)
        assert doc.has_many_sheets is False

    def test_zero_sheets_not_many(self):
        doc = _make_doc(0, 0)
        assert doc.has_many_sheets is False

    def test_single_sheet_not_many(self):
        doc = _make_doc(1, 100)
        assert doc.has_many_sheets is False

    def test_ten_sheets_is_many(self):
        doc = _make_doc(10, 0)
        assert doc.has_many_sheets is True


# ── is_cell_dense ─────────────────────────────────────────────────────────────

class TestIsCellDense:
    def test_avg_over_1000_is_dense(self):
        doc = _make_doc(2, 2002)  # avg = 1001
        assert doc.is_cell_dense is True

    def test_avg_exactly_1000_not_dense(self):
        doc = _make_doc(2, 2000)  # avg = 1000, not > 1000
        assert doc.is_cell_dense is False

    def test_avg_below_1000_not_dense(self):
        doc = _make_doc(1, 500)
        assert doc.is_cell_dense is False

    def test_no_sheets_not_dense(self):
        doc = _make_doc(0, 0)
        assert doc.is_cell_dense is False

    def test_single_sheet_dense(self):
        doc = _make_doc(1, 5000)
        assert doc.is_cell_dense is True

    def test_many_sheets_sparse_not_dense(self):
        doc = _make_doc(10, 100)  # avg = 10
        assert doc.is_cell_dense is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_large_dense_workbook(self):
        doc = _make_doc(5, 50000)
        assert doc.is_large_workbook is True
        assert doc.is_cell_dense is True

    def test_many_sheets_sparse_not_large(self):
        doc = _make_doc(10, 100)
        assert doc.has_many_sheets is True
        assert doc.is_large_workbook is False
        assert doc.is_cell_dense is False

    def test_empty_workbook_all_false(self):
        doc = _make_doc(0, 0)
        assert doc.is_large_workbook is False
        assert doc.has_many_sheets is False
        assert doc.is_cell_dense is False

    def test_single_sheet_large_and_dense(self):
        doc = _make_doc(1, 20000)
        assert doc.is_large_workbook is True
        assert doc.is_cell_dense is True
        assert doc.has_many_sheets is False
