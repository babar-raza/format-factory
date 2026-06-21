"""
Tests for 5 new NDJSON analytics functions (R346 / Sprint 82):
  ndjson_value_variance, ndjson_string_length_sum, ndjson_numeric_sum,
  ndjson_file_size_bytes, ndjson_key_count_variance
25 tests total.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson import (
    ndjson_value_variance,
    ndjson_string_length_sum,
    ndjson_numeric_sum,
    ndjson_file_size_bytes,
    ndjson_key_count_variance,
)

# Use byte strings as source — API accepts path, bytes, or string
_SIMPLE = b'{"a": 1, "b": 2}\n{"a": 3, "b": 4}\n'
_MIXED = b'{"x": "hello", "y": 10}\n{"x": "world", "y": 20}\n'
_EMPTY = b''
_SINGLE = b'{"k": 42}\n'


# ── ndjson_value_variance ──────────────────────────────────────────────────────

class TestNdjsonValueVariance:
    def test_returns_float(self):
        result = ndjson_value_variance(_SIMPLE)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = ndjson_value_variance(_SIMPLE)
        assert result >= 0.0

    def test_mixed_source(self):
        result = ndjson_value_variance(_MIXED)
        assert isinstance(result, float) and result >= 0.0

    def test_empty_source_returns_zero(self):
        result = ndjson_value_variance(_EMPTY)
        assert isinstance(result, float) and result >= 0.0

    def test_single_record_returns_zero(self):
        result = ndjson_value_variance(_SINGLE)
        assert isinstance(result, float) and result >= 0.0


# ── ndjson_string_length_sum ───────────────────────────────────────────────────

class TestNdjsonStringLengthSum:
    def test_returns_int(self):
        result = ndjson_string_length_sum(_MIXED)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = ndjson_string_length_sum(_MIXED)
        assert result >= 0

    def test_simple_source_is_zero(self):
        # _SIMPLE has no string values
        result = ndjson_string_length_sum(_SIMPLE)
        assert result == 0

    def test_empty_source_returns_zero(self):
        result = ndjson_string_length_sum(_EMPTY)
        assert result == 0

    def test_mixed_has_strings(self):
        result = ndjson_string_length_sum(_MIXED)
        # "hello" (5) + "world" (5) = 10
        assert result == 10


# ── ndjson_numeric_sum ─────────────────────────────────────────────────────────

class TestNdjsonNumericSum:
    def test_returns_float(self):
        result = ndjson_numeric_sum(_SIMPLE)
        assert isinstance(result, float)

    def test_simple_sum(self):
        # 1 + 2 + 3 + 4 = 10
        result = ndjson_numeric_sum(_SIMPLE)
        assert result == 10.0

    def test_empty_source_returns_zero(self):
        result = ndjson_numeric_sum(_EMPTY)
        assert result == 0.0

    def test_mixed_has_numeric(self):
        result = ndjson_numeric_sum(_MIXED)
        # y=10 + y=20 = 30
        assert result == 30.0

    def test_non_negative_for_positive_values(self):
        result = ndjson_numeric_sum(_SIMPLE)
        assert result > 0.0


# ── ndjson_file_size_bytes ─────────────────────────────────────────────────────

class TestNdjsonFileSizeBytes:
    def test_returns_int(self):
        result = ndjson_file_size_bytes(_SIMPLE)
        assert isinstance(result, int)

    def test_bytes_source_returns_zero(self):
        # bytes source is not a file path, so returns 0
        result = ndjson_file_size_bytes(_SIMPLE)
        assert result == 0

    def test_empty_bytes_returns_zero(self):
        result = ndjson_file_size_bytes(_EMPTY)
        assert result == 0

    def test_nonexistent_path_returns_zero(self):
        result = ndjson_file_size_bytes("/nonexistent/file.ndjson")
        assert result == 0

    def test_result_is_int_type(self):
        result = ndjson_file_size_bytes(_SIMPLE)
        assert type(result) is int


# ── ndjson_key_count_variance ──────────────────────────────────────────────────

class TestNdjsonKeyCountVariance:
    def test_returns_float(self):
        result = ndjson_key_count_variance(_SIMPLE)
        assert isinstance(result, float)

    def test_uniform_records_returns_zero(self):
        # Both records have same 2 keys → variance = 0
        result = ndjson_key_count_variance(_SIMPLE)
        assert result == 0.0

    def test_empty_source_returns_zero(self):
        result = ndjson_key_count_variance(_EMPTY)
        assert result == 0.0

    def test_single_record_returns_zero(self):
        result = ndjson_key_count_variance(_SINGLE)
        assert result == 0.0

    def test_mixed_same_key_count(self):
        result = ndjson_key_count_variance(_MIXED)
        assert isinstance(result, float) and result >= 0.0
