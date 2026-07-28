"""Sprint 65 — ODS / QOI / XCF / CSV product deepening (R295).

Tests 8 new analytics functions:
  ODS: ods_row_value_variance, ods_is_multi_sheet
  QOI: qoi_is_monochrome, qoi_red_ratio
  XCF: xcf_layer_area_variance, xcf_row_count
  CSV: csv_column_count_variance, csv_has_numeric_header
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods import ods_row_value_variance, ods_is_multi_sheet
from src.python.qoi import qoi_is_monochrome, qoi_red_ratio
from src.python.xcf import xcf_layer_area_variance, xcf_row_count
from src.python.ff_csv.csv_parser import csv_column_count_variance, csv_has_numeric_header

_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"
_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid" / "2x2-black.qoi"
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf"
_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"


class TestOdsRowValueVariance:
    def test_returns_float(self):
        assert isinstance(ods_row_value_variance(_ODS), (int, float))

    def test_nonnegative(self):
        assert ods_row_value_variance(_ODS) >= 0.0


class TestOdsIsMultiSheet:
    def test_returns_bool(self):
        assert isinstance(ods_is_multi_sheet(_ODS), bool)


class TestQoiIsMonochrome:
    def test_returns_bool(self):
        assert isinstance(qoi_is_monochrome(_QOI), bool)


class TestQoiRedRatio:
    def test_returns_float(self):
        assert isinstance(qoi_red_ratio(_QOI), (int, float))

    def test_bounded(self):
        val = qoi_red_ratio(_QOI)
        assert 0.0 <= val <= 1.0


class TestXcfLayerAreaVariance:
    def test_returns_float(self):
        assert isinstance(xcf_layer_area_variance(_XCF), (int, float))

    def test_nonnegative(self):
        assert xcf_layer_area_variance(_XCF) >= 0.0


class TestXcfRowCount:
    def test_returns_int(self):
        assert isinstance(xcf_row_count(_XCF), int)

    def test_positive(self):
        assert xcf_row_count(_XCF) > 0


class TestCsvColumnCountVariance:
    def test_returns_float(self):
        assert isinstance(csv_column_count_variance(_CSV), (int, float))

    def test_nonnegative(self):
        assert csv_column_count_variance(_CSV) >= 0.0


class TestCsvHasNumericHeader:
    def test_returns_bool(self):
        assert isinstance(csv_has_numeric_header(_CSV), bool)
