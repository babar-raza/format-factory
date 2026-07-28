"""R561: CSV dimension properties — is_empty, is_single_row, is_wide, is_tall.

Tests for CsvDocument dimension properties added in R561.
Spec refs: SAL-CSV-00001.
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.models import CsvDocument

SAMPLES = Path("samples/by-format/csv")


def _make_doc(rows=None, headers=None, has_header=False):
    """Build a minimal CsvDocument from a dict."""
    if rows is None:
        rows = []
    return CsvDocument({
        "rows": rows,
        "headers": headers or [],
        "row_count": len(rows),
        "has_header": has_header,
        "delimiter": ",",
    })


class TestIsEmpty:
    def test_no_rows_is_empty(self):
        doc = _make_doc(rows=[])
        assert doc.is_empty is True

    def test_one_row_not_empty(self):
        doc = _make_doc(rows=[["a", "b"]])
        assert doc.is_empty is False

    def test_many_rows_not_empty(self):
        doc = _make_doc(rows=[["a"], ["b"], ["c"]])
        assert doc.is_empty is False

    def test_is_empty_type(self):
        doc = _make_doc(rows=[])
        assert isinstance(doc.is_empty, bool)


class TestIsSingleRow:
    def test_one_row_is_single(self):
        doc = _make_doc(rows=[["a", "b"]])
        assert doc.is_single_row is True

    def test_zero_rows_not_single(self):
        doc = _make_doc(rows=[])
        assert doc.is_single_row is False

    def test_two_rows_not_single(self):
        doc = _make_doc(rows=[["a"], ["b"]])
        assert doc.is_single_row is False

    def test_is_single_row_type(self):
        doc = _make_doc(rows=[["x"]])
        assert isinstance(doc.is_single_row, bool)


class TestIsWideIsTall:
    def test_wide_more_cols_than_rows(self):
        doc = _make_doc(rows=[["a", "b", "c", "d", "e"]])  # 1 row, 5 cols
        assert doc.is_wide is True
        assert doc.is_tall is False

    def test_tall_more_rows_than_cols(self):
        rows = [["a"] for _ in range(5)]  # 5 rows, 1 col
        doc = _make_doc(rows=rows, headers=["X"])
        assert doc.is_tall is True
        assert doc.is_wide is False

    def test_square_not_wide_not_tall(self):
        doc = _make_doc(rows=[["a", "b"], ["c", "d"]])  # 2x2
        assert doc.is_wide is False
        assert doc.is_tall is False

    def test_is_wide_type(self):
        doc = _make_doc(rows=[["a"]])
        assert isinstance(doc.is_wide, bool)

    def test_is_tall_type(self):
        doc = _make_doc(rows=[["a"]])
        assert isinstance(doc.is_tall, bool)


class TestDimensionConsistency:
    def test_empty_not_single(self):
        doc = _make_doc(rows=[])
        assert doc.is_empty
        assert not doc.is_single_row

    def test_single_not_empty(self):
        doc = _make_doc(rows=[["x"]])
        assert doc.is_single_row
        assert not doc.is_empty

    def test_from_file_single_cell(self):
        doc = CsvDocument.from_file(SAMPLES / "single-cell.csv")
        assert isinstance(doc.is_empty, bool)
        assert isinstance(doc.is_single_row, bool)

    def test_from_file_minimal_2x2(self):
        doc = CsvDocument.from_file(SAMPLES / "minimal-2x2.csv")
        assert isinstance(doc.is_wide, bool)
        assert isinstance(doc.is_tall, bool)
