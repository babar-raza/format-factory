"""
test_rnext47_ppm_probe_gap_closure.py

Gap closure: GAP-PPM-FOSS-PROBE_PPM-001 (missing_test_coverage)
Sprint: FORMAT-FACTORY-PROBE-COVERAGE-PRODUCT-RNEXT47-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import probe_ppm

_P3_CONTENT = "P3\n3 1\n255\n255 0 0 0 255 0 0 0 255\n"


class TestPpmProbeGapClosure:
    """Targeted tests for probe_ppm covering GAP-PPM-FOSS-PROBE_PPM-001."""

    def test_probe_ppm_returns_dict(self, tmp_path):
        f = tmp_path / "test.ppm"
        f.write_text(_P3_CONTENT, encoding="utf-8")
        result = probe_ppm(f)
        assert isinstance(result, dict)

    def test_probe_ppm_exists_true(self, tmp_path):
        f = tmp_path / "test.ppm"
        f.write_text(_P3_CONTENT, encoding="utf-8")
        result = probe_ppm(f)
        assert result["exists"] is True

    def test_probe_ppm_exists_false_for_missing(self, tmp_path):
        result = probe_ppm(tmp_path / "ghost.ppm")
        assert result["exists"] is False

    def test_probe_ppm_valid_header(self, tmp_path):
        f = tmp_path / "test.ppm"
        f.write_text(_P3_CONTENT, encoding="utf-8")
        result = probe_ppm(f)
        assert result.get("valid_header") is True

    def test_probe_ppm_magic_p3(self, tmp_path):
        f = tmp_path / "test.ppm"
        f.write_text(_P3_CONTENT, encoding="utf-8")
        result = probe_ppm(f)
        assert result.get("magic") == "P3"

    def test_probe_ppm_dimensions(self, tmp_path):
        f = tmp_path / "test.ppm"
        f.write_text(_P3_CONTENT, encoding="utf-8")
        result = probe_ppm(f)
        assert result.get("width") == 3
        assert result.get("height") == 1

    def test_probe_ppm_maxval(self, tmp_path):
        f = tmp_path / "test.ppm"
        f.write_text(_P3_CONTENT, encoding="utf-8")
        result = probe_ppm(f)
        assert result.get("maxval") == 255
