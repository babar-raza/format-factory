"""R167 — TOML Roundtrip capability coverage test (GAP-TOML-FOSS-ROUNDTRIP-001).

Closes: GAP-TOML-FOSS-ROUNDTRIP-001 (missing_test_coverage for Roundtrip capability).
Queue:  gap-coverage-q-004
"""
from __future__ import annotations

import pytest
from pathlib import Path

from src.python.toml.toml_codec import roundtrip, load_toml, write_toml

ROUNDTRIP_TOML = Path("reports/broad-rnext/sample-outputs/toml-roundtrip-output.toml")


class TestTomlRoundtrip:
    def test_roundtrip_returns_dict(self, tmp_path):
        dest = tmp_path / "out.toml"
        model = roundtrip(ROUNDTRIP_TOML, dest)
        assert isinstance(model, dict)

    def test_roundtrip_dest_file_created(self, tmp_path):
        dest = tmp_path / "out.toml"
        roundtrip(ROUNDTRIP_TOML, dest)
        assert dest.exists()

    def test_roundtrip_preserves_data(self, tmp_path):
        dest = tmp_path / "out.toml"
        original = load_toml(ROUNDTRIP_TOML)
        result = roundtrip(ROUNDTRIP_TOML, dest)
        assert result.get("data") == original.get("data")

    def test_roundtrip_from_bytes(self, tmp_path):
        dest = tmp_path / "out.toml"
        raw = ROUNDTRIP_TOML.read_bytes()
        model = roundtrip(raw, dest)
        assert isinstance(model, dict)

    def test_roundtrip_simple_content(self, tmp_path):
        src = tmp_path / "src.toml"
        dest = tmp_path / "dest.toml"
        src.write_text('[section]\nkey = "value"\n', encoding="utf-8")
        model = roundtrip(src, dest)
        assert model["data"]["section"]["key"] == "value"

    def test_roundtrip_numeric_values(self, tmp_path):
        src = tmp_path / "src.toml"
        dest = tmp_path / "dest.toml"
        src.write_text("count = 42\nrate = 3.14\n", encoding="utf-8")
        model = roundtrip(src, dest)
        assert model["data"]["count"] == 42

    def test_roundtrip_nested_table(self, tmp_path):
        src = tmp_path / "src.toml"
        dest = tmp_path / "dest.toml"
        src.write_text("[a]\n[a.b]\nval = true\n", encoding="utf-8")
        model = roundtrip(src, dest)
        assert model["data"]["a"]["b"]["val"] is True

    def test_roundtrip_idempotent(self, tmp_path):
        dest1 = tmp_path / "out1.toml"
        dest2 = tmp_path / "out2.toml"
        m1 = roundtrip(ROUNDTRIP_TOML, dest1)
        m2 = roundtrip(dest1, dest2)
        assert m1.get("data") == m2.get("data")
