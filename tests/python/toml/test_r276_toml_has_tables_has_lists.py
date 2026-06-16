"""
Tests for toml_has_tables and toml_has_lists.
Closes: GAP-TOML-FOSS-TOML_HAS_TAB-001, GAP-TOML-FOSS-TOML_HAS_LIS-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml import toml_has_tables, toml_has_lists

_WITH_TABLES = b"[server]\nhost = \"localhost\"\n\n[database]\nname = \"mydb\"\n"
_WITH_LIST = b"name = \"test\"\ntags = [\"a\", \"b\", \"c\"]\ncount = 1\n"
_FLAT_NO_LIST = b"name = \"test\"\ncount = 42\nenabled = true\n"
_EMPTY = b""


class TestTomlHasTables:
    def test_returns_bool(self):
        assert isinstance(toml_has_tables(_WITH_TABLES), bool)

    def test_true_when_tables_present(self):
        assert toml_has_tables(_WITH_TABLES) is True

    def test_false_for_flat_toml(self):
        assert toml_has_tables(_FLAT_NO_LIST) is False

    def test_false_for_empty(self):
        assert toml_has_tables(_EMPTY) is False

    def test_true_for_single_table(self):
        content = b"[config]\nkey = \"val\"\n"
        assert toml_has_tables(content) is True


class TestTomlHasLists:
    def test_returns_bool(self):
        assert isinstance(toml_has_lists(_WITH_LIST), bool)

    def test_true_when_list_present(self):
        assert toml_has_lists(_WITH_LIST) is True

    def test_false_for_no_list(self):
        assert toml_has_lists(_FLAT_NO_LIST) is False

    def test_false_for_empty(self):
        assert toml_has_lists(_EMPTY) is False

    def test_true_for_integer_list(self):
        content = b"values = [1, 2, 3]\n"
        assert toml_has_lists(content) is True
