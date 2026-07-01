"""R564: DIF structural properties — is_single_col, has_title, is_multi_row.

Tests for DifModelDocument structural properties added in R564.
Spec refs: FACT-DIF-001 (dif:header, dif:document), FACT-DIF-002 (dif:vector).
"""

import types
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.models import DifModelDocument, DifDoc

SAMPLES = Path("samples/by-format/dif/valid")


def _make_doc(title="", vectors=1, tuples=1, rows=None):
    """Build a minimal DifModelDocument."""
    if rows is None:
        rows = [[] for _ in range(tuples)]
    parsed = types.SimpleNamespace(
        title=title,
        vectors=vectors,
        tuples=tuples,
        rows=rows,
    )
    return DifModelDocument(parsed)


class TestIsSingleCol:
    def test_one_vector_is_single_col(self):
        doc = _make_doc(vectors=1)
        assert doc.is_single_col is True

    def test_zero_vectors_not_single(self):
        doc = _make_doc(vectors=0)
        assert doc.is_single_col is False

    def test_two_vectors_not_single(self):
        doc = _make_doc(vectors=2)
        assert doc.is_single_col is False

    def test_is_single_col_type(self):
        doc = _make_doc(vectors=1)
        assert isinstance(doc.is_single_col, bool)

    def test_is_single_col_consistent_with_col_count(self):
        doc = _make_doc(vectors=1)
        assert doc.is_single_col is True
        assert doc.col_count == 1


class TestHasTitle:
    def test_non_empty_title(self):
        doc = _make_doc(title="MyData")
        assert doc.has_title is True

    def test_empty_title(self):
        doc = _make_doc(title="")
        assert doc.has_title is False

    def test_whitespace_title_truthy(self):
        doc = _make_doc(title="   ")
        # Python bool(" ") is True
        assert doc.has_title is True

    def test_has_title_type(self):
        doc = _make_doc(title="T")
        assert isinstance(doc.has_title, bool)

    def test_no_title_returns_false(self):
        doc = _make_doc(title=None)
        assert doc.has_title is False


class TestIsMultiRow:
    def test_zero_rows_not_multi(self):
        doc = _make_doc(tuples=0, rows=[])
        assert doc.is_multi_row is False

    def test_one_row_not_multi(self):
        doc = _make_doc(tuples=1, rows=[[]])
        assert doc.is_multi_row is False

    def test_two_rows_is_multi(self):
        doc = _make_doc(tuples=2, rows=[[], []])
        assert doc.is_multi_row is True

    def test_many_rows_is_multi(self):
        doc = _make_doc(tuples=5, rows=[[] for _ in range(5)])
        assert doc.is_multi_row is True

    def test_is_multi_row_type(self):
        doc = _make_doc(tuples=2, rows=[[], []])
        assert isinstance(doc.is_multi_row, bool)


class TestStructuralConsistency:
    def test_single_row_not_multi(self):
        doc = _make_doc(tuples=1, rows=[[]])
        assert doc.is_single_row is True
        assert doc.is_multi_row is False

    def test_multi_row_not_single(self):
        doc = _make_doc(tuples=3, rows=[[], [], []])
        assert doc.is_single_row is False
        assert doc.is_multi_row is True

    def test_single_col_consistent_with_vectors(self):
        doc = _make_doc(vectors=1)
        assert doc.is_single_col
        assert doc.col_count == 1

    def test_from_file(self):
        doc = DifModelDocument.from_file(SAMPLES / "numeric-row.dif")
        assert isinstance(doc.is_single_col, bool)
        assert isinstance(doc.has_title, bool)
        assert isinstance(doc.is_multi_row, bool)

    def test_alias_has_properties(self):
        doc = _make_doc(vectors=1, tuples=2, rows=[[], []])
        assert isinstance(doc, DifDoc)
        assert hasattr(doc, "is_single_col")
        assert hasattr(doc, "has_title")
        assert hasattr(doc, "is_multi_row")
