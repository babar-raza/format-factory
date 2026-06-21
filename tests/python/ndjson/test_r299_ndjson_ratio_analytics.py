"""Tests for ndjson_numeric_ratio and ndjson_bool_ratio (Sprint r299)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import ndjson_numeric_ratio, ndjson_bool_ratio

_MIXED = b'{"a": 1, "b": "hello"}\n{"a": 2, "b": "world"}\n'
_ALL_BOOL = b'{"x": true, "y": false}\n'
_ALL_NUMERIC = b'{"n": 1}\n{"n": 2}\n{"n": 3}\n'


class TestNdjsonNumericRatio:
    """Tests for ndjson_numeric_ratio."""

    def test_mixed_returns_half(self):
        """2 numeric out of 4 total values → 0.5."""
        result = ndjson_numeric_ratio(_MIXED)
        assert abs(result - 0.5) < 1e-9

    def test_all_bool_returns_zero(self):
        """Bools are not counted as numeric → 0.0."""
        result = ndjson_numeric_ratio(_ALL_BOOL)
        assert result == 0.0

    def test_all_numeric_returns_one(self):
        """3 numeric out of 3 → 1.0."""
        result = ndjson_numeric_ratio(_ALL_NUMERIC)
        assert abs(result - 1.0) < 1e-9

    def test_returns_float(self):
        result = ndjson_numeric_ratio(_MIXED)
        assert isinstance(result, float)

    def test_nonnegative(self):
        for src in [_MIXED, _ALL_BOOL, _ALL_NUMERIC]:
            assert ndjson_numeric_ratio(src) >= 0.0

    def test_all_numeric_more_than_mixed(self):
        r1 = ndjson_numeric_ratio(_MIXED)
        r2 = ndjson_numeric_ratio(_ALL_NUMERIC)
        assert r2 > r1


class TestNdjsonBoolRatio:
    """Tests for ndjson_bool_ratio."""

    def test_mixed_returns_zero(self):
        """No bools in mixed data → 0.0."""
        result = ndjson_bool_ratio(_MIXED)
        assert result == 0.0

    def test_all_bool_returns_one(self):
        """2 bools out of 2 total → 1.0."""
        result = ndjson_bool_ratio(_ALL_BOOL)
        assert abs(result - 1.0) < 1e-9

    def test_all_numeric_returns_zero(self):
        """No bools in all-numeric data → 0.0."""
        result = ndjson_bool_ratio(_ALL_NUMERIC)
        assert result == 0.0

    def test_returns_float(self):
        result = ndjson_bool_ratio(_ALL_BOOL)
        assert isinstance(result, float)

    def test_nonnegative(self):
        for src in [_MIXED, _ALL_BOOL, _ALL_NUMERIC]:
            assert ndjson_bool_ratio(src) >= 0.0

    def test_all_bool_more_than_mixed(self):
        r1 = ndjson_bool_ratio(_MIXED)
        r2 = ndjson_bool_ratio(_ALL_BOOL)
        assert r2 > r1
