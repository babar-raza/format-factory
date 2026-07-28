"""Tests for R1273: CsvDocument extended grid analysis properties.

Properties under test:
    is_narrow_grid — row_count > 3 * column_count (and column_count > 0)
    is_flat_grid   — column_count > 3 * row_count (and row_count > 0)
    is_sparse_data — fill_density < 0.5 and total_cell_count > 0

spec_fact_ref: SAL-CSV-00001
"""

import pytest

from ff_csv.models import CsvDocument


def _make_doc(rows: list[list[str]], headers: list[str] | None = None, delimiter: str = ",") -> CsvDocument:
    """Build a CsvDocument stub."""
    cols = len(rows[0]) if rows else (len(headers) if headers else 0)
    return CsvDocument({
        "rows": rows,
        "headers": headers or [],
        "has_header": headers is not None,
        "delimiter": delimiter,
        "row_count": len(rows),
        "column_count": cols,
    })


def _make_grid(nrows: int, ncols: int, empty_ratio: float = 0.0) -> CsvDocument:
    """Build a grid with optional empty cell ratio."""
    import math
    total = nrows * ncols
    n_empty = int(math.floor(total * empty_ratio))
    rows = []
    for r in range(nrows):
        row = []
        for c in range(ncols):
            cell_idx = r * ncols + c
            row.append("" if cell_idx < n_empty else f"v{cell_idx}")
        rows.append(row)
    return CsvDocument({
        "rows": rows,
        "headers": [],
        "has_header": False,
        "delimiter": ",",
        "row_count": nrows,
        "column_count": ncols,
    })


# ── is_narrow_grid ────────────────────────────────────────────────────────────

class TestIsNarrowGrid:
    def test_row_gt_3x_cols(self):
        # 40 rows, 10 cols → 40 > 30 → narrow
        doc = _make_grid(40, 10)
        assert doc.is_narrow_grid is True

    def test_exactly_3x_not_narrow(self):
        # 30 rows, 10 cols → 30 = 30 → not narrow
        doc = _make_grid(30, 10)
        assert doc.is_narrow_grid is False

    def test_square_not_narrow(self):
        doc = _make_grid(10, 10)
        assert doc.is_narrow_grid is False

    def test_no_columns_not_narrow(self):
        doc = _make_doc([])
        assert doc.is_narrow_grid is False

    def test_tall_but_not_narrow(self):
        # 20 rows, 10 cols → not > 30
        doc = _make_grid(20, 10)
        assert doc.is_narrow_grid is False


# ── is_flat_grid ──────────────────────────────────────────────────────────────

class TestIsFlatGrid:
    def test_col_gt_3x_rows(self):
        # 10 rows, 40 cols → 40 > 30 → flat
        doc = _make_grid(10, 40)
        assert doc.is_flat_grid is True

    def test_exactly_3x_not_flat(self):
        # 10 rows, 30 cols → 30 = 30 → not flat
        doc = _make_grid(10, 30)
        assert doc.is_flat_grid is False

    def test_square_not_flat(self):
        doc = _make_grid(10, 10)
        assert doc.is_flat_grid is False

    def test_no_rows_not_flat(self):
        doc = _make_doc([])
        assert doc.is_flat_grid is False

    def test_wide_but_not_flat(self):
        doc = _make_grid(10, 20)
        assert doc.is_flat_grid is False


# ── is_sparse_data ────────────────────────────────────────────────────────────

class TestIsSparseData:
    def test_60_pct_empty_is_sparse(self):
        # 6 empty out of 10 = 60% empty → fill=40% < 50%
        doc = _make_grid(2, 5, empty_ratio=0.6)
        assert doc.is_sparse_data is True

    def test_full_grid_not_sparse(self):
        doc = _make_grid(5, 5, empty_ratio=0.0)
        assert doc.is_sparse_data is False

    def test_empty_doc_not_sparse(self):
        doc = _make_doc([])
        assert doc.is_sparse_data is False

    def test_exactly_50_pct_empty_not_sparse(self):
        # fill = 50%, not < 50%
        doc = _make_grid(2, 5, empty_ratio=0.5)
        assert doc.is_sparse_data is False

    def test_mostly_empty_is_sparse(self):
        doc = _make_grid(4, 5, empty_ratio=0.8)
        assert doc.is_sparse_data is True


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_narrow_implies_tall(self):
        doc = _make_grid(40, 5)
        assert doc.is_narrow_grid is True
        assert doc.is_tall is True
        assert doc.is_flat_grid is False

    def test_flat_implies_wide(self):
        doc = _make_grid(5, 40)
        assert doc.is_flat_grid is True
        assert doc.is_wide is True
        assert doc.is_narrow_grid is False

    def test_full_grid_not_sparse(self):
        doc = _make_grid(10, 10)
        assert doc.fill_density == pytest.approx(1.0)
        assert doc.is_sparse_data is False
