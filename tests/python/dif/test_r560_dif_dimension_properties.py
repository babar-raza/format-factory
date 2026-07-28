"""R560: DIF dimension properties — col_count, is_empty, is_single_row.

Tests for DifModelDocument dimension properties added in R560.
Spec refs: SAL-DIF-00001.
"""

import types
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.models import DifModelDocument, DifDoc

SAMPLES = Path("samples/by-format/dif/valid")


def _make_doc(vectors=2, tuples=2, rows=None):
    """Build a minimal DifModelDocument from a parsed stub."""
    if rows is None:
        rows = [[""] * vectors for _ in range(tuples)]
    return DifModelDocument(types.SimpleNamespace(
        title="TEST",
        vectors=vectors,
        tuples=tuples,
        rows=rows,
    ))


class TestColCount:
    def test_col_count_equals_vectors(self):
        doc = _make_doc(vectors=3)
        assert doc.col_count == 3

    def test_col_count_single_column(self):
        doc = _make_doc(vectors=1)
        assert doc.col_count == 1

    def test_col_count_type(self):
        doc = _make_doc(vectors=4)
        assert isinstance(doc.col_count, int)

    def test_col_count_matches_vectors_property(self):
        for v in [1, 2, 5, 10]:
            doc = _make_doc(vectors=v)
            assert doc.col_count == doc.vectors


class TestIsEmpty:
    def test_zero_rows_is_empty(self):
        doc = _make_doc(tuples=0, rows=[])
        assert doc.is_empty is True

    def test_one_row_not_empty(self):
        doc = _make_doc(tuples=1, rows=[["a", "b"]])
        assert doc.is_empty is False

    def test_two_rows_not_empty(self):
        doc = _make_doc(tuples=2, rows=[["a"], ["b"]])
        assert doc.is_empty is False

    def test_is_empty_type(self):
        doc = _make_doc(tuples=0, rows=[])
        assert isinstance(doc.is_empty, bool)


class TestIsSingleRow:
    def test_one_row_is_single(self):
        doc = _make_doc(tuples=1, rows=[["a", "b"]])
        assert doc.is_single_row is True

    def test_zero_rows_not_single(self):
        doc = _make_doc(tuples=0, rows=[])
        assert doc.is_single_row is False

    def test_two_rows_not_single(self):
        doc = _make_doc(tuples=2, rows=[["a"], ["b"]])
        assert doc.is_single_row is False

    def test_is_single_row_type(self):
        doc = _make_doc(tuples=1, rows=[["a"]])
        assert isinstance(doc.is_single_row, bool)


class TestDimensionConsistency:
    def test_empty_and_single_row_exclusive(self):
        empty = _make_doc(tuples=0, rows=[])
        single = _make_doc(tuples=1, rows=[["x"]])
        assert empty.is_empty and not empty.is_single_row
        assert single.is_single_row and not single.is_empty

    def test_is_empty_consistent_with_row_count(self):
        for n in [0, 1, 2, 5]:
            rows = [["x"] for _ in range(n)]
            doc = _make_doc(tuples=n, rows=rows)
            assert doc.is_empty == (n == 0)

    def test_from_file_minimal_2x2(self):
        doc = DifModelDocument.from_file(SAMPLES / "minimal-2x2.dif")
        assert isinstance(doc.col_count, int)
        assert isinstance(doc.is_empty, bool)
        assert isinstance(doc.is_single_row, bool)
        assert doc.col_count == doc.vectors

    def test_from_file_single_cell(self):
        doc = DifModelDocument.from_file(SAMPLES / "single-cell.dif")
        assert isinstance(doc.col_count, int)
        assert isinstance(doc.is_single_row, bool)

    def test_alias_dif_doc_has_properties(self):
        doc = DifDoc.from_file(SAMPLES / "minimal-2x2.dif")
        assert hasattr(doc, "col_count")
        assert hasattr(doc, "is_empty")
        assert hasattr(doc, "is_single_row")
