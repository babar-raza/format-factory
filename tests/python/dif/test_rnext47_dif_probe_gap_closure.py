"""
test_rnext47_dif_probe_gap_closure.py

Gap closure: GAP-DIF-FOSS-PROBE_DIF-001 (missing_test_coverage)
Sprint: FORMAT-FACTORY-PROBE-COVERAGE-PRODUCT-RNEXT47-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import probe_dif

_MINIMAL_DIF = """\
TABLE
0,1
"Test"
VECTORS
0,2
""
TUPLES
0,1
""
DATA
0,0
""
-1,0
BOT
1,0
42
-1,0
EOD
"""


class TestDifProbeGapClosure:
    """Targeted tests for probe_dif covering GAP-DIF-FOSS-PROBE_DIF-001."""

    def test_probe_dif_returns_dict(self, tmp_path):
        f = tmp_path / "test.dif"
        f.write_text(_MINIMAL_DIF, encoding="utf-8")
        result = probe_dif(f)
        assert isinstance(result, dict)

    def test_probe_dif_exists_true(self, tmp_path):
        f = tmp_path / "test.dif"
        f.write_text(_MINIMAL_DIF, encoding="utf-8")
        result = probe_dif(f)
        assert result["exists"] is True

    def test_probe_dif_exists_false_for_missing_file(self, tmp_path):
        result = probe_dif(tmp_path / "ghost.dif")
        assert result["exists"] is False

    def test_probe_dif_valid_header(self, tmp_path):
        f = tmp_path / "test.dif"
        f.write_text(_MINIMAL_DIF, encoding="utf-8")
        result = probe_dif(f)
        assert result.get("valid_header") is True

    def test_probe_dif_has_title(self, tmp_path):
        f = tmp_path / "test.dif"
        f.write_text(_MINIMAL_DIF, encoding="utf-8")
        result = probe_dif(f)
        assert "title" in result
        assert result["title"] == "Test"

    def test_probe_dif_has_vectors(self, tmp_path):
        f = tmp_path / "test.dif"
        f.write_text(_MINIMAL_DIF, encoding="utf-8")
        result = probe_dif(f)
        assert "vectors" in result
        assert isinstance(result["vectors"], int)

    def test_probe_dif_has_path(self, tmp_path):
        f = tmp_path / "test.dif"
        f.write_text(_MINIMAL_DIF, encoding="utf-8")
        result = probe_dif(f)
        assert "path" in result
