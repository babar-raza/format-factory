"""
Sprint 100 — NDJSON analytics round 4.
25 tests for 5 new analytics functions:
  ndjson_bool_value_count, ndjson_null_value_count, ndjson_max_string_length,
  ndjson_numeric_field_ratio, ndjson_unique_key_count
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson import (
    ndjson_bool_value_count,
    ndjson_null_value_count,
    ndjson_max_string_length,
    ndjson_numeric_field_ratio,
    ndjson_unique_key_count,
)

_SIMPLE = b'{"a": 1, "b": 2}\n{"a": 3, "b": 4}\n'
_MIXED = b'{"x": "hello", "y": 10}\n{"x": "world", "y": 20}\n'
_BOOL = b'{"flag": true, "done": false}\n{"flag": false, "done": true}\n'
_NULL = b'{"k": null, "v": 1}\n{"k": null, "v": 2}\n'
_EMPTY = b''


# --- ndjson_bool_value_count ---

class TestNdjsonBoolValueCount:
    def test_returns_int(self):
        result = ndjson_bool_value_count(_SIMPLE)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = ndjson_bool_value_count(_SIMPLE)
        assert result >= 0

    def test_bool_source(self):
        result = ndjson_bool_value_count(_BOOL)
        assert result == 4

    def test_empty_source(self):
        result = ndjson_bool_value_count(_EMPTY)
        assert result == 0

    def test_mixed_source_no_bools(self):
        result = ndjson_bool_value_count(_MIXED)
        assert result == 0


# --- ndjson_null_value_count ---

class TestNdjsonNullValueCount:
    def test_returns_int(self):
        result = ndjson_null_value_count(_SIMPLE)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = ndjson_null_value_count(_SIMPLE)
        assert result >= 0

    def test_null_source(self):
        result = ndjson_null_value_count(_NULL)
        assert result == 2

    def test_empty_source(self):
        result = ndjson_null_value_count(_EMPTY)
        assert result == 0

    def test_simple_no_nulls(self):
        result = ndjson_null_value_count(_SIMPLE)
        assert result == 0


# --- ndjson_max_string_length ---

class TestNdjsonMaxStringLength:
    def test_returns_int(self):
        result = ndjson_max_string_length(_MIXED)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = ndjson_max_string_length(_MIXED)
        assert result >= 0

    def test_mixed_source_positive(self):
        result = ndjson_max_string_length(_MIXED)
        assert result == 5  # "hello" or "world"

    def test_simple_no_strings(self):
        result = ndjson_max_string_length(_SIMPLE)
        assert result == 0

    def test_empty_source(self):
        result = ndjson_max_string_length(_EMPTY)
        assert result == 0


# --- ndjson_numeric_field_ratio ---

class TestNdjsonNumericFieldRatio:
    def test_returns_float(self):
        result = ndjson_numeric_field_ratio(_SIMPLE)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = ndjson_numeric_field_ratio(_SIMPLE)
        assert 0.0 <= result <= 1.0

    def test_all_numeric(self):
        result = ndjson_numeric_field_ratio(_SIMPLE)
        assert result == 1.0

    def test_mixed_source_half_numeric(self):
        result = ndjson_numeric_field_ratio(_MIXED)
        assert result == 0.5

    def test_empty_source(self):
        result = ndjson_numeric_field_ratio(_EMPTY)
        assert result == 0.0


# --- ndjson_unique_key_count ---

class TestNdjsonUniqueKeyCount:
    def test_returns_int(self):
        result = ndjson_unique_key_count(_SIMPLE)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = ndjson_unique_key_count(_SIMPLE)
        assert result >= 0

    def test_simple_two_keys(self):
        result = ndjson_unique_key_count(_SIMPLE)
        assert result == 2

    def test_mixed_source_two_keys(self):
        result = ndjson_unique_key_count(_MIXED)
        assert result == 2

    def test_empty_source(self):
        result = ndjson_unique_key_count(_EMPTY)
        assert result == 0
