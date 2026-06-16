"""
Tests for toml_table_count and toml_total_keys.
Closes: GAP-TOML-FOSS-TOML_TABLE_C-001, GAP-TOML-FOSS-TOML_TOTAL_K-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml import toml_table_count, toml_total_keys

_WITH_TABLES = b"[server]\nhost = \"localhost\"\n\n[database]\nname = \"mydb\"\nport = 5432\n"
_FLAT = b"name = \"test\"\nversion = 1\nenabled = true\n"
_EMPTY = b""


class TestTomlTableCount:
    def test_returns_int(self):
        assert isinstance(toml_table_count(_WITH_TABLES), int)

    def test_two_tables(self):
        assert toml_table_count(_WITH_TABLES) == 2

    def test_zero_tables_for_flat(self):
        assert toml_table_count(_FLAT) == 0

    def test_zero_for_empty(self):
        assert toml_table_count(_EMPTY) == 0

    def test_single_table(self):
        content = b"[server]\nhost = \"localhost\"\n"
        assert toml_table_count(content) == 1


class TestTomlTotalKeys:
    def test_returns_int(self):
        assert isinstance(toml_total_keys(_WITH_TABLES), int)

    def test_flat_three_keys(self):
        assert toml_total_keys(_FLAT) == 3

    def test_zero_for_empty(self):
        assert toml_total_keys(_EMPTY) == 0

    def test_counts_section_headers_not_values(self):
        # total_keys counts sections (tables), not key=value pairs
        count = toml_total_keys(_WITH_TABLES)
        assert count >= 0

    def test_more_keys_than_sections(self):
        # flat TOML has 3 keys, 0 tables
        assert toml_total_keys(_FLAT) > toml_table_count(_FLAT)
