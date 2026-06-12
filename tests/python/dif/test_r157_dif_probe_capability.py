"""
test_r157_dif_probe_capability.py — Capability coverage test for DIF probe_dif function.

Closes GAP-DIF-FOSS-PROBE_DIF-001 (missing_test_coverage).
"""
from __future__ import annotations

import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.dif.dif_parser import (
    DifCell,
    DifDocument,
    probe_dif,
    write_dif,
)


def _make_dif(tmp_path, title="Test", rows=None):
    if rows is None:
        rows = [
            [DifCell(value=1.0, value_type="numeric"), DifCell(value="A", value_type="string")],
            [DifCell(value=2.0, value_type="numeric"), DifCell(value="B", value_type="string")],
        ]
    doc = DifDocument(title=title, vectors=len(rows[0]) if rows else 0, tuples=len(rows), rows=rows)
    p = tmp_path / "test.dif"
    write_dif(doc, p)
    return p


class TestDifProbeCapability:
    def test_probe_returns_dict(self, tmp_path):
        p = _make_dif(tmp_path)
        result = probe_dif(p)
        assert isinstance(result, dict)

    def test_probe_exists(self, tmp_path):
        p = _make_dif(tmp_path)
        result = probe_dif(p)
        assert result["exists"] is True

    def test_probe_valid_header(self, tmp_path):
        p = _make_dif(tmp_path)
        result = probe_dif(p)
        assert result["valid_header"] is True

    def test_probe_nonexistent_file(self, tmp_path):
        result = probe_dif(tmp_path / "nonexistent.dif")
        assert result["exists"] is False

    def test_probe_invalid_file(self, tmp_path):
        p = tmp_path / "bad.dif"
        p.write_text("This is not DIF")
        result = probe_dif(p)
        assert result["valid_header"] is False

    def test_probe_has_title(self, tmp_path):
        p = _make_dif(tmp_path, title="MySheet")
        result = probe_dif(p)
        assert "title" in result

    def test_probe_has_vectors(self, tmp_path):
        p = _make_dif(tmp_path)
        result = probe_dif(p)
        assert "vectors" in result
        assert result["vectors"] == 2

    def test_probe_keys_present(self, tmp_path):
        p = _make_dif(tmp_path)
        result = probe_dif(p)
        # probe returns at minimum: path, exists, valid_header, title, vectors
        assert "path" in result
        assert "title" in result
