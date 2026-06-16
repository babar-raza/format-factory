"""Sprint 72 — ODS / QOI / XCF / CSV product deepening (R302).

Tests 8 new analytics functions:
  ODS: ods_total_string_length, ods_is_all_numeric
  QOI: qoi_pixel_density, qoi_is_dark
  XCF: xcf_file_bytes_per_layer, xcf_average_dimension
  CSV: csv_nonempty_row_ratio, csv_avg_cell_length
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods import ods_total_string_length, ods_is_all_numeric
from src.python.qoi import qoi_pixel_density, qoi_is_dark
from src.python.xcf import xcf_file_bytes_per_layer, xcf_average_dimension
from src.python.csv.csv_parser import csv_nonempty_row_ratio, csv_avg_cell_length

_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"
_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid" / "2x2-black.qoi"
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf"
_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"


class TestOdsTotalStringLength:
    def test_returns_int(self):
        assert isinstance(ods_total_string_length(_ODS), int)

    def test_nonnegative(self):
        assert ods_total_string_length(_ODS) >= 0


class TestOdsIsAllNumeric:
    def test_returns_bool(self):
        assert isinstance(ods_is_all_numeric(_ODS), bool)


class TestQoiPixelDensity:
    def test_returns_float(self):
        assert isinstance(qoi_pixel_density(_QOI), (int, float))

    def test_positive(self):
        assert qoi_pixel_density(_QOI) > 0


class TestQoiIsDark:
    def test_returns_bool(self):
        assert isinstance(qoi_is_dark(_QOI), bool)


class TestXcfFileBytesPerLayer:
    def test_returns_float(self):
        assert isinstance(xcf_file_bytes_per_layer(_XCF), (int, float))

    def test_positive(self):
        assert xcf_file_bytes_per_layer(_XCF) > 0


class TestXcfAverageDimension:
    def test_returns_float(self):
        assert isinstance(xcf_average_dimension(_XCF), (int, float))

    def test_positive(self):
        assert xcf_average_dimension(_XCF) > 0


class TestCsvNonemptyRowRatio:
    def test_returns_float(self):
        assert isinstance(csv_nonempty_row_ratio(_CSV), (int, float))

    def test_between_zero_and_one(self):
        ratio = csv_nonempty_row_ratio(_CSV)
        assert 0.0 <= ratio <= 1.0


class TestCsvAvgCellLength:
    def test_returns_float(self):
        assert isinstance(csv_avg_cell_length(_CSV), (int, float))

    def test_nonnegative(self):
        assert csv_avg_cell_length(_CSV) >= 0.0
