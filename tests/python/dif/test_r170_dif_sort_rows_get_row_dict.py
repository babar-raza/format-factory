"""R170 — DIF sort_rows_by_column and get_row_as_dict tests.

Sprint: FORMAT-FACTORY-PROOF-CLOSED-SELF-HEALING-PROFESSIONALIZE-PRODUCT-READINESS-RNEXT-001
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.python.dif.dif_parser import (
    sort_rows_by_column,
    get_row_as_dict,
    DifDocument,
    DifCell,
    write_dif,
)


def _make_dif_file(rows_data: list[list]) -> Path:
    """Write a DIF file with given rows and return path."""
    cells = [
        [DifCell(value=v, value_type="numeric" if isinstance(v, (int, float)) else "string") for v in row]
        for row in rows_data
    ]
    n_cols = len(rows_data[0]) if rows_data else 0
    doc = DifDocument(
        title="test",
        vectors=n_cols,
        tuples=len(rows_data),
        rows=cells,
    )
    tmp = tempfile.NamedTemporaryFile(suffix=".dif", delete=False)
    write_dif(doc, tmp.name)
    tmp.close()
    return Path(tmp.name)


class TestSortRowsByColumn:
    def test_sort_ascending_by_col0(self):
        path = _make_dif_file([[3, "c"], [1, "a"], [2, "b"]])
        try:
            result = sort_rows_by_column(path, col=0, reverse=False)
            col0_vals = [row[0].value for row in result.rows]
            assert col0_vals == [1, 2, 3]
        finally:
            path.unlink(missing_ok=True)

    def test_sort_descending_by_col0(self):
        path = _make_dif_file([[1, "a"], [3, "c"], [2, "b"]])
        try:
            result = sort_rows_by_column(path, col=0, reverse=True)
            col0_vals = [row[0].value for row in result.rows]
            assert col0_vals == [3, 2, 1]
        finally:
            path.unlink(missing_ok=True)

    def test_sort_by_string_col(self):
        path = _make_dif_file([[1, "banana"], [2, "apple"], [3, "cherry"]])
        try:
            result = sort_rows_by_column(path, col=1, reverse=False)
            col1_vals = [row[1].value for row in result.rows]
            assert col1_vals == ["apple", "banana", "cherry"]
        finally:
            path.unlink(missing_ok=True)

    def test_sort_returns_dif_document(self):
        path = _make_dif_file([[2, "b"], [1, "a"]])
        try:
            result = sort_rows_by_column(path, col=0)
            assert isinstance(result, DifDocument)
        finally:
            path.unlink(missing_ok=True)

    def test_sort_preserves_row_count(self):
        path = _make_dif_file([[3, "c"], [1, "a"], [2, "b"]])
        try:
            result = sort_rows_by_column(path, col=0)
            assert len(result.rows) == 3
        finally:
            path.unlink(missing_ok=True)

    def test_sort_out_of_range_col_places_at_end(self):
        """Rows with col out-of-range are placed at end — no error raised."""
        path = _make_dif_file([[1, "a"], [2, "b"]])
        try:
            result = sort_rows_by_column(path, col=99)
            assert len(result.rows) == 2
        finally:
            path.unlink(missing_ok=True)

    def test_function_in_all(self):
        from src.python.dif import __all__ as dif_all
        assert "sort_rows_by_column" in dif_all


class TestGetRowAsDict:
    def test_basic_row_dict(self):
        doc = DifDocument(
            title="test", vectors=2, tuples=2,
            rows=[
                [DifCell(value=1, value_type="numeric"), DifCell(value="hello", value_type="string")],
                [DifCell(value=2, value_type="numeric"), DifCell(value="world", value_type="string")],
            ],
        )
        result = get_row_as_dict(doc, 0)
        assert result == {0: 1, 1: "hello"}

    def test_second_row_dict(self):
        doc = DifDocument(
            title="test", vectors=2, tuples=2,
            rows=[
                [DifCell(value=10, value_type="numeric"), DifCell(value=20, value_type="numeric")],
                [DifCell(value=30, value_type="numeric"), DifCell(value=40, value_type="numeric")],
            ],
        )
        result = get_row_as_dict(doc, 1)
        assert result == {0: 30, 1: 40}

    def test_out_of_range_returns_empty(self):
        doc = DifDocument(
            title="test", vectors=1, tuples=1,
            rows=[[DifCell(value=1, value_type="numeric")]],
        )
        assert get_row_as_dict(doc, 99) == {}
        assert get_row_as_dict(doc, -1) == {}

    def test_empty_document_returns_empty(self):
        doc = DifDocument(title="test", vectors=0, tuples=0, rows=[])
        assert get_row_as_dict(doc, 0) == {}

    def test_keys_are_int_indices(self):
        doc = DifDocument(
            title="test", vectors=3, tuples=1,
            rows=[[
                DifCell(value=1, value_type="numeric"),
                DifCell(value=2, value_type="numeric"),
                DifCell(value=3, value_type="numeric"),
            ]],
        )
        result = get_row_as_dict(doc, 0)
        assert list(result.keys()) == [0, 1, 2]

    def test_function_in_all(self):
        from src.python.dif import __all__ as dif_all
        assert "get_row_as_dict" in dif_all
