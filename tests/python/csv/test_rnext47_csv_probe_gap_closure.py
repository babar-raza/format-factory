"""
test_rnext47_csv_probe_gap_closure.py

Gap closure: GAP-CSV-FOSS-PROBE_CSV-001 (missing_test_coverage)
Sprint: FORMAT-FACTORY-PROBE-COVERAGE-PRODUCT-RNEXT47-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import probe_csv


class TestCsvProbeGapClosure:
    """Targeted tests for probe_csv covering GAP-CSV-FOSS-PROBE_CSV-001."""

    def test_probe_csv_returns_dict(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_text("a,b\n1,2\n", encoding="utf-8")
        result = probe_csv(f)
        assert isinstance(result, dict)

    def test_probe_csv_exists_true_for_valid_file(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_text("x,y\n10,20\n", encoding="utf-8")
        result = probe_csv(f)
        assert result["exists"] is True

    def test_probe_csv_exists_false_for_missing_file(self, tmp_path):
        result = probe_csv(tmp_path / "ghost.csv")
        assert result["exists"] is False

    def test_probe_csv_has_size_bytes(self, tmp_path):
        content = b"col1,col2\nval1,val2\n"
        f = tmp_path / "data.csv"
        f.write_bytes(content)
        result = probe_csv(f)
        assert "size_bytes" in result
        assert result["size_bytes"] == len(content)

    def test_probe_csv_has_first_line(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_text("header1,header2\nrow1a,row1b\n", encoding="utf-8")
        result = probe_csv(f)
        assert result["first_line"] == "header1,header2"

    def test_probe_csv_detects_delimiter_comma(self, tmp_path):
        f = tmp_path / "comma.csv"
        f.write_text("a,b,c\n1,2,3\n", encoding="utf-8")
        result = probe_csv(f)
        assert result["delimiter"] == ","

    def test_probe_csv_detects_delimiter_tab(self, tmp_path):
        f = tmp_path / "tab.csv"
        f.write_text("a\tb\tc\n1\t2\t3\n", encoding="utf-8")
        result = probe_csv(f)
        assert result["delimiter"] == "\t"

    def test_probe_csv_has_path_key(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_text("x\n1\n", encoding="utf-8")
        result = probe_csv(f)
        assert "path" in result
        assert str(f) in result["path"] or f.name in result["path"]
