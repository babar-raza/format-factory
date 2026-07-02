"""Tests for R1268: GnumericDocument sheet cell distribution analysis properties.

Properties under test:
    min_cells_per_sheet         — minimum cell count in any sheet (0 if no sheets)
    cell_count_range            — max_cells_per_sheet - min_cells_per_sheet
    has_uniform_cell_distribution — all sheets have same cell count

spec_fact_ref: FACT-GNUMERIC-001
"""

import pytest
from gnumeric.models import GnumericDocument


def _make_doc(cell_counts_per_sheet: list[int], sheet_count: int | None = None) -> GnumericDocument:
    """Build a GnumericDocument stub with given per-sheet cell counts."""
    sheets = [
        {"name": f"Sheet{i+1}", "cell_grid": {j: {"value": str(j)} for j in range(c)}}
        for i, c in enumerate(cell_counts_per_sheet)
    ]
    total_cells = sum(cell_counts_per_sheet)
    return GnumericDocument({
        "is_gnumeric": True,
        "sheet_count": sheet_count if sheet_count is not None else len(cell_counts_per_sheet),
        "cell_count": total_cells,
        "sheets": sheets,
    })


# ── min_cells_per_sheet ───────────────────────────────────────────────────────

class TestMinCellsPerSheet:
    def test_no_sheets_returns_zero(self):
        doc = _make_doc([])
        assert doc.min_cells_per_sheet == 0

    def test_single_sheet_min(self):
        doc = _make_doc([50])
        assert doc.min_cells_per_sheet == 50

    def test_picks_smallest(self):
        doc = _make_doc([100, 50, 200])
        assert doc.min_cells_per_sheet == 50

    def test_all_same(self):
        doc = _make_doc([75, 75, 75])
        assert doc.min_cells_per_sheet == 75

    def test_one_empty_sheet(self):
        doc = _make_doc([0, 100, 200])
        assert doc.min_cells_per_sheet == 0


# ── cell_count_range ──────────────────────────────────────────────────────────

class TestCellCountRange:
    def test_no_sheets_range_zero(self):
        doc = _make_doc([])
        assert doc.cell_count_range == 0

    def test_single_sheet_range_zero(self):
        doc = _make_doc([100])
        assert doc.cell_count_range == 0

    def test_equal_sheets_range_zero(self):
        doc = _make_doc([200, 200, 200])
        assert doc.cell_count_range == 0

    def test_varied_sheets_range(self):
        doc = _make_doc([100, 500])
        assert doc.cell_count_range == 400

    def test_range_is_max_minus_min(self):
        doc = _make_doc([50, 150, 300])
        assert doc.cell_count_range == doc.max_cells_per_sheet - doc.min_cells_per_sheet


# ── has_uniform_cell_distribution ─────────────────────────────────────────────

class TestHasUniformCellDistribution:
    def test_no_sheets_is_uniform(self):
        doc = _make_doc([])
        assert doc.has_uniform_cell_distribution is True

    def test_single_sheet_is_uniform(self):
        doc = _make_doc([100])
        assert doc.has_uniform_cell_distribution is True

    def test_equal_sheets_uniform(self):
        doc = _make_doc([100, 100, 100])
        assert doc.has_uniform_cell_distribution is True

    def test_different_sizes_not_uniform(self):
        doc = _make_doc([100, 200])
        assert doc.has_uniform_cell_distribution is False

    def test_one_empty_sheet_not_uniform(self):
        doc = _make_doc([0, 100])
        assert doc.has_uniform_cell_distribution is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_uniform_implies_zero_range(self):
        doc = _make_doc([150, 150])
        assert doc.has_uniform_cell_distribution is True
        assert doc.cell_count_range == 0

    def test_nonzero_range_implies_not_uniform(self):
        doc = _make_doc([100, 300])
        assert doc.cell_count_range > 0
        assert doc.has_uniform_cell_distribution is False

    def test_range_consistent_with_bounds(self):
        doc = _make_doc([50, 100, 200, 350])
        assert doc.cell_count_range == doc.max_cells_per_sheet - doc.min_cells_per_sheet
        assert doc.min_cells_per_sheet == 50
        assert doc.max_cells_per_sheet == 350
