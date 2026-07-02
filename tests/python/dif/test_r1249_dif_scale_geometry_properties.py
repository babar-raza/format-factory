"""Tests for R1249: DifModelDocument scale and geometry properties.

Properties under test:
    is_large    — cell_count > 1000
    aspect_ratio — vectors / row_count (0.0 if no rows)
    is_square   — row_count == vectors and row_count > 0

spec_fact_ref: FACT-DIF-001
"""

import types
import pytest
from dif.models import DifModelDocument


def _make_cell(value=0, text="", value_type="numeric"):
    return types.SimpleNamespace(value=value, text=text, value_type=value_type)


def _make_doc(rows: int, cols: int, title: str = "") -> DifModelDocument:
    """Build a DifModelDocument stub with given grid dimensions."""
    rows_data = [[_make_cell() for _ in range(cols)] for _ in range(rows)]
    parsed = types.SimpleNamespace(
        title=title,
        vectors=cols,
        tuples=rows,
        rows=rows_data,
        path="test.dif",
    )
    return DifModelDocument(parsed)


# ── is_large ──────────────────────────────────────────────────────────────────

class TestIsLarge:
    def test_over_1000_cells_is_large(self):
        doc = _make_doc(rows=10, cols=101)  # 1010 cells
        assert doc.is_large is True

    def test_exactly_1000_not_large(self):
        doc = _make_doc(rows=10, cols=100)  # 1000, not > 1000
        assert doc.is_large is False

    def test_below_1000_not_large(self):
        doc = _make_doc(rows=5, cols=10)  # 50
        assert doc.is_large is False

    def test_empty_not_large(self):
        doc = _make_doc(rows=0, cols=0)
        assert doc.is_large is False

    def test_large_single_row(self):
        doc = _make_doc(rows=1, cols=1001)
        assert doc.is_large is True


# ── aspect_ratio ──────────────────────────────────────────────────────────────

class TestAspectRatio:
    def test_zero_rows_returns_zero(self):
        doc = _make_doc(rows=0, cols=5)
        assert doc.aspect_ratio == 0.0

    def test_square_ratio_one(self):
        doc = _make_doc(rows=10, cols=10)
        assert doc.aspect_ratio == pytest.approx(1.0)

    def test_wide_ratio_gt_one(self):
        doc = _make_doc(rows=5, cols=20)
        assert doc.aspect_ratio == pytest.approx(4.0)

    def test_tall_ratio_lt_one(self):
        doc = _make_doc(rows=20, cols=5)
        assert doc.aspect_ratio == pytest.approx(0.25)

    def test_single_row_ratio(self):
        doc = _make_doc(rows=1, cols=10)
        assert doc.aspect_ratio == pytest.approx(10.0)

    def test_single_col_ratio(self):
        doc = _make_doc(rows=10, cols=1)
        assert doc.aspect_ratio == pytest.approx(0.1)


# ── is_square ─────────────────────────────────────────────────────────────────

class TestIsSquare:
    def test_equal_rows_and_cols_is_square(self):
        doc = _make_doc(rows=5, cols=5)
        assert doc.is_square is True

    def test_unequal_not_square(self):
        doc = _make_doc(rows=5, cols=10)
        assert doc.is_square is False

    def test_zero_rows_not_square(self):
        doc = _make_doc(rows=0, cols=0)
        assert doc.is_square is False

    def test_single_cell_is_square(self):
        doc = _make_doc(rows=1, cols=1)
        assert doc.is_square is True

    def test_more_rows_not_square(self):
        doc = _make_doc(rows=10, cols=5)
        assert doc.is_square is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_square_aspect_ratio_one(self):
        doc = _make_doc(rows=7, cols=7)
        assert doc.is_square is True
        assert doc.aspect_ratio == pytest.approx(1.0)

    def test_wide_not_square_ratio_gt_one(self):
        doc = _make_doc(rows=4, cols=12)
        assert doc.is_wide is True
        assert doc.is_square is False
        assert doc.aspect_ratio > 1.0

    def test_large_and_wide(self):
        doc = _make_doc(rows=10, cols=200)  # 2000 cells
        assert doc.is_large is True
        assert doc.is_wide is True
