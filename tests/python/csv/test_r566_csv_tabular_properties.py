"""R566: CSV additional tabular properties — is_multi_row, is_single_column, has_multiple_columns.

Tests for CsvDocument tabular properties added in R566.
Spec refs: FACT-CSV-001 (csv:record).
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))


from src.python.csv.models import CsvDocument

SAMPLES = Path("samples/by-format/csv")


def _make_doc(rows=None, headers=None):
    """Build a minimal CsvDocument."""
    data = {
        "rows": rows or [],
        "headers": headers or [],
        "row_count": len(rows or []),
        "delimiter": ",",
    }
    return CsvDocument(data)


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

    def test_many_rows_is_multi(self):
        doc = _make_doc(rows=[["x"] for _ in range(10)])
        assert doc.is_multi_row is True

    def test_is_multi_row_type(self):
        doc = _make_doc(rows=[["a"], ["b"]])
        assert isinstance(doc.is_multi_row, bool)

    def test_multi_row_not_single(self):
        doc = _make_doc(rows=[["a"], ["b"]])
        assert doc.is_multi_row is True
        assert doc.is_single_row is False


class TestIsSingleColumn:
    def test_no_columns_not_single(self):
        doc = _make_doc(rows=[])
        assert doc.is_single_column is False

    def test_one_column(self):
        doc = _make_doc(headers=["col1"], rows=[["val"]])
        assert doc.is_single_column is True

    def test_two_columns_not_single(self):
        doc = _make_doc(headers=["a", "b"], rows=[["1", "2"]])
        assert doc.is_single_column is False

    def test_is_single_column_type(self):
        doc = _make_doc(headers=["x"], rows=[["v"]])
        assert isinstance(doc.is_single_column, bool)


class TestHasMultipleColumns:
    def test_no_columns(self):
        doc = _make_doc(rows=[])
        assert doc.has_multiple_columns is False

    def test_one_column(self):
        doc = _make_doc(headers=["col1"], rows=[["v"]])
        assert doc.has_multiple_columns is False

    def test_two_columns(self):
        doc = _make_doc(headers=["a", "b"], rows=[["1", "2"]])
        assert doc.has_multiple_columns is True

    def test_three_columns(self):
        doc = _make_doc(headers=["a", "b", "c"], rows=[["1", "2", "3"]])
        assert doc.has_multiple_columns is True

    def test_has_multiple_columns_type(self):
        doc = _make_doc(headers=["a", "b"])
        assert isinstance(doc.has_multiple_columns, bool)


class TestTabularPropertyConsistency:
    def test_single_col_not_multiple(self):
        doc = _make_doc(headers=["col"], rows=[["v"]])
        assert doc.is_single_column is True
        assert doc.has_multiple_columns is False

    def test_multiple_cols_not_single(self):
        doc = _make_doc(headers=["a", "b"], rows=[["1", "2"]])
        assert doc.is_single_column is False
        assert doc.has_multiple_columns is True

    def test_single_row_not_multi_row(self):
        doc = _make_doc(rows=[["a"]])
        assert doc.is_single_row is True
        assert doc.is_multi_row is False

    def test_from_file(self):
        doc = CsvDocument.from_file(SAMPLES / "minimal-2x2.csv")
        assert isinstance(doc.is_multi_row, bool)
        assert isinstance(doc.is_single_column, bool)
        assert isinstance(doc.has_multiple_columns, bool)
