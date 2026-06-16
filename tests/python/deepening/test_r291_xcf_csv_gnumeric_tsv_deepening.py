"""Sprint 61 — XCF / CSV / Gnumeric / TSV product deepening (R291).

Tests 8 new analytics functions:
  XCF: xcf_is_wide, xcf_pixel_density
  CSV: csv_is_empty, csv_column_name_lengths
  Gnumeric: gnumeric_column_variance, gnumeric_is_rectangular
  TSV: tsv_string_density, tsv_avg_row_length
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_is_wide, xcf_pixel_density
from src.python.csv.csv_parser import csv_is_empty, csv_column_name_lengths
from src.python.gnumeric import gnumeric_column_variance, gnumeric_is_rectangular
from src.python.tsv import tsv_string_density, tsv_avg_row_length

_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf"
_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"
_GNM = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"
_TSV = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"


class TestXcfIsWide:
    def test_returns_bool(self):
        assert isinstance(xcf_is_wide(_XCF), bool)

    def test_1x1_not_wide(self):
        assert xcf_is_wide(_XCF) is False


class TestXcfPixelDensity:
    def test_returns_float(self):
        assert isinstance(xcf_pixel_density(_XCF), (int, float))

    def test_positive(self):
        assert xcf_pixel_density(_XCF) > 0.0


class TestCsvIsEmpty:
    def test_returns_bool(self):
        assert isinstance(csv_is_empty(_CSV), bool)

    def test_minimal_not_empty(self):
        assert csv_is_empty(_CSV) is False


class TestCsvColumnNameLengths:
    def test_returns_list(self):
        result = csv_column_name_lengths(_CSV)
        assert isinstance(result, list)


class TestGnumericColumnVariance:
    def test_returns_float(self):
        assert isinstance(gnumeric_column_variance(_GNM), (int, float))

    def test_nonnegative(self):
        assert gnumeric_column_variance(_GNM) >= 0.0


class TestGnumericIsRectangular:
    def test_returns_bool(self):
        assert isinstance(gnumeric_is_rectangular(_GNM), bool)


class TestTsvStringDensity:
    def test_returns_float(self):
        assert isinstance(tsv_string_density(_TSV), (int, float))

    def test_bounded(self):
        val = tsv_string_density(_TSV)
        assert 0.0 <= val <= 1.0


class TestTsvAvgRowLength:
    def test_returns_float(self):
        assert isinstance(tsv_avg_row_length(_TSV), (int, float))

    def test_positive(self):
        assert tsv_avg_row_length(_TSV) > 0.0
