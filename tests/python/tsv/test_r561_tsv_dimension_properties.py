"""R561: TSV dimension properties — is_empty, is_single_row, is_wide, is_tall.

Tests for TsvDocument dimension properties added in R561.
Spec refs: SAL-TSV-00001.
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.models import TsvDocument

SAMPLES = Path("samples/by-format/tsv")


def _make_doc(rows=None, headers=None, has_header=False):
    """Build a minimal TsvDocument from a dict."""
    if rows is None:
        rows = []
    return TsvDocument({
        "rows": rows,
        "headers": headers or [],
        "row_count": len(rows),
        "has_header": has_header,
    })


class TestIsEmpty:
    def test_no_rows_is_empty(self):
        doc = _make_doc(rows=[])
        assert doc.is_empty is True

    def test_one_row_not_empty(self):
        doc = _make_doc(rows=[["a", "b"]])
        assert doc.is_empty is False

    def test_multiple_rows_not_empty(self):
        doc = _make_doc(rows=[["a"], ["b"]])
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
        doc = _make_doc(rows=[["a", "b", "c"]])  # 1 row, 3 cols
        assert doc.is_wide is True
        assert doc.is_tall is False

    def test_tall_more_rows_than_cols(self):
        rows = [["a"] for _ in range(4)]  # 4 rows, 1 col
        doc = _make_doc(rows=rows, headers=["X"])
        assert doc.is_tall is True
        assert doc.is_wide is False

    def test_square_not_wide_not_tall(self):
        doc = _make_doc(rows=[["a", "b"], ["c", "d"]])  # 2x2
        assert not doc.is_wide
        assert not doc.is_tall

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

    def test_single_implies_not_empty(self):
        doc = _make_doc(rows=[["x"]])
        assert doc.is_single_row
        assert not doc.is_empty

    def test_from_file_single_cell(self):
        doc = TsvDocument.from_file(SAMPLES / "single-cell.tsv")
        assert isinstance(doc.is_empty, bool)
        assert isinstance(doc.is_single_row, bool)

    def test_from_file_minimal_2x2(self):
        doc = TsvDocument.from_file(SAMPLES / "minimal-2x2.tsv")
        assert isinstance(doc.is_wide, bool)
        assert isinstance(doc.is_tall, bool)
