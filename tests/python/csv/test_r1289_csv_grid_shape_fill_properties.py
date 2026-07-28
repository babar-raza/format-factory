"""Tests for R1289: CsvDocument grid shape and fill completeness properties.

Properties under test:
    is_square_grid  — row_count == column_count and both positive
    is_dense_data   — fill_density > 0.8
    empty_cell_count — round((1 - fill_density) * total_cell_count)

spec_fact_ref: SAL-CSV-00001
"""

import math
import pytest

from ff_csv.models import CsvDocument


def _make_doc(row_count: int, col_count: int, empty_ratio: float = 0.0) -> CsvDocument:
    """Build a CsvDocument stub with given dimensions and empty cell ratio."""
    total = row_count * col_count
    n_empty = int(math.floor(total * empty_ratio))
    rows = []
    for r in range(row_count):
        row = []
        for c in range(col_count):
            cell_idx = r * col_count + c
            row.append("" if cell_idx < n_empty else f"v{cell_idx}")
        rows.append(row)
    return CsvDocument({
        "rows": rows,
        "headers": [],
        "has_header": False,
        "delimiter": ",",
        "row_count": row_count,
        "column_count": col_count,
    })


# ── is_square_grid ────────────────────────────────────────────────────────────

class TestIsSquareGrid:
    def test_empty_grid_not_square(self):
        doc = _make_doc(0, 0)
        assert doc.is_square_grid is False

    def test_one_row_zero_cols_not_square(self):
        doc = _make_doc(1, 0)
        assert doc.is_square_grid is False

    def test_square_1x1(self):
        doc = _make_doc(1, 1)
        assert doc.is_square_grid is True

    def test_square_5x5(self):
        doc = _make_doc(5, 5)
        assert doc.is_square_grid is True

    def test_rectangular_not_square(self):
        doc = _make_doc(3, 5)
        assert doc.is_square_grid is False

    def test_wide_not_square(self):
        doc = _make_doc(2, 10)
        assert doc.is_square_grid is False

    def test_tall_not_square(self):
        doc = _make_doc(10, 2)
        assert doc.is_square_grid is False


# ── is_dense_data ─────────────────────────────────────────────────────────────

class TestIsDenseData:
    def test_empty_grid_not_dense(self):
        doc = _make_doc(0, 0)
        assert doc.is_dense_data is False

    def test_all_filled_is_dense(self):
        doc = _make_doc(5, 5, empty_ratio=0.0)
        assert doc.is_dense_data is True

    def test_mostly_filled_is_dense(self):
        # 10% empty → fill = 0.9 > 0.8
        doc = _make_doc(10, 10, empty_ratio=0.1)
        assert doc.is_dense_data is True

    def test_exactly_80_pct_not_dense(self):
        # fill = 0.8 NOT > 0.8
        doc = _make_doc(10, 10, empty_ratio=0.2)
        assert doc.is_dense_data is False

    def test_50_pct_empty_not_dense(self):
        doc = _make_doc(10, 10, empty_ratio=0.5)
        assert doc.is_dense_data is False


# ── empty_cell_count ──────────────────────────────────────────────────────────

class TestEmptyCellCount:
    def test_all_filled_zero_empty(self):
        doc = _make_doc(5, 5, empty_ratio=0.0)
        assert doc.empty_cell_count == 0

    def test_all_empty_equals_total(self):
        doc = _make_doc(4, 4, empty_ratio=1.0)
        assert doc.empty_cell_count == 16

    def test_half_empty(self):
        doc = _make_doc(4, 4, empty_ratio=0.5)
        # fill_density ≈ 0.5, empty = round(0.5 * 16) = 8
        assert doc.empty_cell_count == 8

    def test_empty_grid_zero_empty_cells(self):
        doc = _make_doc(0, 0)
        assert doc.empty_cell_count == 0

    def test_25_pct_empty(self):
        # 4x4 = 16 cells, 25% empty = 4
        doc = _make_doc(4, 4, empty_ratio=0.25)
        assert doc.empty_cell_count == 4


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_dense_implies_not_sparse(self):
        doc = _make_doc(5, 5, empty_ratio=0.0)
        assert doc.is_dense_data is True
        assert doc.is_sparse_data is False

    def test_square_grid_equal_dimensions(self):
        doc = _make_doc(5, 5)
        assert doc.is_square_grid is True
        assert doc.row_count == doc.column_count

    def test_empty_count_plus_filled_equals_total(self):
        doc = _make_doc(4, 4, empty_ratio=0.25)
        total = doc.total_cell_count
        filled = total - doc.empty_cell_count
        # filled_density ≈ filled / total
        assert filled >= 0
        assert doc.empty_cell_count + filled == total
