"""
Tests for toml_key_count_per_table and toml_total_value_count.
Closes: GAP-TOML-FOSS-TOML_KEY_COU-001, GAP-TOML-FOSS-TOML_TOTAL_V-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml import toml_key_count_per_table, toml_total_value_count

_TWO_TABLES = b"[server]\nhost = \"localhost\"\nport = 8080\n\n[db]\nname = \"mydb\"\n"
_FLAT = b"a = 1\nb = 2\n"
_EMPTY = b""
_THREE_KEYS = b"name = \"test\"\ncount = 42\nenabled = true\n"


class TestTomlKeyCountPerTable:
    def test_returns_list(self):
        assert isinstance(toml_key_count_per_table(_TWO_TABLES), list)

    def test_empty_for_flat(self):
        # flat TOML has no tables, so no per-table key counts
        assert toml_key_count_per_table(_FLAT) == []

    def test_empty_for_empty(self):
        assert toml_key_count_per_table(_EMPTY) == []

    def test_two_tables_returns_two_counts(self):
        result = toml_key_count_per_table(_TWO_TABLES)
        assert len(result) == 2

    def test_counts_are_positive(self):
        result = toml_key_count_per_table(_TWO_TABLES)
        assert all(c > 0 for c in result)


class TestTomlTotalValueCount:
    def test_returns_int(self):
        assert isinstance(toml_total_value_count(_THREE_KEYS), int)

    def test_zero_for_empty(self):
        assert toml_total_value_count(_EMPTY) == 0

    def test_three_for_three_keys(self):
        assert toml_total_value_count(_THREE_KEYS) == 3

    def test_positive_for_flat(self):
        assert toml_total_value_count(_FLAT) > 0

    def test_two_for_two_keys(self):
        assert toml_total_value_count(_FLAT) == 2
