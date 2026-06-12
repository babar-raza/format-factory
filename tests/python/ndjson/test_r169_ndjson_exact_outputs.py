"""R169 — NDJSON exact-output tests for count_unique_values and zip_with_index."""
from __future__ import annotations

from src.python.ndjson.ndjson_codec import count_unique_values, zip_with_index


class TestCountUniqueValuesExact:
    def test_three_distinct(self):
        records = [{"color": "red"}, {"color": "green"}, {"color": "blue"}]
        assert count_unique_values(records, "color") == 3

    def test_two_unique_out_of_four(self):
        records = [{"x": "a"}, {"x": "b"}, {"x": "a"}, {"x": "b"}]
        assert count_unique_values(records, "x") == 2

    def test_single_record_one_unique(self):
        assert count_unique_values([{"k": "v"}], "k") == 1


class TestZipWithIndexExact:
    def test_first_index_is_zero(self):
        result = zip_with_index([{"a": 1}, {"a": 2}])
        assert result[0]["_index"] == 0

    def test_second_index_is_one(self):
        result = zip_with_index([{"a": 1}, {"a": 2}])
        assert result[1]["_index"] == 1

    def test_original_value_preserved(self):
        result = zip_with_index([{"city": "Paris", "pop": 2161000}])
        assert result[0]["city"] == "Paris"
        assert result[0]["pop"] == 2161000

    def test_custom_field_exact_value(self):
        result = zip_with_index([{"x": 1}, {"x": 2}], field_name="seq")
        assert result[0]["seq"] == 0
        assert result[1]["seq"] == 1
