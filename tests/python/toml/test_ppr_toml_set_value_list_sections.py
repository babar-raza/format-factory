"""Tests for TOML set_value and list_sections.

Sprint: product-progress-rnext
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

import pytest
from src.python.toml.toml_codec import (
    set_value,
    list_sections,
    load_toml,
    write_toml,
)

SIMPLE_TOML = b'[server]\nhost = "localhost"\nport = 8080\n\n[database]\nname = "mydb"\n'
NESTED_TOML = b'[app]\nname = "demo"\n\n[app.db]\nhost = "db-host"\nport = 5432\n\n[app.cache]\ntimeout = 30\n'
FLAT_TOML = b'key1 = 1\nkey2 = "hello"\nflag = true\n'


# --- set_value tests ---

def test_set_value_top_level_existing():
    """set_value overwrites an existing top-level scalar."""
    data = {"host": "old", "port": 80}
    result = set_value(data, "host", "new")
    assert result["host"] == "new"
    assert result["port"] == 80


def test_set_value_top_level_new():
    """set_value creates a new top-level key."""
    data = {"existing": 1}
    result = set_value(data, "new_key", "value")
    assert result["new_key"] == "value"
    assert result["existing"] == 1


def test_set_value_nested_existing():
    """set_value updates a nested key."""
    data = {"server": {"host": "old", "port": 80}}
    result = set_value(data, "server.host", "new-host")
    assert result["server"]["host"] == "new-host"
    assert result["server"]["port"] == 80


def test_set_value_creates_intermediate_sections():
    """set_value creates missing intermediate dicts."""
    data = {"other": 1}
    result = set_value(data, "app.db.host", "localhost")
    assert result["app"]["db"]["host"] == "localhost"
    assert result["other"] == 1


def test_set_value_does_not_mutate_input():
    """set_value returns a new dict; does not modify original."""
    data = {"key": "original"}
    result = set_value(data, "key", "changed")
    assert data["key"] == "original"
    assert result["key"] == "changed"


def test_set_value_numeric_value():
    """set_value works with numeric values."""
    data = {"port": 80}
    result = set_value(data, "port", 443)
    assert result["port"] == 443


def test_set_value_bool_value():
    """set_value works with boolean values."""
    data = {"active": False}
    result = set_value(data, "active", True)
    assert result["active"] is True


def test_set_value_type_error_on_non_dict_intermediate():
    """set_value raises TypeError when intermediate key is not a dict."""
    data = {"server": "not_a_dict"}
    with pytest.raises(TypeError):
        set_value(data, "server.host", "value")


def test_set_value_roundtrip(tmp_path):
    """set_value result can be written and reloaded via write_toml/load_toml."""
    data = {"name": "test", "count": 1}
    updated = set_value(data, "count", 99)
    dest = tmp_path / "out.toml"
    write_toml(updated, dest)
    reloaded = load_toml(dest)
    assert reloaded["data"]["count"] == 99
    assert reloaded["data"]["name"] == "test"


def test_set_value_nested_new_key():
    """set_value adds a new key to an existing nested section."""
    data = {"server": {"host": "localhost"}}
    result = set_value(data, "server.timeout", 30)
    assert result["server"]["timeout"] == 30
    assert result["server"]["host"] == "localhost"


# --- list_sections tests ---

def test_list_sections_basic():
    """list_sections returns top-level section names."""
    result = list_sections(SIMPLE_TOML)
    assert "server" in result
    assert "database" in result


def test_list_sections_excludes_scalars():
    """list_sections does not include scalar keys."""
    result = list_sections(FLAT_TOML)
    assert result == []


def test_list_sections_nested():
    """list_sections returns nested section paths with dotted notation."""
    result = list_sections(NESTED_TOML)
    assert "app" in result
    assert "app.db" in result
    assert "app.cache" in result


def test_list_sections_sorted():
    """list_sections returns sorted list."""
    result = list_sections(NESTED_TOML)
    assert result == sorted(result)


def test_list_sections_from_file(tmp_path):
    """list_sections works with a file path."""
    p = tmp_path / "cfg.toml"
    p.write_bytes(SIMPLE_TOML)
    result = list_sections(p)
    assert "server" in result
    assert "database" in result


def test_list_sections_empty_document():
    """list_sections returns empty list for TOML with no sections."""
    result = list_sections(b'key = 1\n')
    assert result == []


def test_list_sections_returns_list():
    """list_sections returns a list type."""
    result = list_sections(SIMPLE_TOML)
    assert isinstance(result, list)
