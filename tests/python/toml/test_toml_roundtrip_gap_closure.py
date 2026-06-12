"""
test_toml_roundtrip_gap_closure.py -- TOML roundtrip and set/delete operations.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-8
Tests TOML set_value, delete_key, roundtrip, and flatten with content verification.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import (
    roundtrip,
    get_value,
    set_value,
    delete_key,
    flatten,
)


_TOML_DATA = b'[app]\nname = "myapp"\nversion = "1.0.0"\n\n[app.settings]\ndebug = false\nport = 8080\n'


def test_set_value_modifies_key():
    data = {"x": 1, "y": 2}
    result = set_value(data, "x", 99)
    assert result["x"] == 99
    assert result["y"] == 2


def test_set_value_nested():
    data = {"app": {"name": "old"}}
    result = set_value(data, "app.name", "new")
    assert result["app"]["name"] == "new"


def test_delete_key_removes_entry():
    data = {"a": 1, "b": 2}
    result = delete_key(data, "a")
    assert "a" not in result
    assert "b" in result


def test_delete_nested_key():
    data = {"app": {"name": "test", "version": "1.0"}}
    result = delete_key(data, "app.name")
    assert "name" not in result["app"]
    assert "version" in result["app"]


def test_roundtrip_produces_file(tmp_path):
    src = tmp_path / "input.toml"
    src.write_bytes(_TOML_DATA)
    dest = tmp_path / "output.toml"
    result = roundtrip(str(src), str(dest))
    assert isinstance(result, dict)
    assert dest.exists()


def test_roundtrip_preserves_data(tmp_path):
    src = tmp_path / "input.toml"
    src.write_bytes(_TOML_DATA)
    dest = tmp_path / "output.toml"
    result = roundtrip(str(src), str(dest))
    # roundtrip returns a result dict with "data" key containing parsed content
    assert "data" in result
    assert result["data"]["app"]["name"] == "myapp"


def test_flatten_separator():
    src_data = b'[a]\n[a.b]\nx = 1\n'
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
        f.write(src_data)
        p = f.name
    flat = flatten(p, separator="/")
    assert any("/" in k for k in flat)


def test_get_value_returns_correct(tmp_path):
    # get_value takes a source path, not a dict
    src = tmp_path / "test.toml"
    src.write_bytes(b'[app]\nname = "test"\nport = 8080\n')
    val = get_value(str(src), "app.name")
    assert val == "test"
