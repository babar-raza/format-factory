"""Tests for csv_numeric_density and csv_unique_row_count.

Product deepening: CSV analytics — TC-H3-002-CSV / PDC-CSV-DENSITY-UNIQUE-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_numeric_density, csv_unique_row_count


class TestCsvNumericDensity:
    def test_all_numeric(self, tmp_path):
        p = tmp_path / "allnum.csv"
        p.write_text("1,2,3\n4,5,6\n", encoding="utf-8")
        result = csv_numeric_density(p)
        assert result == 1.0

    def test_mixed(self, tmp_path):
        p = tmp_path / "mixed.csv"
        p.write_text("1,abc\n3,def\n", encoding="utf-8")
        result = csv_numeric_density(p)
        assert 0.0 < result < 1.0

    def test_no_numeric(self, tmp_path):
        p = tmp_path / "nonum.csv"
        p.write_text("a,b\nc,d\n", encoding="utf-8")
        assert csv_numeric_density(p) == 0.0

    def test_empty(self, tmp_path):
        p = tmp_path / "empty.csv"
        p.write_text("", encoding="utf-8")
        assert csv_numeric_density(p) == 0.0

    def test_returns_float(self, tmp_path):
        p = tmp_path / "ft.csv"
        p.write_text("1,2\n", encoding="utf-8")
        assert isinstance(csv_numeric_density(p), float)


class TestCsvUniqueRowCount:
    def test_all_unique(self, tmp_path):
        p = tmp_path / "unique.csv"
        p.write_text("a,b\nc,d\n", encoding="utf-8")
        assert csv_unique_row_count(p) == 2

    def test_duplicates(self, tmp_path):
        p = tmp_path / "dup.csv"
        p.write_text("a,b\na,b\nc,d\n", encoding="utf-8")
        assert csv_unique_row_count(p) == 2

    def test_empty(self, tmp_path):
        p = tmp_path / "empty2.csv"
        p.write_text("", encoding="utf-8")
        assert csv_unique_row_count(p) == 0

    def test_returns_int(self, tmp_path):
        p = tmp_path / "ft2.csv"
        p.write_text("x\n", encoding="utf-8")
        assert isinstance(csv_unique_row_count(p), int)

    def test_single_row(self, tmp_path):
        p = tmp_path / "single.csv"
        p.write_text("a,b\n", encoding="utf-8")
        assert csv_unique_row_count(p) == 1
