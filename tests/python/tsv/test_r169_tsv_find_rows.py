"""Tests for TSV find_rows_containing function (rnext36)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from src.python.tsv.tsv_parser import find_rows_containing


def _model(headers, rows):
    return {"headers": headers, "rows": rows, "row_count": len(rows)}


class TestFindRowsContaining:
    def test_basic_found(self):
        model = _model(["name", "city"], [["Alice", "New York"], ["Bob", "Paris"]])
        assert find_rows_containing(model, "Alice") == [0]

    def test_multiple_matches(self):
        model = _model(["a", "b"], [["foo", "bar"], ["baz", "foo"], ["xyz", "abc"]])
        assert find_rows_containing(model, "foo") == [0, 1]

    def test_not_found(self):
        model = _model(["a"], [["hello"], ["world"]])
        assert find_rows_containing(model, "xyz") == []

    def test_empty_rows(self):
        model = _model(["a"], [])
        assert find_rows_containing(model, "text") == []

    def test_case_sensitive_no_match(self):
        model = _model(["a"], [["Hello"]])
        assert find_rows_containing(model, "hello", case_sensitive=True) == []

    def test_case_insensitive_match(self):
        model = _model(["a"], [["Hello World"]])
        assert find_rows_containing(model, "hello", case_sensitive=False) == [0]

    def test_substring_match(self):
        model = _model(["a"], [["format-factory"], ["other"]])
        assert find_rows_containing(model, "factory") == [0]

    def test_all_rows_match(self):
        model = _model(["a"], [["test1"], ["test2"], ["test3"]])
        assert find_rows_containing(model, "test") == [0, 1, 2]
