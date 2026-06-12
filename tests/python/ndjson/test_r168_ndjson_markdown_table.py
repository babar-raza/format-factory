"""R168 — NDJSON to_markdown_table tests.

Queue: sprint4-q-004
"""
from __future__ import annotations

import pytest

from src.python.ndjson.ndjson_codec import to_markdown_table


class TestToMarkdownTable:
    def test_empty_returns_empty(self):
        assert to_markdown_table([]) == ""

    def test_returns_string(self):
        records = [{"a": 1, "b": 2}]
        result = to_markdown_table(records)
        assert isinstance(result, str)

    def test_has_header_row(self):
        records = [{"name": "Alice", "age": 30}]
        result = to_markdown_table(records)
        assert "name" in result
        assert "age" in result

    def test_has_separator_row(self):
        records = [{"col": "val"}]
        result = to_markdown_table(records)
        assert "---" in result

    def test_has_pipe_delimiters(self):
        records = [{"x": 1}]
        result = to_markdown_table(records)
        assert "|" in result

    def test_multiple_records(self):
        records = [{"name": "A", "v": 1}, {"name": "B", "v": 2}]
        result = to_markdown_table(records)
        lines = result.strip().split("\n")
        assert len(lines) == 4  # header + separator + 2 data rows

    def test_single_record_three_lines(self):
        records = [{"k": "v"}]
        result = to_markdown_table(records)
        lines = result.strip().split("\n")
        assert len(lines) == 3

    def test_values_in_output(self):
        records = [{"city": "Paris", "pop": 2161000}]
        result = to_markdown_table(records)
        assert "Paris" in result
        assert "2161000" in result
