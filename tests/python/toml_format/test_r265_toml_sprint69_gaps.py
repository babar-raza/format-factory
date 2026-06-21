"""Tests for TOML Sprint 69 gap closure.

Closes:
  GAP-TOML-FOSS-TOML_BOOL_CO-001   (Toml Bool Count)
  GAP-TOML-FOSS-TOML_HAS_BOO-001   (Toml Has Boolean Value)
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.toml import toml_bool_count, toml_has_boolean_value

_DIR = _REPO / "samples" / "by-format" / "toml"
_MINIMAL = str(_DIR / "minimal.toml")


class TestTomlBoolCount:
    def test_return_type(self):
        assert isinstance(toml_bool_count(_MINIMAL), int)

    def test_exact_1_for_minimal(self):
        assert toml_bool_count(_MINIMAL) == 1

    def test_nonnegative(self):
        assert toml_bool_count(_MINIMAL) >= 0

    def test_zero_for_no_booleans(self, tmp_path):
        f = tmp_path / "nobool.toml"
        f.write_text('key = "value"\ncount = 42\n')
        assert toml_bool_count(str(f)) == 0

    def test_exact_2_for_two_booleans(self, tmp_path):
        f = tmp_path / "twobool.toml"
        f.write_text("a = true\nb = false\n")
        assert toml_bool_count(str(f)) == 2

    def test_consistent_across_calls(self):
        assert toml_bool_count(_MINIMAL) == toml_bool_count(_MINIMAL)


class TestTomlHasBooleanValue:
    def test_return_type(self):
        assert isinstance(toml_has_boolean_value(_MINIMAL), bool)

    def test_true_for_minimal(self):
        assert toml_has_boolean_value(_MINIMAL) is True

    def test_false_for_no_booleans(self, tmp_path):
        f = tmp_path / "nobool.toml"
        f.write_text('key = "value"\ncount = 42\n')
        assert toml_has_boolean_value(str(f)) is False

    def test_true_for_explicit_bool(self, tmp_path):
        f = tmp_path / "withbool.toml"
        f.write_text("enabled = true\n")
        assert toml_has_boolean_value(str(f)) is True

    def test_is_boolean(self):
        result = toml_has_boolean_value(_MINIMAL)
        assert result in (True, False)

    def test_consistent_across_calls(self):
        assert toml_has_boolean_value(_MINIMAL) == toml_has_boolean_value(_MINIMAL)
