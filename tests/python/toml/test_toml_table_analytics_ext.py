"""Tests for TOML table analytics extension functions."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_table_analytics import (
    toml_top_level_key_count,
    toml_has_nested_tables,
    toml_recursive_list_count,
    toml_is_deep,
    toml_avg_string_length,
    toml_top_level_table_count,
)

SAMPLES = Path("samples/by-format/toml")
MINIMAL = SAMPLES / "minimal.toml"
# minimal.toml: 5 top-level keys (title, version, enabled, server, database)
# server={host, port}, database={name, max_connections}, depth=2, no lists


# --- toml_top_level_key_count ---

def test_top_level_key_count_minimal():
    assert toml_top_level_key_count(MINIMAL) == 5


def test_top_level_key_count_returns_int():
    assert isinstance(toml_top_level_key_count(MINIMAL), int)


def test_top_level_key_count_positive():
    assert toml_top_level_key_count(MINIMAL) > 0


# --- toml_has_nested_tables ---

def test_has_nested_tables_minimal():
    # server and database are nested tables
    assert toml_has_nested_tables(MINIMAL) is True


def test_has_nested_tables_returns_bool():
    assert isinstance(toml_has_nested_tables(MINIMAL), bool)


# --- toml_recursive_list_count ---

def test_recursive_list_count_minimal():
    # minimal has no arrays
    assert toml_recursive_list_count(MINIMAL) == 0


def test_recursive_list_count_returns_int():
    assert isinstance(toml_recursive_list_count(MINIMAL), int)


def test_recursive_list_count_non_negative():
    assert toml_recursive_list_count(MINIMAL) >= 0


# --- toml_is_deep ---

def test_is_deep_minimal():
    # depth=2, not deep (< 3)
    assert toml_is_deep(MINIMAL) is False


def test_is_deep_returns_bool():
    assert isinstance(toml_is_deep(MINIMAL), bool)


# --- toml_avg_string_length ---

def test_avg_string_length_minimal():
    # strings: "Format Factory TOML Sample"=26, "1.0"=3, "localhost"=9, "format_factory"=14
    # avg = 52 / 4 = 13.0
    assert toml_avg_string_length(MINIMAL) == 13.0


def test_avg_string_length_returns_float():
    assert isinstance(toml_avg_string_length(MINIMAL), float)


def test_avg_string_length_positive():
    assert toml_avg_string_length(MINIMAL) > 0.0


# --- toml_top_level_table_count ---

def test_top_level_table_count_minimal():
    # server and database are top-level dicts = 2
    assert toml_top_level_table_count(MINIMAL) == 2


def test_top_level_table_count_returns_int():
    assert isinstance(toml_top_level_table_count(MINIMAL), int)


def test_top_level_table_count_positive():
    assert toml_top_level_table_count(MINIMAL) > 0
