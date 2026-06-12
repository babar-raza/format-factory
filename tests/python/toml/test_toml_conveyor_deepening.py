"""
test_toml_conveyor_deepening.py -- TOML product deepening tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-4
Tests newer codec functions: flatten, to_env, diff_keys, rename_key, etc.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import (
    list_sections,
    get_section_keys,
    has_key,
    count_keys,
    flatten,
    to_env,
    diff_keys,
    rename_key,
    merge_toml,
    to_json_str,
)


_BASIC_TOML = b'[server]\nhost = "localhost"\nport = 8080\n\n[database]\nname = "mydb"\nmax_conn = 10\n'


def test_flatten(tmp_path):
    src = tmp_path / "test.toml"
    src.write_bytes(_BASIC_TOML)
    flat = flatten(str(src))
    assert isinstance(flat, dict)
    assert "server.host" in flat
    assert flat["server.host"] == "localhost"
    assert "database.max_conn" in flat


def test_to_env(tmp_path):
    src = tmp_path / "test.toml"
    src.write_bytes(_BASIC_TOML)
    env_str = to_env(str(src), prefix="APP_", uppercase=True)
    assert isinstance(env_str, str)
    assert "APP_SERVER_HOST" in env_str or "APP_" in env_str


def test_diff_keys(tmp_path):
    a = tmp_path / "a.toml"
    b = tmp_path / "b.toml"
    a.write_bytes(b'[server]\nhost = "localhost"\n')
    b.write_bytes(b'[server]\nhost = "localhost"\nport = 8080\n')
    diff = diff_keys(str(a), str(b))
    assert isinstance(diff, list)


def test_rename_key():
    data = {"name": "test", "value": 42}
    result = rename_key(data, "name", "title")
    assert "title" in result
    assert result["title"] == "test"
    assert "name" not in result


def test_count_keys(tmp_path):
    src = tmp_path / "test.toml"
    src.write_bytes(_BASIC_TOML)
    count = count_keys(str(src))
    assert isinstance(count, int)
    assert count >= 2


def test_count_keys_recursive(tmp_path):
    src = tmp_path / "test.toml"
    src.write_bytes(_BASIC_TOML)
    count = count_keys(str(src), recursive=True)
    assert isinstance(count, int)
    assert count >= 4


def test_has_key(tmp_path):
    src = tmp_path / "test.toml"
    src.write_bytes(_BASIC_TOML)
    assert has_key(str(src), "server.host") is True
    assert has_key(str(src), "nonexistent.key") is False


def test_list_sections(tmp_path):
    src = tmp_path / "test.toml"
    src.write_bytes(_BASIC_TOML)
    sections = list_sections(str(src))
    assert isinstance(sections, list)
    assert "server" in sections
    assert "database" in sections


def test_get_section_keys(tmp_path):
    src = tmp_path / "test.toml"
    src.write_bytes(_BASIC_TOML)
    keys = get_section_keys(str(src), "server")
    assert isinstance(keys, list)
    assert "host" in keys
    assert "port" in keys


def test_to_json_str(tmp_path):
    src = tmp_path / "test.toml"
    src.write_bytes(_BASIC_TOML)
    json_str = to_json_str(str(src))
    assert isinstance(json_str, str)
    assert "localhost" in json_str


def test_merge_toml(tmp_path):
    a = tmp_path / "a.toml"
    b = tmp_path / "b.toml"
    a.write_bytes(b'[server]\nhost = "localhost"\n')
    b.write_bytes(b'[server]\nport = 8080\n')
    merged = merge_toml(str(a), str(b))
    assert isinstance(merged, dict)
    assert "server" in merged
