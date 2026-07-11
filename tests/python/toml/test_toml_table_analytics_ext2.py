"""Tests for 6 new functions in toml_table_analytics (ext2 batch)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pytest

from toml.toml_table_analytics import (
    toml_recursive_numeric_count,
    toml_is_empty,
    toml_has_top_level_lists,
    toml_top_level_list_count,
    toml_max_string_length,
    toml_nested_table_count,
)

MINIMAL = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"

# minimal.toml data:
# title='Format Factory TOML Sample', version='1.0', enabled=True,
# server={host='localhost', port=8080}, database={name='format_factory', max_connections=10}


# --- toml_recursive_numeric_count ---

def test_recursive_numeric_count_minimal():
    # port=8080, max_connections=10 → 2 numeric (not bool)
    assert toml_recursive_numeric_count(MINIMAL) == 2


def test_recursive_numeric_count_bytes():
    data = b"[section]\ncount = 3\nvalue = 1.5\n"
    assert toml_recursive_numeric_count(data) == 2


def test_recursive_numeric_count_bool_excluded():
    # booleans should not be counted as numeric
    data = b"flag = true\ncount = 7\n"
    assert toml_recursive_numeric_count(data) == 1


# --- toml_is_empty ---

def test_is_empty_minimal():
    assert toml_is_empty(MINIMAL) is False


def test_is_empty_empty_doc():
    data = b""
    assert toml_is_empty(data) is True


def test_is_empty_with_content():
    data = b"key = 'value'\n"
    assert toml_is_empty(data) is False


# --- toml_has_top_level_lists ---

def test_has_top_level_lists_minimal():
    # minimal.toml has no top-level lists
    assert toml_has_top_level_lists(MINIMAL) is False


def test_has_top_level_lists_with_array():
    data = b"items = [1, 2, 3]\n"
    assert toml_has_top_level_lists(data) is True


def test_has_top_level_lists_nested_only():
    # list only nested inside a table — should be False (top-level check)
    data = b"[section]\nvalues = [1, 2]\n"
    assert toml_has_top_level_lists(data) is False


# --- toml_top_level_list_count ---

def test_top_level_list_count_minimal():
    assert toml_top_level_list_count(MINIMAL) == 0


def test_top_level_list_count_two_arrays():
    data = b"a = [1, 2]\nb = [3, 4]\nc = 'string'\n"
    assert toml_top_level_list_count(data) == 2


def test_top_level_list_count_zero():
    data = b"x = 'hello'\ny = 42\n"
    assert toml_top_level_list_count(data) == 0


# --- toml_max_string_length ---

def test_max_string_length_minimal():
    # 'Format Factory TOML Sample' = 26 chars
    assert toml_max_string_length(MINIMAL) == 26


def test_max_string_length_custom():
    data = b"a = 'hi'\nb = 'hello world'\n"
    assert toml_max_string_length(data) == 11


def test_max_string_length_no_strings():
    data = b"count = 42\n"
    assert toml_max_string_length(data) == 0


# --- toml_nested_table_count ---

def test_nested_table_count_minimal():
    # server and database tables = 2
    assert toml_nested_table_count(MINIMAL) == 2


def test_nested_table_count_zero():
    data = b"key = 'value'\nnum = 42\n"
    assert toml_nested_table_count(data) == 0


def test_nested_table_count_with_table():
    data = b"[section]\nkey = 'val'\n"
    assert toml_nested_table_count(data) == 1
