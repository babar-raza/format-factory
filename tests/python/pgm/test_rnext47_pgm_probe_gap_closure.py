"""
test_rnext47_pgm_probe_gap_closure.py

Gap closure: GAP-PGM-FOSS-PROBE_PGM-001 (missing_test_coverage)
Sprint: FORMAT-FACTORY-PROBE-COVERAGE-PRODUCT-RNEXT47-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import probe_pgm

_P2_CONTENT = "P2\n4 2\n255\n0 64 128 255\n10 20 30 40\n"


class TestPgmProbeGapClosure:
    """Targeted tests for probe_pgm covering GAP-PGM-FOSS-PROBE_PGM-001."""

    def test_probe_pgm_returns_dict(self, tmp_path):
        f = tmp_path / "test.pgm"
        f.write_text(_P2_CONTENT, encoding="utf-8")
        result = probe_pgm(f)
        assert isinstance(result, dict)

    def test_probe_pgm_exists_true(self, tmp_path):
        f = tmp_path / "test.pgm"
        f.write_text(_P2_CONTENT, encoding="utf-8")
        result = probe_pgm(f)
        assert result["exists"] is True

    def test_probe_pgm_exists_false_for_missing(self, tmp_path):
        result = probe_pgm(tmp_path / "ghost.pgm")
        assert result["exists"] is False

    def test_probe_pgm_valid_header(self, tmp_path):
        f = tmp_path / "test.pgm"
        f.write_text(_P2_CONTENT, encoding="utf-8")
        result = probe_pgm(f)
        assert result.get("valid_header") is True

    def test_probe_pgm_magic_p2(self, tmp_path):
        f = tmp_path / "test.pgm"
        f.write_text(_P2_CONTENT, encoding="utf-8")
        result = probe_pgm(f)
        assert result.get("magic") == "P2"

    def test_probe_pgm_dimensions(self, tmp_path):
        f = tmp_path / "test.pgm"
        f.write_text(_P2_CONTENT, encoding="utf-8")
        result = probe_pgm(f)
        assert result.get("width") == 4
        assert result.get("height") == 2

    def test_probe_pgm_maxval(self, tmp_path):
        f = tmp_path / "test.pgm"
        f.write_text(_P2_CONTENT, encoding="utf-8")
        result = probe_pgm(f)
        assert result.get("maxval") == 255
