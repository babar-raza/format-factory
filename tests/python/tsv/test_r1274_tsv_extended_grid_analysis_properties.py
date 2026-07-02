"""Tests for R1274: TsvDocument extended grid analysis properties.

Properties under test:
    is_narrow_grid — row_count > 3 * column_count (and column_count > 0)
    is_flat_grid   — column_count > 3 * row_count (and row_count > 0)
    is_sparse_data — fill_density < 0.5 and total_cell_count > 0

spec_fact_ref: FACT-TSV-001
"""

import math
import pytest
from tsv.models import TsvDocument


def _make_grid(nrows: int, ncols: int, empty_ratio: float = 0.0) -> TsvDocument:
    """Build a TsvDocument stub with optional empty cell ratio."""
    total = nrows * ncols
    n_empty = int(math.floor(total * empty_ratio))
    rows = []
    for r in range(nrows):
        row = []
        for c in range(ncols):
            cell_idx = r * ncols + c
            row.append("" if cell_idx < n_empty else f"v{cell_idx}")
        rows.append(row)
    return TsvDocument({
        "rows": rows,
        "headers": [],
        "has_header": False,
        "delimiter": "\t",
        "row_count": nrows,
        "column_count": ncols,
    })


def _make_doc(rows: list[list[str]], ncols: int | None = None) -> TsvDocument:
    nc = ncols if ncols is not None else (len(rows[0]) if rows else 0)
    return TsvDocument({
        "rows": rows,
        "headers": [],
        "has_header": False,
        "delimiter": "\t",
        "row_count": len(rows),
        "column_count": nc,
    })


# ── is_narrow_grid ────────────────────────────────────────────────────────────

class TestIsNarrowGrid:
    def test_row_gt_3x_cols(self):
        doc = _make_grid(40, 10)
        assert doc.is_narrow_grid is True

    def test_exactly_3x_not_narrow(self):
        doc = _make_grid(30, 10)
        assert doc.is_narrow_grid is False

    def test_square_not_narrow(self):
        doc = _make_grid(10, 10)
        assert doc.is_narrow_grid is False

    def test_no_columns_not_narrow(self):
        doc = _make_doc([], ncols=0)
        assert doc.is_narrow_grid is False

    def test_tall_but_not_narrow(self):
        doc = _make_grid(20, 10)
        assert doc.is_narrow_grid is False


# ── is_flat_grid ──────────────────────────────────────────────────────────────

class TestIsFlatGrid:
    def test_col_gt_3x_rows(self):
        doc = _make_grid(10, 40)
        assert doc.is_flat_grid is True

    def test_exactly_3x_not_flat(self):
        doc = _make_grid(10, 30)
        assert doc.is_flat_grid is False

    def test_square_not_flat(self):
        doc = _make_grid(10, 10)
        assert doc.is_flat_grid is False

    def test_no_rows_not_flat(self):
        doc = _make_doc([], ncols=0)
        assert doc.is_flat_grid is False

    def test_wide_but_not_flat(self):
        doc = _make_grid(10, 20)
        assert doc.is_flat_grid is False


# ── is_sparse_data ────────────────────────────────────────────────────────────

class TestIsSparseData:
    def test_mostly_empty_is_sparse(self):
        doc = _make_grid(4, 5, empty_ratio=0.8)
        assert doc.is_sparse_data is True

    def test_full_grid_not_sparse(self):
        doc = _make_grid(5, 5, empty_ratio=0.0)
        assert doc.is_sparse_data is False

    def test_empty_doc_not_sparse(self):
        doc = _make_doc([], ncols=0)
        assert doc.is_sparse_data is False

    def test_exactly_50_pct_empty_not_sparse(self):
        doc = _make_grid(2, 5, empty_ratio=0.5)
        assert doc.is_sparse_data is False

    def test_60_pct_empty_is_sparse(self):
        doc = _make_grid(2, 5, empty_ratio=0.6)
        assert doc.is_sparse_data is True


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_narrow_implies_tall(self):
        doc = _make_grid(40, 5)
        assert doc.is_narrow_grid is True
        assert doc.is_tall is True

    def test_flat_implies_wide(self):
        doc = _make_grid(5, 40)
        assert doc.is_flat_grid is True
        assert doc.is_wide is True

    def test_full_grid_fill_density_one(self):
        doc = _make_grid(5, 5, empty_ratio=0.0)
        assert doc.fill_density == pytest.approx(1.0)
        assert doc.is_sparse_data is False
