"""Tests for R1230: DifModelDocument grid shape classification properties.

Properties under test:
    is_wide     — vectors > row_count
    is_tall     — row_count > vectors
    is_tabular  — row_count > 0 and vectors > 0

spec_fact_ref: FACT-DIF-001
"""

import types
import pytest
from dif.models import DifModelDocument


def _make_doc(row_count: int, vectors: int):
    """Build a DifModelDocument stub with given row and column counts."""
    rows = [[types.SimpleNamespace()] * vectors for _ in range(row_count)]
    parsed = types.SimpleNamespace(
        title="TEST",
        vectors=vectors,
        tuples=row_count,
        rows=rows,
        path="test.dif",
    )
    return DifModelDocument(parsed)


# ── is_wide ───────────────────────────────────────────────────────────────────

class TestIsWide:
    def test_more_columns_than_rows_is_wide(self):
        doc = _make_doc(3, 10)
        assert doc.is_wide is True

    def test_equal_rows_and_columns_not_wide(self):
        doc = _make_doc(5, 5)
        assert doc.is_wide is False

    def test_more_rows_than_columns_not_wide(self):
        doc = _make_doc(10, 3)
        assert doc.is_wide is False

    def test_single_row_multi_col_is_wide(self):
        doc = _make_doc(1, 5)
        assert doc.is_wide is True

    def test_empty_doc_not_wide(self):
        doc = _make_doc(0, 0)
        assert doc.is_wide is False

    def test_single_col_not_wide(self):
        doc = _make_doc(5, 1)
        assert doc.is_wide is False


# ── is_tall ───────────────────────────────────────────────────────────────────

class TestIsTall:
    def test_more_rows_than_columns_is_tall(self):
        doc = _make_doc(10, 3)
        assert doc.is_tall is True

    def test_equal_rows_and_columns_not_tall(self):
        doc = _make_doc(5, 5)
        assert doc.is_tall is False

    def test_more_columns_than_rows_not_tall(self):
        doc = _make_doc(3, 10)
        assert doc.is_tall is False

    def test_single_col_multi_row_is_tall(self):
        doc = _make_doc(5, 1)
        assert doc.is_tall is True

    def test_empty_doc_not_tall(self):
        doc = _make_doc(0, 0)
        assert doc.is_tall is False

    def test_single_row_not_tall(self):
        doc = _make_doc(1, 5)
        assert doc.is_tall is False


# ── is_tabular ────────────────────────────────────────────────────────────────

class TestIsTabular:
    def test_has_rows_and_cols_is_tabular(self):
        doc = _make_doc(3, 4)
        assert doc.is_tabular is True

    def test_zero_rows_not_tabular(self):
        doc = _make_doc(0, 5)
        assert doc.is_tabular is False

    def test_zero_cols_not_tabular(self):
        doc = _make_doc(5, 0)
        assert doc.is_tabular is False

    def test_both_zero_not_tabular(self):
        doc = _make_doc(0, 0)
        assert doc.is_tabular is False

    def test_single_row_single_col_is_tabular(self):
        doc = _make_doc(1, 1)
        assert doc.is_tabular is True

    def test_large_tabular_doc(self):
        doc = _make_doc(100, 50)
        assert doc.is_tabular is True


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_wide_is_not_tall(self):
        doc = _make_doc(2, 10)
        assert doc.is_wide is True
        assert doc.is_tall is False

    def test_tall_is_not_wide(self):
        doc = _make_doc(10, 2)
        assert doc.is_tall is True
        assert doc.is_wide is False

    def test_square_neither_wide_nor_tall(self):
        doc = _make_doc(5, 5)
        assert doc.is_wide is False
        assert doc.is_tall is False

    def test_tabular_wide_doc(self):
        doc = _make_doc(2, 8)
        assert doc.is_tabular is True
        assert doc.is_wide is True

    def test_tabular_tall_doc(self):
        doc = _make_doc(8, 2)
        assert doc.is_tabular is True
        assert doc.is_tall is True

    def test_non_tabular_not_wide_not_tall(self):
        doc = _make_doc(0, 0)
        assert doc.is_tabular is False
        assert doc.is_wide is False
        assert doc.is_tall is False
