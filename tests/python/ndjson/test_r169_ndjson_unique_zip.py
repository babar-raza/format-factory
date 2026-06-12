"""R169 — NDJSON count_unique_values and zip_with_index tests."""
from __future__ import annotations

import pytest

from src.python.ndjson.ndjson_codec import count_unique_values, zip_with_index


class TestCountUniqueValues:
    def test_empty_returns_zero(self):
        assert count_unique_values([], "field") == 0

    def test_single_distinct(self):
        records = [{"a": 1}, {"a": 1}, {"a": 1}]
        assert count_unique_values(records, "a") == 1

    def test_multiple_distinct(self):
        records = [{"x": "a"}, {"x": "b"}, {"x": "c"}]
        assert count_unique_values(records, "x") == 3

    def test_partial_distinct(self):
        records = [{"v": 1}, {"v": 2}, {"v": 1}, {"v": 3}]
        assert count_unique_values(records, "v") == 3

    def test_missing_field_excluded(self):
        records = [{"a": 1}, {"b": 2}, {"a": 1}]
        assert count_unique_values(records, "a") == 1

    def test_returns_int(self):
        records = [{"k": "x"}]
        assert isinstance(count_unique_values(records, "k"), int)

    def test_ndjson_bytes(self):
        data = b'{"c":1}\n{"c":2}\n{"c":1}\n'
        assert count_unique_values(data, "c") == 2

    def test_none_values_counted(self):
        records = [{"x": None}, {"x": None}, {"x": 1}]
        assert count_unique_values(records, "x") == 2


class TestZipWithIndex:
    def test_empty_returns_empty(self):
        assert zip_with_index([]) == []

    def test_adds_index_field(self):
        result = zip_with_index([{"a": 1}])
        assert result[0]["_index"] == 0

    def test_index_increments(self):
        result = zip_with_index([{"x": 1}, {"x": 2}, {"x": 3}])
        indices = [r["_index"] for r in result]
        assert indices == [0, 1, 2]

    def test_preserves_fields(self):
        result = zip_with_index([{"name": "Alice", "age": 30}])
        assert result[0]["name"] == "Alice"
        assert result[0]["age"] == 30

    def test_custom_field_name(self):
        result = zip_with_index([{"a": 1}], field_name="row_num")
        assert result[0]["row_num"] == 0

    def test_returns_list(self):
        assert isinstance(zip_with_index([{"x": 1}]), list)

    def test_ndjson_bytes(self):
        data = b'{"a":1}\n{"a":2}\n'
        result = zip_with_index(data)
        assert len(result) == 2
        assert result[1]["_index"] == 1

    def test_length_preserved(self):
        records = [{"k": i} for i in range(5)]
        result = zip_with_index(records)
        assert len(result) == 5
