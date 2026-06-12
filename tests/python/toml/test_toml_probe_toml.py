"""
test_toml_probe_toml.py

Sprint: FORMAT-FACTORY-GAP-DRIVEN-PRODUCT-RNEXT-001
Gap IDs: GAP-TOML-FOSS-PROBE_TOML-001

Focused tests for probe_toml function.
Closes missing_test_coverage gap.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml.toml_codec import probe_toml


class TestProbeToml:
    def test_probe_existing_file(self, tmp_path):
        f = tmp_path / "test.toml"
        f.write_text('[section]\nkey = "value"\n', encoding="utf-8")
        result = probe_toml(str(f))
        assert isinstance(result, dict)
        assert result.get("exists") is True

    def test_probe_missing_file(self, tmp_path):
        result = probe_toml(str(tmp_path / "ghost.toml"))
        assert isinstance(result, dict)
        assert result.get("exists") is False

    def test_probe_returns_path(self, tmp_path):
        f = tmp_path / "a.toml"
        f.write_text("x = 1\n", encoding="utf-8")
        result = probe_toml(str(f))
        assert "path" in result

    def test_probe_empty_file(self, tmp_path):
        f = tmp_path / "empty.toml"
        f.write_text("", encoding="utf-8")
        result = probe_toml(str(f))
        assert isinstance(result, dict)
        assert result.get("exists") is True
