"""
Tests for TOML ratio and sum analytics (2 new FOSS functions).
Closes: GAP-TOML-FOSS-TOML_BOOL_R-001, GAP-TOML-FOSS-TOML_NUMER-001

Known sample values (inline bytes):
  empty: bool_ratio=0.0, numeric_sum=0.0
  flag=true: bool_ratio=1.0, numeric_sum=0.0
  a=1,b=2,c=true: bool_ratio=1/3, numeric_sum=3.0
  a=1,b=10,c=-5: bool_ratio=0.0, numeric_sum=6.0
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pytest
from toml.toml_codec import toml_bool_ratio, toml_numeric_sum

_EMPTY = b""
_BOOL_ONLY = b"flag = true\n"
_MIXED = b"a = 1\nb = 2\nc = true\n"
_NUMERIC = b"a = 1\nb = 10\nc = -5\n"
_TEXT_ONLY = b'name = "Alice"\n'
_FLOAT = b"x = 5.0\ny = 7.5\n"


class TestTomlBoolRatio:
    def test_returns_float(self):
        assert isinstance(toml_bool_ratio(_EMPTY), float)

    def test_empty_is_zero(self):
        assert toml_bool_ratio(_EMPTY) == 0.0

    def test_all_bool_is_one(self):
        assert toml_bool_ratio(_BOOL_ONLY) == 1.0

    def test_no_bools_is_zero(self):
        assert toml_bool_ratio(_NUMERIC) == 0.0

    def test_text_only_is_zero(self):
        assert toml_bool_ratio(_TEXT_ONLY) == 0.0

    def test_mixed_ratio(self):
        # a=1, b=2, c=true → 1 bool out of 3 = 1/3
        result = toml_bool_ratio(_MIXED)
        assert result == pytest.approx(1 / 3, rel=1e-6)

    def test_bounded_zero_to_one(self):
        for src in [_EMPTY, _BOOL_ONLY, _MIXED, _NUMERIC, _TEXT_ONLY]:
            r = toml_bool_ratio(src)
            assert 0.0 <= r <= 1.0

    def test_all_return_float(self):
        for src in [_EMPTY, _BOOL_ONLY, _MIXED, _NUMERIC]:
            assert isinstance(toml_bool_ratio(src), float)


class TestTomlNumericSum:
    def test_returns_float(self):
        assert isinstance(toml_numeric_sum(_EMPTY), float)

    def test_empty_is_zero(self):
        assert toml_numeric_sum(_EMPTY) == 0.0

    def test_bool_only_is_zero(self):
        # booleans excluded
        assert toml_numeric_sum(_BOOL_ONLY) == 0.0

    def test_text_only_is_zero(self):
        assert toml_numeric_sum(_TEXT_ONLY) == 0.0

    def test_integer_sum(self):
        # a=1, b=10, c=-5 → 1+10-5=6
        assert toml_numeric_sum(_NUMERIC) == 6.0

    def test_float_sum(self):
        # x=5.0, y=7.5 → 12.5
        assert toml_numeric_sum(_FLOAT) == pytest.approx(12.5, rel=1e-6)

    def test_mixed_sum_excludes_bool(self):
        # a=1, b=2, c=true → 1+2=3 (bool excluded)
        assert toml_numeric_sum(_MIXED) == 3.0

    def test_all_return_float(self):
        for src in [_EMPTY, _BOOL_ONLY, _NUMERIC, _FLOAT]:
            assert isinstance(toml_numeric_sum(src), float)
