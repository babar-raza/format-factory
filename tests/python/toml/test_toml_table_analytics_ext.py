"""Tests for TOML table analytics extensions in toml_table_analytics.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_table_analytics import (
    toml_top_level_keys,
    toml_has_boolean_values,
    toml_top_level_string_count,
    toml_top_level_int_count,
    toml_top_level_keys_sorted,
    toml_top_level_scalar_count,
)

SAMPLES = Path("samples/by-format/toml")
MINIMAL = SAMPLES / "minimal.toml"
# minimal.toml: keys=[title(str), version(str), enabled(bool), server(dict), database(dict)]
# title="Format Factory TOML Sample", version="1.0", enabled=true
# server={host, port}, database={name, max_connections}


# --- toml_top_level_keys ---

def test_top_level_keys_minimal():
    result = toml_top_level_keys(MINIMAL)
    assert result == ["title", "version", "enabled", "server", "database"]


def test_top_level_keys_count():
    assert len(toml_top_level_keys(MINIMAL)) == 5


def test_top_level_keys_contains_title():
    assert "title" in toml_top_level_keys(MINIMAL)


def test_top_level_keys_returns_list():
    assert isinstance(toml_top_level_keys(MINIMAL), list)


# --- toml_has_boolean_values ---

def test_has_boolean_values_minimal():
    assert toml_has_boolean_values(MINIMAL) is True


def test_has_boolean_values_returns_bool():
    assert isinstance(toml_has_boolean_values(MINIMAL), bool)


# --- toml_top_level_string_count ---

def test_top_level_string_count_minimal():
    # title and version are strings; enabled is bool, server/database are dicts
    assert toml_top_level_string_count(MINIMAL) == 2


def test_top_level_string_count_returns_int():
    assert isinstance(toml_top_level_string_count(MINIMAL), int)


# --- toml_top_level_int_count ---

def test_top_level_int_count_minimal():
    # No top-level integer keys (version is str, port is inside server dict)
    assert toml_top_level_int_count(MINIMAL) == 0


def test_top_level_int_count_returns_int():
    assert isinstance(toml_top_level_int_count(MINIMAL), int)


# --- toml_top_level_keys_sorted ---

def test_top_level_keys_sorted_minimal():
    result = toml_top_level_keys_sorted(MINIMAL)
    assert result == sorted(["title", "version", "enabled", "server", "database"])


def test_top_level_keys_sorted_is_sorted():
    result = toml_top_level_keys_sorted(MINIMAL)
    assert result == sorted(result)


def test_top_level_keys_sorted_returns_list():
    assert isinstance(toml_top_level_keys_sorted(MINIMAL), list)


# --- toml_top_level_scalar_count ---

def test_top_level_scalar_count_minimal():
    # title(str) + version(str) + enabled(bool) = 3 scalars; server/database are dicts
    assert toml_top_level_scalar_count(MINIMAL) == 3


def test_top_level_scalar_count_returns_int():
    assert isinstance(toml_top_level_scalar_count(MINIMAL), int)
