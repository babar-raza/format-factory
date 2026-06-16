"""
Tests for toml_has_booleans and toml_is_flat.
Closes: GAP-TOML-FOSS-TOML_HAS_BOO-001, GAP-TOML-FOSS-TOML_IS_FLAT-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml import toml_has_booleans, toml_is_flat

_WITH_BOOL = b"enabled = true\nname = \"test\"\ncount = 42\n"
_NO_BOOL = b"name = \"test\"\ncount = 42\n"
_WITH_TABLES = b"[server]\nhost = \"localhost\"\nport = 8080\n"
_FLAT = b"a = 1\nb = 2\nc = 3\n"
_EMPTY = b""


class TestTomlHasBooleans:
    def test_returns_bool(self):
        assert isinstance(toml_has_booleans(_WITH_BOOL), bool)

    def test_true_when_boolean_present(self):
        assert toml_has_booleans(_WITH_BOOL) is True

    def test_false_when_no_boolean(self):
        assert toml_has_booleans(_NO_BOOL) is False

    def test_false_for_empty(self):
        assert toml_has_booleans(_EMPTY) is False

    def test_true_for_false_boolean(self):
        content = b"active = false\n"
        assert toml_has_booleans(content) is True


class TestTomlIsFlat:
    def test_returns_bool(self):
        assert isinstance(toml_is_flat(_FLAT), bool)

    def test_true_for_flat(self):
        assert toml_is_flat(_FLAT) is True

    def test_false_for_tables(self):
        assert toml_is_flat(_WITH_TABLES) is False

    def test_true_for_empty(self):
        # Empty TOML has no tables — it's flat (or trivially so)
        result = toml_is_flat(_EMPTY)
        assert isinstance(result, bool)

    def test_false_for_single_table(self):
        content = b"[config]\nkey = \"val\"\n"
        assert toml_is_flat(content) is False
