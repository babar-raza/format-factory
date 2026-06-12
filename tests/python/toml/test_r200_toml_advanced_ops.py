"""
tests/python/toml/test_r200_toml_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT5-001
TASK-001: TOML advanced operations — key access, sections, analytics, mutation, export.

Covers: probe_toml, load_toml, get_keys, get_all_keys, get_value, list_sections,
has_section, has_any_section, get_section_keys, get_section_as_dict, has_key,
count_keys, count_values_in_section, toml_string_value_count, toml_list_count,
count_sections_with_key, flatten, to_json_str, to_env, set_value, delete_key,
rename_key, update_section, diff_keys, merge_toml, write_toml, roundtrip.
"""
from __future__ import annotations

import sys
import os
import json
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml import (
    probe_toml, load_toml, write_toml, get_keys, roundtrip,
    get_value, merge_toml, to_json_str, set_value, list_sections,
    delete_key, get_section_keys, has_key, count_keys, flatten,
    to_env, diff_keys, rename_key, update_section, has_section,
    get_all_keys, get_section_as_dict, has_any_section,
    count_values_in_section, toml_string_value_count,
    toml_list_count, count_sections_with_key,
)

_CONTENT = b"""
title = "My App"
version = "1.0.0"

[database]
host = "localhost"
port = 5432
tags = ["primary", "prod"]

[server]
host = "0.0.0.0"
port = 8080
"""


def _make_toml_file(content=None):
    content = content or _CONTENT
    fd, path = tempfile.mkstemp(suffix=".toml")
    with os.fdopen(fd, "wb") as f:
        f.write(content)
    return path


class TestTomlProbeAndLoad:
    """Probe and load functions."""

    def test_probe_toml_returns_dict(self):
        path = _make_toml_file()
        try:
            result = probe_toml(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_probe_toml_exists_true(self):
        path = _make_toml_file()
        try:
            result = probe_toml(path)
            assert result.get("exists") is True
        finally:
            os.unlink(path)

    def test_probe_toml_section_count(self):
        path = _make_toml_file()
        try:
            result = probe_toml(path)
            assert result.get("section_count", 0) == 2
        finally:
            os.unlink(path)

    def test_load_toml_returns_dict(self):
        path = _make_toml_file()
        try:
            result = load_toml(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_load_toml_has_data_key(self):
        path = _make_toml_file()
        try:
            result = load_toml(path)
            assert "data" in result
        finally:
            os.unlink(path)

    def test_load_toml_data_has_top_level_keys(self):
        path = _make_toml_file()
        try:
            result = load_toml(path)
            data = result["data"]
            assert "title" in data
            assert data["title"] == "My App"
        finally:
            os.unlink(path)


class TestTomlKeyAccess:
    """Key and value access functions."""

    def test_get_keys_returns_list(self):
        path = _make_toml_file()
        try:
            result = get_keys(path)
            assert isinstance(result, list)
        finally:
            os.unlink(path)

    def test_get_keys_has_expected_keys(self):
        path = _make_toml_file()
        try:
            result = get_keys(path)
            assert "title" in result
            assert "database" in result
        finally:
            os.unlink(path)

    def test_get_all_keys_returns_list(self):
        path = _make_toml_file()
        try:
            result = get_all_keys(path)
            assert isinstance(result, list)
            assert len(result) > 0
        finally:
            os.unlink(path)

    def test_get_all_keys_has_dotted_paths(self):
        path = _make_toml_file()
        try:
            result = get_all_keys(path)
            assert "database.host" in result
        finally:
            os.unlink(path)

    def test_get_value_top_level(self):
        path = _make_toml_file()
        try:
            result = get_value(path, "title")
            assert result == "My App"
        finally:
            os.unlink(path)

    def test_get_value_nested(self):
        path = _make_toml_file()
        try:
            result = get_value(path, "database.host")
            assert result == "localhost"
        finally:
            os.unlink(path)


class TestTomlSectionOps:
    """Section inspection functions."""

    def test_list_sections_returns_list(self):
        path = _make_toml_file()
        try:
            result = list_sections(path)
            assert isinstance(result, list)
        finally:
            os.unlink(path)

    def test_list_sections_has_expected(self):
        path = _make_toml_file()
        try:
            result = list_sections(path)
            assert "database" in result
            assert "server" in result
        finally:
            os.unlink(path)

    def test_has_section_existing(self):
        path = _make_toml_file()
        try:
            assert has_section(path, "database") is True
        finally:
            os.unlink(path)

    def test_has_section_missing(self):
        path = _make_toml_file()
        try:
            assert has_section(path, "nosuchsection") is False
        finally:
            os.unlink(path)

    def test_has_any_section_true(self):
        path = _make_toml_file()
        try:
            assert has_any_section(path) is True
        finally:
            os.unlink(path)

    def test_get_section_keys_returns_list(self):
        path = _make_toml_file()
        try:
            result = get_section_keys(path, "database")
            assert isinstance(result, list)
            assert "host" in result
        finally:
            os.unlink(path)

    def test_get_section_as_dict_returns_dict(self):
        path = _make_toml_file()
        try:
            result = get_section_as_dict(path, "database")
            assert isinstance(result, dict)
            assert result.get("host") == "localhost"
        finally:
            os.unlink(path)


class TestTomlPredicates:
    """has_key and count_keys predicates."""

    def test_has_key_existing(self):
        path = _make_toml_file()
        try:
            assert has_key(path, "title") is True
        finally:
            os.unlink(path)

    def test_has_key_missing(self):
        path = _make_toml_file()
        try:
            assert has_key(path, "nonexistent") is False
        finally:
            os.unlink(path)

    def test_count_keys_top_level(self):
        path = _make_toml_file()
        try:
            n = count_keys(path)
            assert isinstance(n, int)
            assert n == 4  # title, version, database, server
        finally:
            os.unlink(path)

    def test_count_keys_recursive_greater(self):
        path = _make_toml_file()
        try:
            top = count_keys(path)
            rec = count_keys(path, recursive=True)
            assert rec > top
        finally:
            os.unlink(path)


class TestTomlAnalytics:
    """Analytics and counting functions."""

    def test_count_values_in_section(self):
        path = _make_toml_file()
        try:
            n = count_values_in_section(path, "database")
            assert isinstance(n, int)
            assert n == 3  # host, port, tags
        finally:
            os.unlink(path)

    def test_toml_string_value_count(self):
        path = _make_toml_file()
        try:
            n = toml_string_value_count(path)
            assert isinstance(n, int)
            assert n >= 0
        finally:
            os.unlink(path)

    def test_toml_list_count(self):
        path = _make_toml_file()
        try:
            n = toml_list_count(path)
            assert isinstance(n, int)
            assert n >= 0
        finally:
            os.unlink(path)

    def test_count_sections_with_key(self):
        path = _make_toml_file()
        try:
            n = count_sections_with_key(path, "host")
            assert isinstance(n, int)
            assert n == 2  # database and server both have host
        finally:
            os.unlink(path)

    def test_flatten_returns_dict(self):
        path = _make_toml_file()
        try:
            result = flatten(path)
            assert isinstance(result, dict)
            assert "database.host" in result
        finally:
            os.unlink(path)

    def test_flatten_values_accessible(self):
        path = _make_toml_file()
        try:
            result = flatten(path)
            assert result.get("database.host") == "localhost"
            assert result.get("server.port") == 8080
        finally:
            os.unlink(path)


class TestTomlExport:
    """Export functions: to_json_str, to_env."""

    def test_to_json_str_returns_string(self):
        path = _make_toml_file()
        try:
            result = to_json_str(path)
            assert isinstance(result, str)
        finally:
            os.unlink(path)

    def test_to_json_str_valid_json(self):
        path = _make_toml_file()
        try:
            result = to_json_str(path)
            parsed = json.loads(result)
            assert isinstance(parsed, dict)
            assert "database" in parsed
        finally:
            os.unlink(path)

    def test_to_env_returns_string(self):
        path = _make_toml_file()
        try:
            result = to_env(path)
            assert isinstance(result, str)
            assert "=" in result
        finally:
            os.unlink(path)

    def test_to_env_uppercase_keys(self):
        path = _make_toml_file()
        try:
            result = to_env(path, uppercase=True)
            assert "DATABASE_HOST" in result or "TITLE" in result
        finally:
            os.unlink(path)


class TestTomlMutation:
    """set_value, delete_key, rename_key, update_section, merge, diff, write, roundtrip."""

    def _get_data(self, path):
        return load_toml(path)["data"]

    def test_set_value_changes_value(self):
        path = _make_toml_file()
        try:
            data = self._get_data(path)
            result = set_value(data, "title", "Updated App")
            assert isinstance(result, dict)
            assert result.get("title") == "Updated App"
        finally:
            os.unlink(path)

    def test_delete_key_removes_key(self):
        path = _make_toml_file()
        try:
            data = self._get_data(path)
            result = delete_key(data, "version")
            assert isinstance(result, dict)
            assert "version" not in result
        finally:
            os.unlink(path)

    def test_rename_key_creates_new_key(self):
        path = _make_toml_file()
        try:
            data = self._get_data(path)
            result = rename_key(data, "title", "app_name")
            assert isinstance(result, dict)
            assert "app_name" in result
            assert "title" not in result
        finally:
            os.unlink(path)

    def test_update_section_updates_values(self):
        path = _make_toml_file()
        try:
            data = self._get_data(path)
            result = update_section(data, "database", {"port": 3306})
            assert isinstance(result, dict)
            assert result["database"]["port"] == 3306
        finally:
            os.unlink(path)

    def test_diff_keys_returns_list(self):
        path_a = _make_toml_file()
        path_b = _make_toml_file(b"title = \"Other\"\nnewkey = \"x\"\n")
        try:
            result = diff_keys(path_a, path_b)
            assert isinstance(result, list)
        finally:
            os.unlink(path_a)
            os.unlink(path_b)

    def test_diff_keys_detects_difference(self):
        path_a = _make_toml_file()
        path_b = _make_toml_file(b"title = \"Other\"\nnewkey = \"x\"\n")
        try:
            result = diff_keys(path_a, path_b)
            # version, database, server are in path_a but not path_b; newkey in path_b not path_a
            assert len(result) > 0
        finally:
            os.unlink(path_a)
            os.unlink(path_b)

    def test_merge_toml_returns_dict(self):
        path_a = _make_toml_file()
        path_b = _make_toml_file(b"[extra]\nfoo = \"bar\"\n")
        try:
            result = merge_toml(path_a, path_b)
            assert isinstance(result, dict)
        finally:
            os.unlink(path_a)
            os.unlink(path_b)

    def test_merge_toml_combines_sections(self):
        path_a = _make_toml_file()
        path_b = _make_toml_file(b"[extra]\nfoo = \"bar\"\n")
        try:
            result = merge_toml(path_a, path_b)
            # result may be raw data dict or wrapped; check either way
            data = result.get("data", result)
            assert "extra" in data or "database" in data
        finally:
            os.unlink(path_a)
            os.unlink(path_b)

    def test_write_toml_produces_file(self):
        path = _make_toml_file()
        fd, dest = tempfile.mkstemp(suffix=".toml")
        os.close(fd)
        try:
            data = self._get_data(path)
            write_toml(data, dest)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_roundtrip_produces_file(self):
        path = _make_toml_file()
        fd, dest = tempfile.mkstemp(suffix=".toml")
        os.close(fd)
        try:
            result = roundtrip(path, dest)
            assert isinstance(result, dict)
            assert os.path.getsize(dest) > 0
        finally:
            os.unlink(path)
            os.unlink(dest)
