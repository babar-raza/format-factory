"""R168 — TSV get_numeric_columns tests.

Queue: sprint4-q-005
"""
from __future__ import annotations

import pytest

from src.python.tsv.tsv_parser import get_numeric_columns, load_tsv


class TestGetNumericColumns:
    def test_empty_returns_empty(self):
        result = get_numeric_columns({"headers": [], "rows": []})
        assert result == []

    def test_returns_list(self):
        data = load_tsv(b"a\tb\n1\t2\n3\t4\n")
        result = get_numeric_columns(data)
        assert isinstance(result, list)

    def test_numeric_columns_identified(self):
        data = load_tsv(b"x\ty\n1\tabc\n2\tdef\n")
        result = get_numeric_columns(data)
        assert "x" in result
        assert "y" not in result

    def test_mixed_column_not_numeric(self):
        data = load_tsv(b"col\n1\ntwo\n3\n")
        result = get_numeric_columns(data)
        assert "col" not in result

    def test_all_numeric_columns(self):
        data = load_tsv(b"a\tb\n1.5\t2\n3.0\t4\n")
        result = get_numeric_columns(data)
        assert "a" in result
        assert "b" in result

    def test_no_rows_returns_empty(self):
        data = {"headers": ["col1", "col2"], "rows": []}
        result = get_numeric_columns(data)
        assert result == []

    def test_float_values(self):
        data = load_tsv(b"price\n1.99\n2.50\n0.75\n")
        result = get_numeric_columns(data)
        assert "price" in result

    def test_empty_cells_ignored(self):
        data = load_tsv(b"n\n1\n\n3\n")
        result = get_numeric_columns(data)
        assert "n" in result
