"""Roundtrip tests for toml_writer.py — TC-W4-003."""
from __future__ import annotations

import pytest
from pathlib import Path
from toml.toml_writer import write_toml, write_toml_str, TomlWriteError
from toml import load_toml


def test_write_toml_str_simple_types():
    data = {"name": "test", "count": 42, "ratio": 3.14, "active": True}
    out = write_toml_str(data)
    assert 'name = "test"' in out
    assert "count = 42" in out
    assert "active = true" in out


def test_write_toml_str_nested_table():
    data = {"database": {"host": "localhost", "port": 5432}}
    out = write_toml_str(data)
    assert "[database]" in out
    assert 'host = "localhost"' in out
    assert "port = 5432" in out


def test_write_toml_str_list():
    data = {"tags": ["python", "toml", "test"]}
    out = write_toml_str(data)
    assert '"python"' in out
    assert "tags" in out


def test_write_toml_unsupported_type_raises():
    with pytest.raises(TomlWriteError, match="Unsupported"):
        write_toml_str({"bad": {1, 2, 3}})


def test_write_toml_roundtrip(tmp_path):
    data = {"title": "Hello", "count": 7, "nested": {"key": "value"}}
    path = tmp_path / "out.toml"
    write_toml(data, path)
    result = load_toml(str(path))
    # load_toml returns dict with 'data' key containing the parsed values
    assert result.get("format") == "toml"
    doc = result.get("data", {})
    assert doc.get("title") == "Hello"
    assert doc.get("count") == 7
    assert doc.get("nested", {}).get("key") == "value"
