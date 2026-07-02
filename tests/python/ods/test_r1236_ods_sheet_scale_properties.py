"""Tests for R1236: OdsModelDocument sheet scale classification properties.

Properties under test:
    is_large_workbook — total_row_count > 10000
    has_many_sheets   — sheet_count > 5
    avg_rows_per_sheet — total_row_count / sheet_count (0.0 if no sheets)

spec_fact_ref: FACT-ODS-001
"""

import types
import pytest
from ods.models import OdsModelDocument


def _make_sheet(name: str, row_count: int):
    """Build a stub sheet with the given row count."""
    rows = [types.SimpleNamespace(cells=[]) for _ in range(row_count)]
    return types.SimpleNamespace(name=name, rows=rows)


def _make_doc(sheet_row_counts: list[int]) -> OdsModelDocument:
    """Build an OdsModelDocument stub with sheets of given row counts."""
    sheets = [_make_sheet(f"Sheet{i+1}", rc) for i, rc in enumerate(sheet_row_counts)]
    parsed = types.SimpleNamespace(sheets=sheets, path="test.ods")
    return OdsModelDocument(parsed)


# ── is_large_workbook ─────────────────────────────────────────────────────────

class TestIsLargeWorkbook:
    def test_over_10000_total_rows_is_large(self):
        doc = _make_doc([5001, 5000])  # total = 10001
        assert doc.is_large_workbook is True

    def test_exactly_10000_not_large(self):
        doc = _make_doc([5000, 5000])  # total = 10000, not > 10000
        assert doc.is_large_workbook is False

    def test_below_10000_not_large(self):
        doc = _make_doc([100, 200, 300])  # total = 600
        assert doc.is_large_workbook is False

    def test_empty_workbook_not_large(self):
        doc = _make_doc([])
        assert doc.is_large_workbook is False

    def test_single_sheet_large(self):
        doc = _make_doc([10001])
        assert doc.is_large_workbook is True

    def test_many_sheets_total_large(self):
        doc = _make_doc([2000] * 6)  # total = 12000
        assert doc.is_large_workbook is True

    def test_many_sheets_total_not_large(self):
        doc = _make_doc([100] * 10)  # total = 1000
        assert doc.is_large_workbook is False


# ── has_many_sheets ───────────────────────────────────────────────────────────

class TestHasManySheets:
    def test_six_sheets_is_many(self):
        doc = _make_doc([0] * 6)
        assert doc.has_many_sheets is True

    def test_five_sheets_not_many(self):
        doc = _make_doc([0] * 5)  # exactly 5, not > 5
        assert doc.has_many_sheets is False

    def test_four_sheets_not_many(self):
        doc = _make_doc([0] * 4)
        assert doc.has_many_sheets is False

    def test_single_sheet_not_many(self):
        doc = _make_doc([100])
        assert doc.has_many_sheets is False

    def test_empty_not_many(self):
        doc = _make_doc([])
        assert doc.has_many_sheets is False

    def test_ten_sheets_is_many(self):
        doc = _make_doc([10] * 10)
        assert doc.has_many_sheets is True


# ── avg_rows_per_sheet ────────────────────────────────────────────────────────

class TestAvgRowsPerSheet:
    def test_no_sheets_returns_zero(self):
        doc = _make_doc([])
        assert doc.avg_rows_per_sheet == 0.0

    def test_single_sheet_avg(self):
        doc = _make_doc([100])
        assert doc.avg_rows_per_sheet == pytest.approx(100.0)

    def test_equal_sheets_avg(self):
        doc = _make_doc([200, 200, 200])
        assert doc.avg_rows_per_sheet == pytest.approx(200.0)

    def test_mixed_sheets_avg(self):
        doc = _make_doc([100, 200, 300])  # total=600, count=3
        assert doc.avg_rows_per_sheet == pytest.approx(200.0)

    def test_zero_row_sheets_avg(self):
        doc = _make_doc([0, 0, 0])
        assert doc.avg_rows_per_sheet == pytest.approx(0.0)

    def test_fractional_avg(self):
        doc = _make_doc([100, 101])  # total=201, count=2 → 100.5
        assert doc.avg_rows_per_sheet == pytest.approx(100.5)


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_large_workbook_with_many_sheets(self):
        doc = _make_doc([2000] * 6)  # 12000 total, 6 sheets
        assert doc.is_large_workbook is True
        assert doc.has_many_sheets is True

    def test_many_sheets_not_large_workbook(self):
        doc = _make_doc([10] * 6)  # 60 total, 6 sheets
        assert doc.has_many_sheets is True
        assert doc.is_large_workbook is False

    def test_large_workbook_few_sheets(self):
        doc = _make_doc([10001])
        assert doc.is_large_workbook is True
        assert doc.has_many_sheets is False

    def test_avg_consistent_with_total_and_count(self):
        doc = _make_doc([300, 500, 700])
        assert doc.avg_rows_per_sheet == pytest.approx(doc.total_row_count / doc.sheet_count)
