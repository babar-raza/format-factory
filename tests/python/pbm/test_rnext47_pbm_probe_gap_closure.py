"""
test_rnext47_pbm_probe_gap_closure.py

Gap closure: GAP-PBM-FOSS-PROBE_PBM-001 (missing_test_coverage)
Sprint: FORMAT-FACTORY-PROBE-COVERAGE-PRODUCT-RNEXT47-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import probe_pbm

_P1_CONTENT = "P1\n3 2\n0 1 0\n1 0 1\n"


class TestPbmProbeGapClosure:
    """Targeted tests for probe_pbm covering GAP-PBM-FOSS-PROBE_PBM-001."""

    def test_probe_pbm_returns_dict(self, tmp_path):
        f = tmp_path / "test.pbm"
        f.write_text(_P1_CONTENT, encoding="utf-8")
        result = probe_pbm(f)
        assert isinstance(result, dict)

    def test_probe_pbm_exists_true(self, tmp_path):
        f = tmp_path / "test.pbm"
        f.write_text(_P1_CONTENT, encoding="utf-8")
        result = probe_pbm(f)
        assert result["exists"] is True

    def test_probe_pbm_exists_false_for_missing(self, tmp_path):
        result = probe_pbm(tmp_path / "ghost.pbm")
        assert result["exists"] is False

    def test_probe_pbm_valid_header_p1(self, tmp_path):
        f = tmp_path / "test.pbm"
        f.write_text(_P1_CONTENT, encoding="utf-8")
        result = probe_pbm(f)
        assert result.get("valid_header") is True

    def test_probe_pbm_magic_p1(self, tmp_path):
        f = tmp_path / "test.pbm"
        f.write_text(_P1_CONTENT, encoding="utf-8")
        result = probe_pbm(f)
        assert result.get("magic") == "P1"

    def test_probe_pbm_dimensions(self, tmp_path):
        f = tmp_path / "test.pbm"
        f.write_text(_P1_CONTENT, encoding="utf-8")
        result = probe_pbm(f)
        assert result.get("width") == 3
        assert result.get("height") == 2

    def test_probe_pbm_has_path_key(self, tmp_path):
        f = tmp_path / "test.pbm"
        f.write_text(_P1_CONTENT, encoding="utf-8")
        result = probe_pbm(f)
        assert "path" in result
