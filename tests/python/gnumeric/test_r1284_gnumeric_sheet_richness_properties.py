"""Tests for R1284: GnumericDocument sheet cell richness and variance properties.

Properties under test:
    is_data_rich         — avg_cells_per_sheet > 500
    sheet_cell_variance  — cell_count_range / max_cells_per_sheet (0.0 if max=0)
    has_large_sheets     — max_cells_per_sheet > 1000

spec_fact_ref: SAL-GNUMERIC-00001
"""

import pytest
from gnumeric.models import GnumericDocument


def _make_sheet(name: str, cell_count: int) -> dict:
    return {
        "name": name,
        "cell_grid": {f"cell_{i}": i for i in range(cell_count)},
    }


def _make_doc(cell_counts: list[int]) -> GnumericDocument:
    sheets = [_make_sheet(f"Sheet{i+1}", c) for i, c in enumerate(cell_counts)]
    data = {
        "sheets": sheets,
        "cell_count": sum(cell_counts),  # required for avg_cells_per_sheet
        "metadata": {"application": "gnumeric"},
    }
    return GnumericDocument(data)


# ── is_data_rich ──────────────────────────────────────────────────────────────

class TestIsDataRich:
    def test_no_sheets_not_data_rich(self):
        doc = _make_doc([])
        assert doc.is_data_rich is False

    def test_small_cells_not_data_rich(self):
        doc = _make_doc([100, 200])
        assert doc.is_data_rich is False

    def test_exactly_500_not_data_rich(self):
        # avg = 500, NOT > 500
        doc = _make_doc([500])
        assert doc.is_data_rich is False

    def test_501_cells_is_data_rich(self):
        doc = _make_doc([501])
        assert doc.is_data_rich is True

    def test_avg_over_500_is_data_rich(self):
        # avg = (400 + 700) / 2 = 550 > 500
        doc = _make_doc([400, 700])
        assert doc.is_data_rich is True

    def test_high_cell_count_is_data_rich(self):
        doc = _make_doc([2000, 3000])
        assert doc.is_data_rich is True


# ── sheet_cell_variance ───────────────────────────────────────────────────────

class TestSheetCellVariance:
    def test_no_sheets_returns_zero(self):
        doc = _make_doc([])
        assert doc.sheet_cell_variance == pytest.approx(0.0)

    def test_all_empty_returns_zero(self):
        doc = _make_doc([0, 0])
        assert doc.sheet_cell_variance == pytest.approx(0.0)

    def test_uniform_sheets_returns_zero(self):
        doc = _make_doc([100, 100, 100])
        assert doc.sheet_cell_variance == pytest.approx(0.0)

    def test_max_variance(self):
        # range = 100 - 0 = 100, max = 100 → variance = 1.0
        doc = _make_doc([100, 0])
        assert doc.sheet_cell_variance == pytest.approx(1.0)

    def test_partial_variance(self):
        # max=100, min=50 → range=50 → variance = 50/100 = 0.5
        doc = _make_doc([100, 50])
        assert doc.sheet_cell_variance == pytest.approx(0.5)

    def test_three_sheets_variance(self):
        # max=300, min=100, range=200 → 200/300 ≈ 0.667
        doc = _make_doc([100, 200, 300])
        assert doc.sheet_cell_variance == pytest.approx(200 / 300)


# ── has_large_sheets ──────────────────────────────────────────────────────────

class TestHasLargeSheets:
    def test_no_sheets_false(self):
        doc = _make_doc([])
        assert doc.has_large_sheets is False

    def test_small_cells_false(self):
        doc = _make_doc([100, 500, 1000])
        assert doc.has_large_sheets is False

    def test_exactly_1000_not_large(self):
        # NOT > 1000
        doc = _make_doc([1000])
        assert doc.has_large_sheets is False

    def test_1001_cells_is_large(self):
        doc = _make_doc([1001])
        assert doc.has_large_sheets is True

    def test_any_large_sheet_true(self):
        doc = _make_doc([100, 2000, 50])
        assert doc.has_large_sheets is True


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_data_rich_with_large_sheets(self):
        doc = _make_doc([2000])
        assert doc.is_data_rich is True
        assert doc.has_large_sheets is True

    def test_variance_consistent_with_range_and_max(self):
        doc = _make_doc([200, 600])
        assert doc.sheet_cell_variance == pytest.approx(
            doc.cell_count_range / doc.max_cells_per_sheet
        )

    def test_uniform_zero_variance(self):
        doc = _make_doc([300, 300, 300])
        assert doc.has_uniform_cell_distribution is True
        assert doc.sheet_cell_variance == pytest.approx(0.0)
