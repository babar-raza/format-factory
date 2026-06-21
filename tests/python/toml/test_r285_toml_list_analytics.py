"""
Tests for TOML additional analytics (2 FOSS functions).
Closes: GAP-TOML-FOSS-MAX_LIST-001, GAP-TOML-FOSS-ALL_KEYS_LOWER-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml.toml_codec import toml_max_list_length, toml_all_keys_lowercase

_EMPTY = b""
_FLAT = b'name = "Alice"\nage = 42\n'
_WITH_LISTS = b'name = "Bob"\ntags = ["x", "y", "z"]\nscores = [1, 2]\n'
_UPPERCASE_KEY = b'Name = "Carol"\nage = 30\n'
_MIXED = b'name = "Dave"\nAge = 25\n'


class TestTomlMaxListLength:
    def test_returns_int(self):
        assert isinstance(toml_max_list_length(_FLAT), int)

    def test_empty_doc_returns_zero(self):
        assert toml_max_list_length(_EMPTY) == 0

    def test_no_lists_returns_zero(self):
        assert toml_max_list_length(_FLAT) == 0

    def test_single_list(self):
        assert toml_max_list_length(b'items = [1, 2, 3]\n') == 3

    def test_multiple_lists_returns_max(self):
        # tags has 3 items, scores has 2 — max is 3
        assert toml_max_list_length(_WITH_LISTS) == 3

    def test_nonnegative(self):
        assert toml_max_list_length(_WITH_LISTS) >= 0

    def test_longer_list(self):
        toml = b'vals = [10, 20, 30, 40, 50]\n'
        assert toml_max_list_length(toml) == 5

    def test_empty_list_returns_zero(self):
        toml = b'empty = []\n'
        assert toml_max_list_length(toml) == 0


class TestTomlAllKeysLowercase:
    def test_returns_bool(self):
        assert isinstance(toml_all_keys_lowercase(_FLAT), bool)

    def test_empty_doc_is_true(self):
        # vacuous truth: no keys to violate
        assert toml_all_keys_lowercase(_EMPTY) is True

    def test_all_lowercase_returns_true(self):
        assert toml_all_keys_lowercase(_FLAT) is True

    def test_uppercase_key_returns_false(self):
        assert toml_all_keys_lowercase(_UPPERCASE_KEY) is False

    def test_mixed_case_key_returns_false(self):
        assert toml_all_keys_lowercase(_MIXED) is False

    def test_with_lists_lowercase_returns_true(self):
        assert toml_all_keys_lowercase(_WITH_LISTS) is True

    def test_all_upper_returns_false(self):
        toml = b'NAME = "Eve"\nAGE = 99\n'
        assert toml_all_keys_lowercase(toml) is False

    def test_numeric_and_underscore_keys_lowercase(self):
        toml = b'key_1 = true\nkey_2 = false\n'
        assert toml_all_keys_lowercase(toml) is True
