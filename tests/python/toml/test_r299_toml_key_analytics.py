"""Tests for toml_string_key_ratio and toml_min_key_length (Sprint r299)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import toml_string_key_ratio, toml_min_key_length

_MIXED = b'name = "hello"\ncount = 42\n'
_ALL_NUMERIC = b'a = 1\nb = 2\nc = 3\n'
_ONE_STRING = b'x = "hi"\ny = true\nz = 3.14\n'


class TestTomlStringKeyRatio:
    """Tests for toml_string_key_ratio."""

    def test_mixed_returns_half(self):
        """Mixed: 1 string out of 2 keys → 0.5."""
        result = toml_string_key_ratio(_MIXED)
        assert abs(result - 0.5) < 1e-9

    def test_all_numeric_returns_zero(self):
        """All numeric values → 0.0."""
        result = toml_string_key_ratio(_ALL_NUMERIC)
        assert result == 0.0

    def test_one_string_of_three_returns_third(self):
        """1 string out of 3 keys → ~0.333."""
        result = toml_string_key_ratio(_ONE_STRING)
        assert abs(result - 1 / 3) < 1e-9

    def test_returns_float(self):
        result = toml_string_key_ratio(_MIXED)
        assert isinstance(result, float)

    def test_nonnegative(self):
        for src in [_MIXED, _ALL_NUMERIC, _ONE_STRING]:
            assert toml_string_key_ratio(src) >= 0.0

    def test_mixed_more_than_all_numeric(self):
        r1 = toml_string_key_ratio(_ALL_NUMERIC)
        r2 = toml_string_key_ratio(_MIXED)
        assert r2 > r1


class TestTomlMinKeyLength:
    """Tests for toml_min_key_length."""

    def test_mixed_min_key_is_5(self):
        """'name' (4) vs 'count' (5) → min = 4."""
        result = toml_min_key_length(_MIXED)
        assert result == 4

    def test_all_numeric_min_key_is_1(self):
        """Keys 'a', 'b', 'c' → min = 1."""
        result = toml_min_key_length(_ALL_NUMERIC)
        assert result == 1

    def test_one_string_min_key_is_1(self):
        """Keys 'x', 'y', 'z' → min = 1."""
        result = toml_min_key_length(_ONE_STRING)
        assert result == 1

    def test_returns_int(self):
        result = toml_min_key_length(_MIXED)
        assert isinstance(result, int)

    def test_nonnegative(self):
        for src in [_MIXED, _ALL_NUMERIC, _ONE_STRING]:
            assert toml_min_key_length(src) >= 0

    def test_mixed_min_larger_than_single_char(self):
        r1 = toml_min_key_length(_ALL_NUMERIC)
        r2 = toml_min_key_length(_MIXED)
        assert r2 > r1
