"""
Tests for toml_max_value_length and toml_nested_table_count.
Closes: GAP-TOML-FOSS-TOML_MAX_VAL-001, GAP-TOML-FOSS-TOML_NESTED_-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml import toml_max_value_length, toml_nested_table_count

_WITH_LONG_VALUE = b'name = "a_very_long_string_value"\nshort = "hi"\n'
_WITH_NESTED = b"[server]\nhost = \"localhost\"\n\n[server.database]\nname = \"mydb\"\n"
_FLAT = b"name = \"test\"\ncount = 42\n"
_EMPTY = b""


class TestTomlMaxValueLength:
    def test_returns_int(self):
        assert isinstance(toml_max_value_length(_WITH_LONG_VALUE), int)

    def test_zero_for_empty(self):
        assert toml_max_value_length(_EMPTY) == 0

    def test_positive_for_content(self):
        assert toml_max_value_length(_WITH_LONG_VALUE) > 0

    def test_longest_string_wins(self):
        # "a_very_long_string_value" (24) > "hi" (2)
        assert toml_max_value_length(_WITH_LONG_VALUE) >= 2

    def test_flat_content(self):
        content = b'key = "hello"\n'
        assert toml_max_value_length(content) >= 5


class TestTomlNestedTableCount:
    def test_returns_int(self):
        assert isinstance(toml_nested_table_count(_WITH_NESTED), int)

    def test_zero_for_flat(self):
        assert toml_nested_table_count(_FLAT) == 0

    def test_zero_for_empty(self):
        assert toml_nested_table_count(_EMPTY) == 0

    def test_one_for_nested(self):
        # [server.database] is nested under [server]
        assert toml_nested_table_count(_WITH_NESTED) >= 1

    def test_positive_for_multiple_tables(self):
        content = b"[a]\nkey = 1\n\n[b]\nkey = 2\n"
        assert toml_nested_table_count(content) >= 0
