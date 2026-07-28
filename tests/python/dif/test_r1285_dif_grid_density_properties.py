"""Tests for R1285: DifModelDocument grid density and fill analysis properties.

Properties under test:
    is_dense_grid      — cell_density_ratio > 0.8
    is_sparse_grid     — is_tabular and cell_density_ratio < 0.2
    fill_classification — 'empty', 'sparse', 'partial', or 'dense'

spec_fact_ref: SAL-DIF-00001
"""

import types
import pytest
from dif.models import DifModelDocument


def _make_doc(row_count: int, vectors: int, cell_count: int, title: str = "") -> DifModelDocument:
    # Each row is a list of cells; distribute cell_count evenly then remainder
    rows = []
    remaining = cell_count
    for i in range(row_count):
        row_cells = min(remaining, vectors)
        rows.append([None] * row_cells)
        remaining -= row_cells
    parsed = types.SimpleNamespace(
        title=title,
        vectors=vectors,
        tuples=row_count,
        rows=rows,
        path="test.dif",
    )
    return DifModelDocument(parsed)


# ── is_dense_grid ─────────────────────────────────────────────────────────────

class TestIsDenseGrid:
    def test_empty_grid_not_dense(self):
        doc = _make_doc(0, 0, 0)
        assert doc.is_dense_grid is False

    def test_fully_filled_is_dense(self):
        # 4x3 = 12 cells, 12 actual → ratio = 1.0
        doc = _make_doc(4, 3, 12)
        assert doc.is_dense_grid is True

    def test_barely_dense(self):
        # 10x10 = 100 max, 81 actual → ratio = 0.81 > 0.8
        doc = _make_doc(10, 10, 81)
        assert doc.is_dense_grid is True

    def test_exactly_80_not_dense(self):
        # ratio = 0.8, NOT > 0.8
        doc = _make_doc(10, 10, 80)
        assert doc.is_dense_grid is False

    def test_sparse_not_dense(self):
        # 5x5 = 25 max, 5 actual → ratio = 0.2
        doc = _make_doc(5, 5, 5)
        assert doc.is_dense_grid is False


# ── is_sparse_grid ────────────────────────────────────────────────────────────

class TestIsSparseGrid:
    def test_empty_grid_not_sparse(self):
        # is_tabular = False → not sparse
        doc = _make_doc(0, 0, 0)
        assert doc.is_sparse_grid is False

    def test_fully_filled_not_sparse(self):
        doc = _make_doc(4, 3, 12)
        assert doc.is_sparse_grid is False

    def test_low_density_is_sparse(self):
        # 10x10 = 100 max, 10 actual → ratio = 0.1 < 0.2
        doc = _make_doc(10, 10, 10)
        assert doc.is_sparse_grid is True

    def test_exactly_20_not_sparse(self):
        # ratio = 0.2, NOT < 0.2
        doc = _make_doc(10, 10, 20)
        assert doc.is_sparse_grid is False

    def test_partial_fill_not_sparse(self):
        # ratio = 0.5
        doc = _make_doc(10, 10, 50)
        assert doc.is_sparse_grid is False


# ── fill_classification ───────────────────────────────────────────────────────

class TestFillClassification:
    def test_empty_grid_is_empty(self):
        doc = _make_doc(0, 0, 0)
        assert doc.fill_classification == "empty"

    def test_very_sparse_is_sparse(self):
        # ratio = 0.1 < 0.2 → sparse
        doc = _make_doc(10, 10, 10)
        assert doc.fill_classification == "sparse"

    def test_partial_fill_is_partial(self):
        # ratio = 0.5 → partial
        doc = _make_doc(10, 10, 50)
        assert doc.fill_classification == "partial"

    def test_dense_fill_is_dense(self):
        # ratio = 0.9 > 0.8 → dense
        doc = _make_doc(10, 10, 90)
        assert doc.fill_classification == "dense"

    def test_full_fill_is_dense(self):
        # ratio = 1.0 → dense
        doc = _make_doc(5, 4, 20)
        assert doc.fill_classification == "dense"

    def test_exactly_0_2_is_partial(self):
        # ratio = 0.2, >= 0.2, <= 0.8 → partial
        doc = _make_doc(10, 10, 20)
        assert doc.fill_classification == "partial"


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_dense_grid_fill_classification_dense(self):
        doc = _make_doc(5, 5, 24)
        # 24/25 = 0.96 > 0.8
        assert doc.is_dense_grid is True
        assert doc.fill_classification == "dense"

    def test_sparse_grid_fill_classification_sparse(self):
        doc = _make_doc(5, 5, 3)
        # 3/25 = 0.12 < 0.2
        assert doc.is_sparse_grid is True
        assert doc.fill_classification == "sparse"

    def test_dense_and_sparse_mutually_exclusive(self):
        doc = _make_doc(10, 10, 50)
        # ratio = 0.5 → neither dense nor sparse
        assert doc.is_dense_grid is False
        assert doc.is_sparse_grid is False
        assert doc.fill_classification == "partial"
