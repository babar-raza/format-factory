"""Tests for ndjson_string_field_count (Sprint 22)."""
import pytest
from src.python.ndjson import ndjson_string_field_count


class TestNdjsonStringFieldCount:
    def test_all_strings(self):
        records = [{"a": "hello", "b": "world"}]
        assert ndjson_string_field_count(records) == 2

    def test_mixed_types(self):
        records = [{"a": "text", "b": 42, "c": True}]
        assert ndjson_string_field_count(records) == 1

    def test_no_strings(self):
        records = [{"a": 1, "b": 2.5}]
        assert ndjson_string_field_count(records) == 0

    def test_empty_records(self):
        assert ndjson_string_field_count([]) == 0

    def test_multiple_records(self):
        records = [{"a": "x"}, {"a": "y", "b": 1}]
        assert ndjson_string_field_count(records) == 2
