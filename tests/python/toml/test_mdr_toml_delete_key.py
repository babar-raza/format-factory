"""Tests for toml_codec.delete_key — mainstream-product-deepening-rnext2.

Covers: normal deletion (top-level and nested), immutability, KeyError for missing path,
TypeError for non-dict intermediate, and deletion of nested-only key.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import delete_key


# ---------------------------------------------------------------------------
# Normal behavior — top-level
# ---------------------------------------------------------------------------

def test_delete_top_level_key():
    data = {"port": 8080, "host": "localhost", "debug": True}
    result = delete_key(data, "port")
    assert "port" not in result
    assert result["host"] == "localhost"
    assert result["debug"] is True


def test_delete_returns_new_dict():
    data = {"port": 8080, "host": "localhost"}
    result = delete_key(data, "port")
    assert data is not result
    assert "port" in data  # original unchanged


def test_delete_only_removes_target_key():
    data = {"a": 1, "b": 2, "c": 3}
    result = delete_key(data, "b")
    assert result == {"a": 1, "c": 3}


# ---------------------------------------------------------------------------
# Normal behavior — nested
# ---------------------------------------------------------------------------

def test_delete_nested_key():
    data = {"server": {"host": "localhost", "port": 8080}, "debug": False}
    result = delete_key(data, "server.port")
    assert result["server"] == {"host": "localhost"}
    assert result["debug"] is False


def test_delete_nested_key_does_not_mutate_input():
    data = {"server": {"host": "localhost", "port": 8080}}
    delete_key(data, "server.port")
    assert data["server"]["port"] == 8080  # unchanged


def test_delete_deeply_nested_key():
    data = {"a": {"b": {"c": {"d": 42, "e": 99}}}}
    result = delete_key(data, "a.b.c.d")
    assert result["a"]["b"]["c"] == {"e": 99}


def test_delete_entire_section():
    data = {"server": {"host": "localhost", "port": 8080}, "db": {"name": "mydb"}}
    result = delete_key(data, "server")
    assert "server" not in result
    assert result["db"]["name"] == "mydb"


# ---------------------------------------------------------------------------
# Boundary cases
# ---------------------------------------------------------------------------

def test_delete_sole_key():
    data = {"only": "value"}
    result = delete_key(data, "only")
    assert result == {}


def test_delete_key_with_numeric_value():
    data = {"timeout": 30, "retries": 5}
    result = delete_key(data, "timeout")
    assert result == {"retries": 5}


def test_delete_key_leaves_sibling_nested():
    data = {"server": {"host": "localhost", "port": 8080, "tls": True}}
    result = delete_key(data, "server.tls")
    assert result["server"] == {"host": "localhost", "port": 8080}


# ---------------------------------------------------------------------------
# Invalid-input / error cases
# ---------------------------------------------------------------------------

def test_delete_missing_top_level_raises_key_error():
    data = {"a": 1}
    with pytest.raises(KeyError):
        delete_key(data, "z")


def test_delete_missing_nested_key_raises_key_error():
    data = {"server": {"host": "localhost"}}
    with pytest.raises(KeyError):
        delete_key(data, "server.port")


def test_delete_non_dict_intermediate_raises_type_error_b():
    data = {"a": 1}
    with pytest.raises(TypeError):
        delete_key(data, "a.b.c")


def test_delete_non_dict_intermediate_raises_type_error():
    data = {"port": 8080}
    with pytest.raises((KeyError, TypeError)):
        delete_key(data, "port.sub")
