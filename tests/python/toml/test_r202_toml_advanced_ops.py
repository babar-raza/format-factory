"""
tests/python/toml/test_r202_toml_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT16-001
TASK-001 (part A): TOML advanced operations.

Covers: load_toml, probe_toml, get_value, has_key, has_section, list_sections,
count_keys, to_json_str, get_section_as_dict, flatten, get_all_keys, write_toml.
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import (
    load_toml, probe_toml, get_value, has_key, has_section, list_sections,
    count_keys, to_json_str, get_section_as_dict, flatten, get_all_keys, write_toml,
)

_SAMPLE = b'name = "myapp"\nversion = "1.0"\n\n[database]\nhost = "localhost"\nport = 5432\n'


def _write_toml(content: bytes = _SAMPLE) -> str:
    fd, path = tempfile.mkstemp(suffix=".toml")
    os.close(fd)
    Path(path).write_bytes(content)
    return path


class TestTomlLoadAndProbe:
    """load_toml, probe_toml."""

    def test_load_toml_returns_dict(self):
        path = _write_toml()
        try:
            model = load_toml(path)
            assert isinstance(model, dict)
        finally:
            os.unlink(path)

    def test_load_toml_has_data(self):
        path = _write_toml()
        try:
            model = load_toml(path)
            assert "data" in model
        finally:
            os.unlink(path)

    def test_load_toml_data_has_name(self):
        path = _write_toml()
        try:
            model = load_toml(path)
            assert model["data"].get("name") == "myapp"
        finally:
            os.unlink(path)

    def test_probe_toml_dict(self):
        path = _write_toml()
        try:
            result = probe_toml(path)
            assert isinstance(result, dict)
            assert result.get("exists") is True
        finally:
            os.unlink(path)

    def test_probe_toml_section_count(self):
        path = _write_toml()
        try:
            result = probe_toml(path)
            assert result.get("section_count") == 1  # [database] only
        finally:
            os.unlink(path)

    def test_probe_toml_top_level_keys(self):
        path = _write_toml()
        try:
            result = probe_toml(path)
            assert "name" in result.get("top_level_keys", [])
        finally:
            os.unlink(path)


class TestTomlKeyOps:
    """get_value, has_key, has_section, list_sections, count_keys, get_section_as_dict, get_all_keys."""

    def test_get_value_name(self):
        path = _write_toml()
        try:
            assert get_value(path, "name") == "myapp"
        finally:
            os.unlink(path)

    def test_get_value_version(self):
        path = _write_toml()
        try:
            assert get_value(path, "version") == "1.0"
        finally:
            os.unlink(path)

    def test_has_key_true(self):
        path = _write_toml()
        try:
            assert has_key(path, "name") is True
        finally:
            os.unlink(path)

    def test_has_key_false(self):
        path = _write_toml()
        try:
            assert has_key(path, "nonexistent_xyz") is False
        finally:
            os.unlink(path)

    def test_has_section_true(self):
        path = _write_toml()
        try:
            assert has_section(path, "database") is True
        finally:
            os.unlink(path)

    def test_has_section_false(self):
        path = _write_toml()
        try:
            assert has_section(path, "cache") is False
        finally:
            os.unlink(path)

    def test_list_sections_list(self):
        path = _write_toml()
        try:
            sections = list_sections(path)
            assert isinstance(sections, list)
            assert "database" in sections
        finally:
            os.unlink(path)

    def test_count_keys_int(self):
        path = _write_toml()
        try:
            n = count_keys(path)
            assert isinstance(n, int)
            assert n >= 3  # name, version, database section
        finally:
            os.unlink(path)

    def test_get_section_as_dict(self):
        path = _write_toml()
        try:
            sec = get_section_as_dict(path, "database")
            assert isinstance(sec, dict)
            assert sec.get("host") == "localhost"
            assert sec.get("port") == 5432
        finally:
            os.unlink(path)

    def test_get_all_keys_list(self):
        path = _write_toml()
        try:
            keys = get_all_keys(path)
            assert isinstance(keys, list)
            assert "name" in keys
        finally:
            os.unlink(path)


class TestTomlExport:
    """to_json_str, flatten, write_toml."""

    def test_to_json_str_str(self):
        path = _write_toml()
        try:
            result = to_json_str(path)
            assert isinstance(result, str)
            assert "myapp" in result
        finally:
            os.unlink(path)

    def test_flatten_dict(self):
        path = _write_toml()
        try:
            result = flatten(path)
            assert isinstance(result, dict)
            assert "name" in result
        finally:
            os.unlink(path)

    def test_flatten_has_nested_keys(self):
        path = _write_toml()
        try:
            result = flatten(path)
            # Nested keys become "section.key"
            assert any("database." in k for k in result.keys())
        finally:
            os.unlink(path)

    def test_write_toml_creates_file(self):
        path = _write_toml()
        fd, out = tempfile.mkstemp(suffix=".toml")
        os.close(fd)
        try:
            model = load_toml(path)
            write_toml(model["data"], out)
            assert os.path.getsize(out) > 0
        finally:
            os.unlink(path)
            os.unlink(out)
