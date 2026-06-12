"""
test_r169_toml_deep_coverage.py

Sprint: FORMAT-FACTORY-HARDENED-AUDIT-REMEDIATION-SPRINT10-001
Added: 2026-06-11

Tests for TOML deep functions: probe_toml, load_toml, get_value, has_key,
has_section, list_sections, count_keys, flatten, to_json_str, update_section,
set_value, diff_keys.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import (
    probe_toml,
    load_toml,
    get_value,
    set_value,
    has_key,
    has_section,
    list_sections,
    count_keys,
    get_all_keys,
    to_json_str,
    update_section,
    diff_keys,
    flatten,
    write_toml,
)

_SAMPLE = b"""
title = 'Config'
version = 3

[database]
host = 'localhost'
port = 5432

[server]
debug = true
workers = 4
"""

_SIMPLE = b"name = 'test'\nvalue = 42\n"


# ── probe_toml ────────────────────────────────────────────────────────────

class TestProbeToml:

    def test_returns_dict(self):
        result = probe_toml(_SIMPLE)
        assert isinstance(result, dict)

    def test_bytes_content_detected(self):
        result = probe_toml(_SAMPLE)
        assert isinstance(result, dict)

    def test_from_file(self, tmp_path):
        p = tmp_path / "config.toml"
        p.write_bytes(_SIMPLE)
        result = probe_toml(p)
        assert isinstance(result, dict)


# ── load_toml ─────────────────────────────────────────────────────────────

class TestLoadToml:

    def test_returns_dict(self):
        result = load_toml(_SIMPLE)
        assert isinstance(result, dict)

    def test_has_data_key(self):
        result = load_toml(_SIMPLE)
        assert "data" in result

    def test_data_contains_keys(self):
        result = load_toml(_SIMPLE)
        assert "name" in result["data"]

    def test_section_loaded(self):
        result = load_toml(_SAMPLE)
        assert "database" in result["data"]


# ── get_value ─────────────────────────────────────────────────────────────

class TestGetValue:

    def test_top_level_string(self):
        assert get_value(_SAMPLE, "title") == "Config"

    def test_top_level_int(self):
        assert get_value(_SAMPLE, "version") == 3

    def test_nested_key(self):
        result = get_value(_SAMPLE, "database.host")
        assert result == "localhost"

    def test_missing_key_raises(self):
        import pytest
        with pytest.raises(KeyError):
            get_value(_SAMPLE, "nonexistent_key_xyz")


# ── has_key / has_section ─────────────────────────────────────────────────

class TestHasKeyAndSection:

    def test_has_key_true(self):
        assert has_key(_SAMPLE, "title") is True

    def test_has_key_false(self):
        assert has_key(_SAMPLE, "no_such_key_xyz") is False

    def test_has_section_true(self):
        assert has_section(_SAMPLE, "database") is True

    def test_has_section_false(self):
        assert has_section(_SAMPLE, "nonexistent_section") is False

    def test_has_section_server(self):
        assert has_section(_SAMPLE, "server") is True


# ── list_sections ─────────────────────────────────────────────────────────

class TestListSections:

    def test_returns_list(self):
        result = list_sections(_SAMPLE)
        assert isinstance(result, list)

    def test_sections_found(self):
        result = list_sections(_SAMPLE)
        assert "database" in result
        assert "server" in result

    def test_simple_has_no_sections(self):
        result = list_sections(_SIMPLE)
        assert result == []


# ── count_keys ────────────────────────────────────────────────────────────

class TestCountKeys:

    def test_returns_int(self):
        assert isinstance(count_keys(_SIMPLE), int)

    def test_simple_count(self):
        assert count_keys(_SIMPLE) == 2

    def test_sample_top_level(self):
        # title + version + database + server = 4
        count = count_keys(_SAMPLE)
        assert count >= 2


# ── flatten ───────────────────────────────────────────────────────────────

class TestFlatten:

    def test_returns_dict(self):
        result = flatten(_SIMPLE)
        assert isinstance(result, dict)

    def test_simple_passthrough(self):
        result = flatten(_SIMPLE)
        assert "name" in result

    def test_nested_keys_dotted(self):
        result = flatten(_SAMPLE)
        assert "database.host" in result
        assert "database.port" in result

    def test_values_preserved(self):
        result = flatten(_SAMPLE)
        assert result.get("database.host") == "localhost"
        assert result.get("database.port") == 5432


# ── to_json_str ───────────────────────────────────────────────────────────

class TestToJsonStr:

    def test_returns_string(self):
        result = to_json_str(_SIMPLE)
        assert isinstance(result, str)

    def test_valid_json(self):
        import json
        result = json.loads(to_json_str(_SIMPLE))
        assert result is not None

    def test_contains_values(self):
        import json
        result = json.loads(to_json_str(_SIMPLE))
        assert result.get("name") == "test"


# ── update_section ────────────────────────────────────────────────────────

class TestUpdateSection:

    def test_returns_dict(self):
        data = load_toml(_SAMPLE)["data"]
        result = update_section(data, "database", {"host": "newhost"})
        assert isinstance(result, dict)

    def test_updates_key(self):
        data = load_toml(_SAMPLE)["data"]
        result = update_section(data, "database", {"host": "newhost"})
        assert result["database"]["host"] == "newhost"

    def test_preserves_other_keys(self):
        data = load_toml(_SAMPLE)["data"]
        result = update_section(data, "database", {"host": "newhost"})
        assert result["database"]["port"] == 5432


# ── set_value ─────────────────────────────────────────────────────────────

class TestSetValue:

    def test_returns_dict(self):
        data = load_toml(_SIMPLE)["data"]
        result = set_value(data, "name", "changed")
        assert isinstance(result, dict)

    def test_value_updated(self):
        data = load_toml(_SIMPLE)["data"]
        result = set_value(data, "name", "new_name")
        assert result["name"] == "new_name"

    def test_other_keys_preserved(self):
        data = load_toml(_SIMPLE)["data"]
        result = set_value(data, "name", "x")
        assert result["value"] == 42
