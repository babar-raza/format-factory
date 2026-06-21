"""Tests for r329 rework: TOML analytics functions.

Functions:
  toml_bool_count_minus_string_count  — bool count minus string count
  toml_string_count_equals_numeric_count — True if string count == numeric count
"""
import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import (
    toml_bool_count_minus_string_count,
    toml_string_count_equals_numeric_count,
)

_MINIMAL = str(_REPO / "samples" / "by-format" / "toml" / "minimal.toml")

_TWO_BOOLS = b"x = true\ny = false\nz = 1\n"
_ONE_STR_ONE_NUM = b'a = "foo"\nb = 1\n'
_ALL_NUMERIC = b"n1 = 10\nn2 = 20\n"


class TestTomlBoolCountMinusStringCount:
    def test_return_type(self):
        assert isinstance(toml_bool_count_minus_string_count(_MINIMAL), int)

    def test_zero_for_minimal(self):
        # minimal.toml: 1 bool, many strings → result <= 0
        result = toml_bool_count_minus_string_count(_MINIMAL)
        assert result == 0 or result < 0

    def test_exact_for_two_bools(self):
        # "x = true\ny = false\nz = 1\n" → 2 bools, 0 strings → 2
        assert toml_bool_count_minus_string_count(_TWO_BOOLS) == 2

    def test_zero_for_one_each(self):
        # 'a = "foo"\nb = 1\n' → 0 bools, 1 string → clamped to 0
        assert toml_bool_count_minus_string_count(_ONE_STR_ONE_NUM) == 0

    def test_consistent(self):
        assert toml_bool_count_minus_string_count(_MINIMAL) == toml_bool_count_minus_string_count(_MINIMAL)


class TestTomlStringCountEqualsNumericCount:
    def test_return_type(self):
        assert isinstance(toml_string_count_equals_numeric_count(_MINIMAL), bool)

    def test_false_for_minimal(self):
        # minimal.toml has many strings, 2 numerics → not equal
        assert toml_string_count_equals_numeric_count(_MINIMAL) is False

    def test_true_for_one_each(self):
        # 'a = "foo"\nb = 1\n' → 1 string, 1 numeric → True
        assert toml_string_count_equals_numeric_count(_ONE_STR_ONE_NUM) is True

    def test_false_for_all_numeric(self):
        # "n1 = 10\nn2 = 20\n" → 0 strings, 2 numerics → False
        assert toml_string_count_equals_numeric_count(_ALL_NUMERIC) is False

    def test_consistent(self):
        assert toml_string_count_equals_numeric_count(_MINIMAL) == toml_string_count_equals_numeric_count(_MINIMAL)
