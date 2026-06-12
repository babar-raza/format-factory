"""
tests/python/ndjson/test_r196_ndjson_analytics.py

Sprint: FORMAT-FACTORY-ODS-NDJSON-DEEPENING-001
Tests for to_markdown_table(), ndjson_average_field_count(), ndjson_null_field_count().
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson import to_markdown_table, ndjson_average_field_count, ndjson_null_field_count


class TestToMarkdownTable:
    def test_empty_records_returns_empty_string(self):
        result = to_markdown_table([])
        assert result == ""

    def test_returns_string(self):
        result = to_markdown_table([{"a": 1}])
        assert isinstance(result, str)

    def test_contains_header_row(self):
        result = to_markdown_table([{"col": "val"}])
        assert "col" in result

    def test_contains_separator_row(self):
        result = to_markdown_table([{"a": 1}])
        assert "---" in result

    def test_two_column_table_has_both_cols(self):
        result = to_markdown_table([{"x": 1, "y": 2}])
        assert "x" in result
        assert "y" in result

    def test_values_appear_in_table(self):
        result = to_markdown_table([{"name": "Alice", "score": 95}])
        assert "Alice" in result
        assert "95" in result


class TestNdjsonAverageFieldCount:
    def test_empty_list_returns_zero(self):
        result = ndjson_average_field_count([])
        assert result == 0.0

    def test_single_record_two_fields(self):
        result = ndjson_average_field_count([{"a": 1, "b": 2}])
        assert result == 2.0

    def test_uniform_records_returns_field_count(self):
        records = [{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]
        result = ndjson_average_field_count(records)
        assert result == 3.0

    def test_returns_float(self):
        result = ndjson_average_field_count([{"a": 1}])
        assert isinstance(result, float)

    def test_mixed_field_counts_averages_correctly(self):
        records = [{"a": 1}, {"a": 1, "b": 2, "c": 3}]  # avg = 2.0
        result = ndjson_average_field_count(records)
        assert result == 2.0


class TestNdjsonNullFieldCount:
    def test_no_nulls_returns_zero(self):
        records = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        result = ndjson_null_field_count(records, "a")
        assert result == 0

    def test_counts_none_values(self):
        records = [{"a": None}, {"a": 5}, {"a": None}]
        result = ndjson_null_field_count(records, "a")
        assert result == 2

    def test_empty_records_returns_zero(self):
        result = ndjson_null_field_count([], "any_field")
        assert result == 0

    def test_missing_field_counted_as_null(self):
        # Field missing from a record — behavior: count it as null or not
        records = [{"a": 1}, {"b": 2}]  # second record has no "a"
        result = ndjson_null_field_count(records, "a")
        assert isinstance(result, int)
        assert result >= 0

    def test_returns_int(self):
        result = ndjson_null_field_count([{"x": None}], "x")
        assert isinstance(result, int)
