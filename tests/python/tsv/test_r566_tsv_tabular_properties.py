"""R566: TSV additional tabular properties — is_multi_row, is_single_column, has_multiple_columns.

Tests for TsvDocument tabular properties added in R566.
Spec refs: SAL-TSV-00001 (tsv:record).
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.models import TsvDocument

SAMPLES = Path("samples/by-format/tsv")


def _make_doc(rows=None, headers=None):
    """Build a minimal TsvDocument."""
    data = {
        "rows": rows or [],
        "headers": headers or [],
        "row_count": len(rows or []),
    }
    return TsvDocument(data)


class TestIsMultiRow:
    def test_zero_rows_not_multi(self):
        doc = _make_doc(rows=[])
        assert doc.is_multi_row is False

    def test_one_row_not_multi(self):
        doc = _make_doc(rows=[["a", "b"]])
        assert doc.is_multi_row is False

    def test_two_rows_is_multi(self):
        doc = _make_doc(rows=[["a"], ["b"]])
        assert doc.is_multi_row is True

    def test_many_rows(self):
        doc = _make_doc(rows=[["x"] for _ in range(5)])
        assert doc.is_multi_row is True

    def test_is_multi_row_type(self):
        doc = _make_doc(rows=[["a"], ["b"]])
        assert isinstance(doc.is_multi_row, bool)

    def test_inverse_of_single_row(self):
        doc = _make_doc(rows=[["a"]])
        assert doc.is_single_row is True
        assert doc.is_multi_row is False


class TestIsSingleColumn:
    def test_one_column(self):
        doc = _make_doc(headers=["col1"], rows=[["val"]])
        assert doc.is_single_column is True

    def test_two_columns_not_single(self):
        doc = _make_doc(headers=["a", "b"], rows=[["1", "2"]])
        assert doc.is_single_column is False

    def test_no_data_not_single(self):
        doc = _make_doc(rows=[])
        assert doc.is_single_column is False

    def test_is_single_column_type(self):
        doc = _make_doc(headers=["x"])
        assert isinstance(doc.is_single_column, bool)


class TestHasMultipleColumns:
    def test_one_column_no_multiple(self):
        doc = _make_doc(headers=["col1"])
        assert doc.has_multiple_columns is False

    def test_two_columns(self):
        doc = _make_doc(headers=["a", "b"])
        assert doc.has_multiple_columns is True

    def test_no_columns(self):
        doc = _make_doc(rows=[])
        assert doc.has_multiple_columns is False

    def test_has_multiple_columns_type(self):
        doc = _make_doc(headers=["a", "b"])
        assert isinstance(doc.has_multiple_columns, bool)

    def test_single_and_multiple_exclusive(self):
        doc_single = _make_doc(headers=["only"])
        doc_multi = _make_doc(headers=["a", "b"])
        assert doc_single.is_single_column is True
        assert doc_single.has_multiple_columns is False
        assert doc_multi.is_single_column is False
        assert doc_multi.has_multiple_columns is True


class TestPropertyConsistency:
    def test_from_file(self):
        doc = TsvDocument.from_file(SAMPLES / "minimal-2x2.tsv")
        assert isinstance(doc.is_multi_row, bool)
        assert isinstance(doc.is_single_column, bool)
        assert isinstance(doc.has_multiple_columns, bool)
