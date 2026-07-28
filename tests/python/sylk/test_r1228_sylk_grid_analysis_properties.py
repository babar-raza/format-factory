"""Tests for R1228: SylkModelDocument grid density and size classification properties.

Properties under test:
    is_dense       — fill_ratio > 0.8
    is_sparse      — fill_ratio < 0.2
    is_large_grid  — cell_count > 1000

spec_fact_ref: SAL-SYLK-00001
"""

import types
import pytest
from sylk.models import SylkModelDocument


def _make_cell(value_type: str = "numeric"):
    return types.SimpleNamespace(value_type=value_type)


def _make_doc(cell_count: int, nonempty_count: int, rows: int = 10, cols: int = 10):
    """Build a stub SylkModelDocument with the given cell/nonempty counts."""
    cells = (
        [_make_cell("numeric")] * nonempty_count
        + [_make_cell("empty")] * (cell_count - nonempty_count)
    )
    parsed = types.SimpleNamespace(
        cells=cells,
        rows=rows,
        cols=cols,
        path="test.slk",
        id_line="ID;P",
    )
    return SylkModelDocument(parsed)


# ── is_dense ──────────────────────────────────────────────────────────────────

class TestIsDense:
    def test_all_nonempty_is_dense(self):
        doc = _make_doc(10, 10)
        assert doc.is_dense is True

    def test_ratio_above_08_is_dense(self):
        doc = _make_doc(10, 9)  # fill_ratio = 0.9
        assert doc.is_dense is True

    def test_ratio_exactly_08_not_dense(self):
        doc = _make_doc(10, 8)  # fill_ratio = 0.8 (not > 0.8)
        assert doc.is_dense is False

    def test_ratio_below_08_not_dense(self):
        doc = _make_doc(10, 7)  # fill_ratio = 0.7
        assert doc.is_dense is False

    def test_empty_doc_not_dense(self):
        doc = _make_doc(0, 0)
        assert doc.is_dense is False

    def test_all_empty_cells_not_dense(self):
        doc = _make_doc(5, 0)  # fill_ratio = 0.0
        assert doc.is_dense is False

    def test_large_dense_grid(self):
        doc = _make_doc(1000, 950)  # fill_ratio = 0.95
        assert doc.is_dense is True


# ── is_sparse ─────────────────────────────────────────────────────────────────

class TestIsSparse:
    def test_all_empty_is_sparse(self):
        doc = _make_doc(10, 0)  # fill_ratio = 0.0
        assert doc.is_sparse is True

    def test_ratio_below_02_is_sparse(self):
        doc = _make_doc(10, 1)  # fill_ratio = 0.1
        assert doc.is_sparse is True

    def test_ratio_exactly_02_not_sparse(self):
        doc = _make_doc(10, 2)  # fill_ratio = 0.2 (not < 0.2)
        assert doc.is_sparse is False

    def test_ratio_above_02_not_sparse(self):
        doc = _make_doc(10, 5)  # fill_ratio = 0.5
        assert doc.is_sparse is False

    def test_zero_cells_is_sparse(self):
        doc = _make_doc(0, 0)  # fill_ratio = 0.0
        assert doc.is_sparse is True

    def test_dense_doc_not_sparse(self):
        doc = _make_doc(10, 10)  # fill_ratio = 1.0
        assert doc.is_sparse is False

    def test_single_nonempty_out_of_many_is_sparse(self):
        doc = _make_doc(100, 1)  # fill_ratio = 0.01
        assert doc.is_sparse is True


# ── is_large_grid ─────────────────────────────────────────────────────────────

class TestIsLargeGrid:
    def test_over_1000_cells_is_large(self):
        doc = _make_doc(1001, 0)
        assert doc.is_large_grid is True

    def test_exactly_1000_not_large(self):
        doc = _make_doc(1000, 0)  # not > 1000
        assert doc.is_large_grid is False

    def test_below_1000_not_large(self):
        doc = _make_doc(500, 0)
        assert doc.is_large_grid is False

    def test_empty_doc_not_large(self):
        doc = _make_doc(0, 0)
        assert doc.is_large_grid is False

    def test_small_doc_not_large(self):
        doc = _make_doc(10, 5)
        assert doc.is_large_grid is False

    def test_boundary_1001_is_large(self):
        doc = _make_doc(1001, 500)
        assert doc.is_large_grid is True

    def test_very_large_grid(self):
        doc = _make_doc(10000, 8000)
        assert doc.is_large_grid is True


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_dense_is_not_sparse(self):
        doc = _make_doc(10, 9)  # fill_ratio = 0.9
        assert doc.is_dense is True
        assert doc.is_sparse is False

    def test_sparse_is_not_dense(self):
        doc = _make_doc(10, 1)  # fill_ratio = 0.1
        assert doc.is_sparse is True
        assert doc.is_dense is False

    def test_medium_fill_neither_dense_nor_sparse(self):
        doc = _make_doc(10, 5)  # fill_ratio = 0.5
        assert doc.is_dense is False
        assert doc.is_sparse is False

    def test_large_sparse_grid(self):
        doc = _make_doc(1001, 1)  # fill_ratio very low
        assert doc.is_large_grid is True
        assert doc.is_sparse is True
        assert doc.is_dense is False
