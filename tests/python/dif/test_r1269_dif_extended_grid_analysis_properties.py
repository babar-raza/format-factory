"""Tests for R1269: DifModelDocument extended grid analysis properties.

Properties under test:
    is_narrow          — row_count > 3 * vectors (and vectors > 0)
    is_flat            — vectors > 3 * row_count (and row_count > 0)
    cell_density_ratio — cell_count / (row_count * vectors), 0.0 if empty

spec_fact_ref: FACT-DIF-001
"""

import types
import pytest
from dif.models import DifModelDocument


def _make_doc(rows: int, vectors: int, cells: int | None = None) -> DifModelDocument:
    """Build a DifModelDocument stub."""
    actual_cells = cells if cells is not None else rows * vectors
    parsed = types.SimpleNamespace(
        title="test",
        vectors=vectors,
        tuples=rows,
        rows=[[f"v{c}" for c in range(vectors)] for _ in range(rows)],
        cells=[[f"v{c}" for c in range(vectors)] for _ in range(rows)],
    )
    doc = DifModelDocument(parsed)
    # Override cell_count via subclass trick — check actual cell_count property
    return doc


# ── is_narrow ─────────────────────────────────────────────────────────────────

class TestIsNarrow:
    def test_row_gt_3x_vectors(self):
        # 40 rows, 10 cols → 40 > 30 → narrow
        doc = _make_doc(40, 10)
        assert doc.is_narrow is True

    def test_row_exactly_3x_not_narrow(self):
        # 30 rows, 10 cols → 30 = 30 → not narrow (> not >=)
        doc = _make_doc(30, 10)
        assert doc.is_narrow is False

    def test_square_not_narrow(self):
        doc = _make_doc(10, 10)
        assert doc.is_narrow is False

    def test_no_vectors_not_narrow(self):
        doc = _make_doc(100, 0)
        assert doc.is_narrow is False

    def test_tall_but_not_narrow(self):
        # 20 rows, 10 cols → 20 < 30 → not narrow
        doc = _make_doc(20, 10)
        assert doc.is_narrow is False


# ── is_flat ───────────────────────────────────────────────────────────────────

class TestIsFlat:
    def test_vectors_gt_3x_rows(self):
        # 10 rows, 40 cols → 40 > 30 → flat
        doc = _make_doc(10, 40)
        assert doc.is_flat is True

    def test_vectors_exactly_3x_not_flat(self):
        # 10 rows, 30 cols → 30 = 30 → not flat
        doc = _make_doc(10, 30)
        assert doc.is_flat is False

    def test_square_not_flat(self):
        doc = _make_doc(10, 10)
        assert doc.is_flat is False

    def test_no_rows_not_flat(self):
        doc = _make_doc(0, 100)
        assert doc.is_flat is False

    def test_wide_but_not_flat(self):
        # 10 rows, 20 cols → 20 < 30 → not flat
        doc = _make_doc(10, 20)
        assert doc.is_flat is False


# ── cell_density_ratio ────────────────────────────────────────────────────────

class TestCellDensityRatio:
    def test_empty_returns_zero(self):
        doc = _make_doc(0, 0)
        assert doc.cell_density_ratio == pytest.approx(0.0)

    def test_full_grid_ratio_one(self):
        # 10 rows * 5 cols = 50 cells, all filled
        doc = _make_doc(10, 5)
        # cell_count = len(rows) * vectors = 10*5 = 50, theoretical = 10*5 = 50
        assert doc.cell_density_ratio == pytest.approx(1.0)

    def test_no_vectors_returns_zero(self):
        doc = _make_doc(10, 0)
        assert doc.cell_density_ratio == pytest.approx(0.0)

    def test_no_rows_returns_zero(self):
        doc = _make_doc(0, 10)
        assert doc.cell_density_ratio == pytest.approx(0.0)


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_narrow_implies_tall(self):
        doc = _make_doc(40, 5)
        assert doc.is_narrow is True
        assert doc.is_tall is True
        assert doc.is_flat is False

    def test_flat_implies_wide(self):
        doc = _make_doc(5, 40)
        assert doc.is_flat is True
        assert doc.is_wide is True
        assert doc.is_narrow is False

    def test_square_is_neither_narrow_nor_flat(self):
        doc = _make_doc(10, 10)
        assert doc.is_narrow is False
        assert doc.is_flat is False
        assert doc.is_square is True
