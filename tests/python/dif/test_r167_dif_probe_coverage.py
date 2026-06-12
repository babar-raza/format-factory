"""R167 — DIF probe_dif capability coverage test (GAP-DIF-FOSS-PROBE_DIF-001).

Closes: GAP-DIF-FOSS-PROBE_DIF-001 (missing_test_coverage for Probe_DIF capability).
Queue:  gap-coverage-q-005
"""
from __future__ import annotations

import pytest
from pathlib import Path

from src.python.dif.dif_parser import probe_dif

MINIMAL_2X2 = Path("samples/by-format/dif/valid/minimal-2x2.dif")
SINGLE_CELL = Path("samples/by-format/dif/valid/single-cell.dif")
NUMERIC_ROW = Path("samples/by-format/dif/valid/numeric-row.dif")


class TestDifProbe:
    def test_probe_returns_dict(self):
        result = probe_dif(MINIMAL_2X2)
        assert isinstance(result, dict)

    def test_probe_has_path_key(self):
        result = probe_dif(MINIMAL_2X2)
        assert "path" in result

    def test_probe_has_exists_true(self):
        result = probe_dif(MINIMAL_2X2)
        assert result["exists"] is True

    def test_probe_valid_header(self):
        result = probe_dif(MINIMAL_2X2)
        assert result.get("valid_header") is True

    def test_probe_single_cell(self):
        result = probe_dif(SINGLE_CELL)
        assert result["exists"] is True
        assert result.get("valid_header") is True

    def test_probe_numeric_row(self):
        result = probe_dif(NUMERIC_ROW)
        assert result["exists"] is True

    def test_probe_nonexistent_file(self, tmp_path):
        missing = tmp_path / "nonexistent.dif"
        result = probe_dif(missing)
        assert result["exists"] is False

    def test_probe_from_str_path(self):
        result = probe_dif(str(MINIMAL_2X2))
        assert result["exists"] is True
