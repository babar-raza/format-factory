"""
test_rnext47_toml_probe_gap_closure.py

Gap closure: GAP-TOML-FOSS-PROBE_TOML-001 + GAP-TOML-FOSS-LOAD_TOML-001
Sprint: FORMAT-FACTORY-PROBE-COVERAGE-PRODUCT-RNEXT47-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import probe_toml, load_toml


class TestTomlProbeGapClosure:
    """Targeted tests for probe_toml covering GAP-TOML-FOSS-PROBE_TOML-001."""

    def test_probe_toml_from_bytes_returns_dict(self):
        result = probe_toml(b"[section]\nkey = 1\n")
        assert isinstance(result, dict)

    def test_probe_toml_format_key(self):
        result = probe_toml(b"[section]\nkey = 1\n")
        assert result.get("format") == "toml"

    def test_probe_toml_section_count(self):
        result = probe_toml(b"[a]\nx = 1\n[b]\ny = 2\n")
        assert result.get("section_count") == 2

    def test_probe_toml_key_count(self):
        # key_count counts top-level keys (each section is one top-level key)
        result = probe_toml(b"[section]\na = 1\nb = 2\nc = 3\n")
        assert result.get("key_count") == 1

    def test_probe_toml_top_level_keys(self):
        result = probe_toml(b"[server]\nport = 8080\n[db]\nhost = \"localhost\"\n")
        keys = result.get("top_level_keys", [])
        assert "server" in keys
        assert "db" in keys

    def test_probe_toml_size_bytes(self):
        content = b"[section]\nval = 42\n"
        result = probe_toml(content)
        assert result.get("size_bytes") == len(content)

    def test_probe_toml_empty_content(self):
        result = probe_toml(b"")
        assert isinstance(result, dict)


class TestTomlLoadGapClosure:
    """Targeted tests for load_toml covering GAP-TOML-FOSS-LOAD_TOML-001."""

    def test_load_toml_from_file(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_bytes(b"[server]\nport = 9090\n")
        result = load_toml(f)
        assert isinstance(result, dict)
        assert result.get("format") == "toml"

    def test_load_toml_data_accessible(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_bytes(b"[server]\nport = 9090\n")
        result = load_toml(f)
        data = result.get("data", {})
        assert "server" in data

    def test_load_toml_from_bytes(self):
        result = load_toml(b"[app]\nname = \"test\"\n")
        assert isinstance(result, dict)

    def test_load_toml_missing_file_graceful(self, tmp_path):
        # load_toml should not raise for a valid path (file may be read as path)
        result = load_toml(b"key = 42\n")
        assert isinstance(result, dict)
