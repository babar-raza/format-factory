"""Sprint 76 — ODS / QOI / XCF / CSV product deepening cycle 2 (R306).

Tests 8 new analytics functions:
  ODS: ods_empty_sheet_count, ods_numeric_sum
  QOI: qoi_color_depth_estimate, qoi_is_bright
  XCF: xcf_file_size_per_pixel, xcf_is_multi_layer
  CSV: csv_column_value_variance, csv_is_multi_column
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods import ods_empty_sheet_count, ods_numeric_sum
from src.python.qoi import qoi_color_depth_estimate, qoi_is_bright
from src.python.xcf import xcf_file_size_per_pixel, xcf_is_multi_layer
from src.python.csv.csv_parser import csv_column_value_variance, csv_is_multi_column

_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"
_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid" / "2x2-black.qoi"
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf"
_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"


class TestOdsEmptySheetCount:
    def test_returns_int(self):
        assert isinstance(ods_empty_sheet_count(_ODS), int)

    def test_nonnegative(self):
        assert ods_empty_sheet_count(_ODS) >= 0


class TestOdsNumericSum:
    def test_returns_float(self):
        assert isinstance(ods_numeric_sum(_ODS), float)


class TestQoiColorDepthEstimate:
    def test_returns_float(self):
        assert isinstance(qoi_color_depth_estimate(_QOI), float)

    def test_nonnegative(self):
        assert qoi_color_depth_estimate(_QOI) >= 0.0


class TestQoiIsBright:
    def test_returns_bool(self):
        assert isinstance(qoi_is_bright(_QOI), bool)


class TestXcfFileSizePerPixel:
    def test_returns_float(self):
        assert isinstance(xcf_file_size_per_pixel(_XCF), float)

    def test_positive(self):
        assert xcf_file_size_per_pixel(_XCF) > 0


class TestXcfIsMultiLayer:
    def test_returns_bool(self):
        assert isinstance(xcf_is_multi_layer(_XCF), bool)


class TestCsvColumnValueVariance:
    def test_returns_float(self):
        assert isinstance(csv_column_value_variance(_CSV), float)

    def test_nonnegative(self):
        assert csv_column_value_variance(_CSV) >= 0.0


class TestCsvIsMultiColumn:
    def test_returns_bool(self):
        assert isinstance(csv_is_multi_column(_CSV), bool)
