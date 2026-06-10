"""
test_r157_toml_roundtrip_capability.py — Capability coverage test for TOML roundtrip.

Closes GAP-TOML-FOSS-ROUNDTRIP-001 (missing_test_coverage).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.toml.toml_codec import load_toml, write_toml, roundtrip


SAMPLE_TOML = b"""\
title = "Test Config"

[server]
host = "localhost"
port = 8080

[database]
name = "testdb"
enabled = true
"""


class TestTomlRoundtripCapability:
    def test_roundtrip_returns_dict(self, tmp_path):
        src = tmp_path / "input.toml"
        src.write_bytes(SAMPLE_TOML)
        dest = tmp_path / "output.toml"
        result = roundtrip(src, dest)
        assert isinstance(result, dict)

    def test_roundtrip_preserves_string(self, tmp_path):
        src = tmp_path / "input.toml"
        src.write_bytes(SAMPLE_TOML)
        dest = tmp_path / "output.toml"
        result = roundtrip(src, dest)
        assert result["data"]["title"] == "Test Config"

    def test_roundtrip_preserves_nested(self, tmp_path):
        src = tmp_path / "input.toml"
        src.write_bytes(SAMPLE_TOML)
        dest = tmp_path / "output.toml"
        result = roundtrip(src, dest)
        assert result["data"]["server"]["host"] == "localhost"
        assert result["data"]["server"]["port"] == 8080

    def test_roundtrip_preserves_boolean(self, tmp_path):
        src = tmp_path / "input.toml"
        src.write_bytes(SAMPLE_TOML)
        dest = tmp_path / "output.toml"
        result = roundtrip(src, dest)
        assert result["data"]["database"]["enabled"] is True

    def test_roundtrip_creates_dest_file(self, tmp_path):
        src = tmp_path / "input.toml"
        src.write_bytes(SAMPLE_TOML)
        dest = tmp_path / "output.toml"
        roundtrip(src, dest)
        assert dest.exists()
        assert dest.stat().st_size > 0

    def test_roundtrip_from_bytes(self, tmp_path):
        dest = tmp_path / "output.toml"
        result = roundtrip(SAMPLE_TOML, dest)
        assert result["data"]["title"] == "Test Config"

    def test_roundtrip_empty_doc(self, tmp_path):
        src = tmp_path / "empty.toml"
        src.write_bytes(b"# empty\n")
        dest = tmp_path / "output.toml"
        result = roundtrip(src, dest)
        assert isinstance(result["data"], dict)
