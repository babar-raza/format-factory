"""
Tests for toml_is_empty and toml_string_density.
Closes: GAP-TOML-FOSS-TOML_IS_EMPT-001, GAP-TOML-FOSS-TOML_STRING_-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml import toml_is_empty, toml_string_density

_EMPTY = b""
_WITH_STRINGS = b"name = \"test\"\nhost = \"localhost\"\ncount = 42\n"
_ALL_NUMERIC = b"x = 1\ny = 2\nz = 3\n"
_WITH_CONTENT = b"[section]\nkey = \"value\"\n"


class TestTomlIsEmpty:
    def test_returns_bool(self):
        assert isinstance(toml_is_empty(_EMPTY), bool)

    def test_true_for_empty(self):
        assert toml_is_empty(_EMPTY) is True

    def test_false_for_content(self):
        assert toml_is_empty(_WITH_CONTENT) is False

    def test_false_for_strings_only(self):
        assert toml_is_empty(_WITH_STRINGS) is False

    def test_false_for_numeric_keys(self):
        assert toml_is_empty(_ALL_NUMERIC) is False


class TestTomlStringDensity:
    def test_returns_float(self):
        assert isinstance(toml_string_density(_WITH_STRINGS), float)

    def test_zero_for_all_numeric(self):
        assert toml_string_density(_ALL_NUMERIC) == 0.0

    def test_nonzero_for_strings(self):
        # name and host are strings (2/3 keys)
        density = toml_string_density(_WITH_STRINGS)
        assert density > 0.0

    def test_zero_for_empty(self):
        assert toml_string_density(_EMPTY) == 0.0

    def test_between_zero_and_one(self):
        density = toml_string_density(_WITH_STRINGS)
        assert 0.0 <= density <= 1.0
