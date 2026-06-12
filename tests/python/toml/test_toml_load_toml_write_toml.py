"""
test_toml_load_toml_write_toml.py

Sprint: FORMAT-FACTORY-GAP-DRIVEN-PRODUCT-RNEXT-001
Gap IDs: GAP-TOML-FOSS-LOAD_TOML-001, GAP-TOML-FOSS-WRITE_TOML-001

Focused tests for load_toml and write_toml functions.
Closes missing_test_coverage gaps for both functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import load_toml, write_toml, TomlInputError, TomlParseError


class TestLoadToml:
    def test_load_file_returns_dict(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_bytes(b'name = "test"\nvalue = 42\n')
        result = load_toml(f)
        assert isinstance(result, dict)
        assert result["format"] == "toml"

    def test_load_file_data_has_keys(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_bytes(b'name = "hello"\n')
        result = load_toml(f)
        assert "data" in result
        assert result["data"]["name"] == "hello"

    def test_load_missing_file_raises(self, tmp_path):
        with pytest.raises(TomlInputError):
            load_toml(tmp_path / "missing.toml")

    def test_load_bytes_input(self):
        raw = b'x = 1\ny = 2\n'
        result = load_toml(raw)
        assert result["data"]["x"] == 1
        assert result["data"]["y"] == 2

    def test_load_top_level_keys(self, tmp_path):
        f = tmp_path / "a.toml"
        f.write_bytes(b'a = 1\nb = 2\n')
        result = load_toml(f)
        assert set(result["top_level_keys"]) == {"a", "b"}

    def test_load_section(self, tmp_path):
        f = tmp_path / "sec.toml"
        f.write_bytes(b'[server]\nhost = "localhost"\n')
        result = load_toml(f)
        assert "server" in result["data"]
        assert result["data"]["server"]["host"] == "localhost"

    def test_load_malformed_raises(self, tmp_path):
        f = tmp_path / "bad.toml"
        f.write_bytes(b'key = ][[\n')
        with pytest.raises(TomlParseError):
            load_toml(f)


class TestWriteToml:
    def test_write_creates_file(self, tmp_path):
        dest = tmp_path / "out.toml"
        write_toml({"key": "value"}, dest)
        assert dest.exists()

    def test_write_roundtrip_scalar(self, tmp_path):
        dest = tmp_path / "rt.toml"
        write_toml({"x": 42, "name": "hello"}, dest)
        result = load_toml(dest)
        assert result["data"]["x"] == 42
        assert result["data"]["name"] == "hello"

    def test_write_roundtrip_bool(self, tmp_path):
        dest = tmp_path / "bool.toml"
        write_toml({"flag": True, "off": False}, dest)
        result = load_toml(dest)
        assert result["data"]["flag"] is True
        assert result["data"]["off"] is False

    def test_write_nested_section(self, tmp_path):
        dest = tmp_path / "nested.toml"
        write_toml({"db": {"host": "localhost", "port": 5432}}, dest)
        result = load_toml(dest)
        assert result["data"]["db"]["host"] == "localhost"
        assert result["data"]["db"]["port"] == 5432

    def test_write_empty_dict(self, tmp_path):
        dest = tmp_path / "empty.toml"
        write_toml({}, dest)
        assert dest.exists()
        result = load_toml(dest)
        assert result["data"] == {}

    def test_write_to_string_path(self, tmp_path):
        dest = tmp_path / "str_path.toml"
        write_toml({"v": 1}, str(dest))
        assert dest.exists()
