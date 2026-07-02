"""Tests for R1276: OdsModelDocument workbook structure analysis properties.

Properties under test:
    has_data_sheets         — at least one sheet has rows
    largest_sheet_fraction  — max_sheet_rows / total_row_count (0.0 if no rows)
    is_single_sheet_dominant — largest_sheet_fraction > 0.8

spec_fact_ref: FACT-ODS-001
"""

import types
import pytest
from ods.models import OdsModelDocument


def _make_sheet(name: str, row_count: int) -> types.SimpleNamespace:
    """Build a stub ODS sheet with given row count."""
    return types.SimpleNamespace(
        name=name,
        rows=[types.SimpleNamespace(cells=[]) for _ in range(row_count)],
    )


def _make_doc(row_counts: list[int]) -> OdsModelDocument:
    """Build an OdsModelDocument stub with given per-sheet row counts."""
    parsed = types.SimpleNamespace(
        sheets=[_make_sheet(f"Sheet{i+1}", rc) for i, rc in enumerate(row_counts)],
        path="test.ods",
    )
    return OdsModelDocument(parsed)


# ── has_data_sheets ───────────────────────────────────────────────────────────

class TestHasDataSheets:
    def test_no_sheets_false(self):
        doc = _make_doc([])
        assert doc.has_data_sheets is False

    def test_all_empty_sheets_false(self):
        doc = _make_doc([0, 0, 0])
        assert doc.has_data_sheets is False

    def test_one_nonempty_sheet_true(self):
        doc = _make_doc([5, 0, 0])
        assert doc.has_data_sheets is True

    def test_all_nonempty_sheets_true(self):
        doc = _make_doc([10, 20, 30])
        assert doc.has_data_sheets is True

    def test_single_nonempty_sheet(self):
        doc = _make_doc([100])
        assert doc.has_data_sheets is True


# ── largest_sheet_fraction ────────────────────────────────────────────────────

class TestLargestSheetFraction:
    def test_no_sheets_returns_zero(self):
        doc = _make_doc([])
        assert doc.largest_sheet_fraction == pytest.approx(0.0)

    def test_all_empty_sheets_returns_zero(self):
        doc = _make_doc([0, 0])
        assert doc.largest_sheet_fraction == pytest.approx(0.0)

    def test_single_sheet_fraction_one(self):
        doc = _make_doc([100])
        assert doc.largest_sheet_fraction == pytest.approx(1.0)

    def test_equal_sheets_fraction_half(self):
        doc = _make_doc([50, 50])
        assert doc.largest_sheet_fraction == pytest.approx(0.5)

    def test_dominant_sheet_high_fraction(self):
        # 90 out of 100 total → 0.9
        doc = _make_doc([90, 10])
        assert doc.largest_sheet_fraction == pytest.approx(0.9)

    def test_three_sheets_proportional(self):
        doc = _make_doc([60, 30, 10])
        assert doc.largest_sheet_fraction == pytest.approx(60 / 100)


# ── is_single_sheet_dominant ──────────────────────────────────────────────────

class TestIsSingleSheetDominant:
    def test_no_sheets_false(self):
        doc = _make_doc([])
        assert doc.is_single_sheet_dominant is False

    def test_one_sheet_dominant(self):
        doc = _make_doc([100])
        assert doc.is_single_sheet_dominant is True

    def test_90_pct_dominant(self):
        doc = _make_doc([90, 10])
        assert doc.is_single_sheet_dominant is True

    def test_80_pct_not_dominant(self):
        # exactly 80% → not > 0.8
        doc = _make_doc([80, 20])
        assert doc.is_single_sheet_dominant is False

    def test_equal_sheets_not_dominant(self):
        doc = _make_doc([50, 50])
        assert doc.is_single_sheet_dominant is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_dominant_implies_has_data(self):
        doc = _make_doc([90, 5])
        assert doc.is_single_sheet_dominant is True
        assert doc.has_data_sheets is True

    def test_fraction_consistent_with_max_total(self):
        doc = _make_doc([70, 20, 10])
        assert doc.largest_sheet_fraction == pytest.approx(
            doc.max_sheet_rows / doc.total_row_count
        )

    def test_all_empty_no_data_no_fraction(self):
        doc = _make_doc([0, 0])
        assert doc.has_data_sheets is False
        assert doc.largest_sheet_fraction == pytest.approx(0.0)
