"""Tests for TOML get_value, merge_toml, to_json_str.

Sprint: fodg-rework-full-hardening
Run ID: frfh (auto-detected)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

import pytest
from src.python.toml.toml_codec import (
    get_value,
    merge_toml,
    to_json_str,
    write_toml,
    TomlParseError,
)

SIMPLE_TOML = b'[server]\nhost = "localhost"\nport = 8080\n\n[database]\nname = "mydb"\n'
NESTED_TOML = b'[app]\nname = "demo"\nversion = "1.0"\n\n[app.db]\nhost = "db-host"\nport = 5432\n'


def test_get_value_top_level_key():
    """get_value returns a top-level section dict."""
    val = get_value(SIMPLE_TOML, "server")
    assert isinstance(val, dict)
    assert val["host"] == "localhost"


def test_get_value_nested_key():
    """get_value traverses dotted key paths."""
    val = get_value(SIMPLE_TOML, "server.host")
    assert val == "localhost"


def test_get_value_numeric_nested():
    """get_value returns numeric values from nested paths."""
    val = get_value(SIMPLE_TOML, "server.port")
    assert val == 8080


def test_get_value_missing_raises_key_error():
    """get_value raises KeyError for missing paths."""
    with pytest.raises(KeyError):
        get_value(SIMPLE_TOML, "nonexistent")


def test_get_value_missing_nested_raises():
    """get_value raises KeyError for partially missing nested path."""
    with pytest.raises(KeyError):
        get_value(SIMPLE_TOML, "server.nonexistent_key")


def test_get_value_from_file(tmp_path):
    """get_value works with file path input."""
    p = tmp_path / "cfg.toml"
    write_toml({"title": "hello", "count": 42}, p)
    assert get_value(p, "title") == "hello"
    assert get_value(p, "count") == 42


def test_merge_toml_base_values():
    """merge_toml includes base values when not overridden."""
    toml_a = b'name = "base"\nversion = 1\n'
    toml_b = b'version = 2\n'
    merged = merge_toml(toml_a, toml_b)
    assert merged["name"] == "base"
    assert merged["version"] == 2


def test_merge_toml_override_wins():
    """merge_toml: source_b values override source_a on conflict."""
    toml_a = b'host = "old"\nport = 80\n'
    toml_b = b'host = "new"\n'
    merged = merge_toml(toml_a, toml_b)
    assert merged["host"] == "new"
    assert merged["port"] == 80


def test_merge_toml_deep_merge():
    """merge_toml deep-merges nested dicts."""
    toml_a = b'[server]\nhost = "a"\nport = 80\n'
    toml_b = b'[server]\nhost = "b"\n'
    merged = merge_toml(toml_a, toml_b)
    assert merged["server"]["host"] == "b"
    assert merged["server"]["port"] == 80


def test_merge_toml_returns_dict():
    """merge_toml returns a plain dict, not a model."""
    toml_a = b'key = 1\n'
    toml_b = b'other = 2\n'
    result = merge_toml(toml_a, toml_b)
    assert isinstance(result, dict)
    assert result["key"] == 1
    assert result["other"] == 2


def test_to_json_str_returns_string():
    """to_json_str returns a string."""
    result = to_json_str(SIMPLE_TOML)
    assert isinstance(result, str)


def test_to_json_str_valid_json():
    """to_json_str output is valid JSON."""
    result = to_json_str(SIMPLE_TOML)
    parsed = json.loads(result)
    assert "server" in parsed
    assert parsed["server"]["host"] == "localhost"


def test_to_json_str_nested():
    """to_json_str handles nested TOML sections."""
    result = to_json_str(NESTED_TOML)
    parsed = json.loads(result)
    assert parsed["app"]["name"] == "demo"
    assert parsed["app"]["db"]["port"] == 5432


def test_to_json_str_sorted_keys():
    """to_json_str sorts keys for deterministic output."""
    toml = b'z_key = 1\na_key = 2\n'
    result = to_json_str(toml)
    idx_a = result.index("a_key")
    idx_z = result.index("z_key")
    assert idx_a < idx_z
