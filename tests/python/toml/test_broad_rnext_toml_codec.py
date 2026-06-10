"""Tests for TOML codec — new format acquisition (broad-rnext sprint).

Sprint: FORMAT-FACTORY-BROAD-CAPABILITY-LAYER-HEALING-RNEXT-BROAD-001
Uses stdlib tomllib (Python 3.11+) — no external dependencies.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

import pytest
from src.python.toml.toml_codec import (
    probe_toml,
    load_toml,
    write_toml,
    get_keys,
    roundtrip,
    TomlParseError,
    TomlInputError,
)

SIMPLE_TOML = b'[server]\nhost = "localhost"\nport = 8080\n\n[database]\nname = "mydb"\n'


def test_probe_toml_from_bytes():
    """probe_toml returns top_level_keys from raw bytes."""
    result = probe_toml(SIMPLE_TOML)
    assert "server" in result["top_level_keys"]
    assert "database" in result["top_level_keys"]


def test_probe_toml_section_count():
    """probe_toml counts top-level sections (dict values)."""
    result = probe_toml(SIMPLE_TOML)
    assert result["section_count"] == 2


def test_load_toml_from_bytes():
    """load_toml loads TOML from raw bytes."""
    model = load_toml(SIMPLE_TOML)
    assert model["format"] == "toml"
    assert model["data"]["server"]["host"] == "localhost"
    assert model["data"]["server"]["port"] == 8080


def test_load_toml_top_level_keys():
    """load_toml returns top_level_keys list."""
    model = load_toml(SIMPLE_TOML)
    assert set(model["top_level_keys"]) == {"server", "database"}


def test_load_toml_key_count():
    """load_toml returns correct key_count."""
    model = load_toml(SIMPLE_TOML)
    assert model["key_count"] == 2


def test_load_toml_from_file(tmp_path):
    """load_toml loads TOML from a file path."""
    p = tmp_path / "config.toml"
    p.write_bytes(SIMPLE_TOML)
    model = load_toml(p)
    assert model["data"]["database"]["name"] == "mydb"
    assert model["path"] == str(p)


def test_load_toml_invalid_raises(tmp_path):
    """load_toml raises TomlParseError on malformed TOML."""
    p = tmp_path / "bad.toml"
    p.write_text("key = [[invalid\n", encoding="utf-8")
    with pytest.raises(TomlParseError):
        load_toml(p)


def test_load_toml_missing_file_raises():
    """load_toml raises TomlInputError when file not found."""
    with pytest.raises(TomlInputError):
        load_toml("/nonexistent/path/file.toml")


def test_write_toml_creates_file(tmp_path):
    """write_toml creates a TOML file."""
    dest = tmp_path / "out.toml"
    write_toml({"title": "Hello", "count": 42}, dest)
    assert dest.exists()
    content = dest.read_text(encoding="utf-8")
    assert "Hello" in content
    assert "42" in content


def test_write_toml_bool_serialization(tmp_path):
    """write_toml serializes booleans as TOML true/false."""
    dest = tmp_path / "out.toml"
    write_toml({"flag": True, "off": False}, dest)
    content = dest.read_text(encoding="utf-8")
    assert "true" in content
    assert "false" in content


def test_write_toml_list_serialization(tmp_path):
    """write_toml serializes lists correctly."""
    dest = tmp_path / "out.toml"
    write_toml({"nums": [1, 2, 3]}, dest)
    content = dest.read_text(encoding="utf-8")
    assert "[1, 2, 3]" in content


def test_get_keys_from_bytes():
    """get_keys returns top-level keys from raw bytes."""
    keys = get_keys(SIMPLE_TOML)
    assert set(keys) == {"server", "database"}


def test_roundtrip_preserves_data(tmp_path):
    """roundtrip writes and reloads TOML, preserving data."""
    src = tmp_path / "src.toml"
    write_toml({"name": "test", "value": 99, "active": True}, src)
    dest = tmp_path / "dest.toml"
    result = roundtrip(src, dest)
    assert result["data"]["name"] == "test"
    assert result["data"]["value"] == 99
    assert result["data"]["active"] is True


def test_roundtrip_creates_dest_file(tmp_path):
    """roundtrip creates the destination file."""
    raw = b'key = "val"\nnum = 1\n'
    dest = tmp_path / "dest.toml"
    assert not dest.exists()
    roundtrip(raw, dest)
    assert dest.exists()


def test_roundtrip_from_bytes(tmp_path):
    """roundtrip accepts raw bytes as source."""
    raw = b'[info]\ntitle = "hello"\ncount = 5\n'
    dest = tmp_path / "dest.toml"
    result = roundtrip(raw, dest)
    assert result["data"]["info"]["title"] == "hello"
    assert result["data"]["info"]["count"] == 5


def test_probe_toml_from_file(tmp_path):
    """probe_toml handles file paths."""
    p = tmp_path / "config.toml"
    p.write_bytes(SIMPLE_TOML)
    result = probe_toml(p)
    assert result["exists"] is True
    assert "server" in result["top_level_keys"]
