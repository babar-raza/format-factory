"""Sprint 80 — ODS/QOI/XCF/CSV product deepening cycle 3."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods import ods_max_numeric_sum, ods_cell_density
from src.python.qoi import qoi_saturation_estimate, qoi_pixel_contrast
from src.python.xcf import xcf_color_mode_name, xcf_layer_size_variance
from src.python.csv.csv_parser import csv_field_type_variance, csv_header_length_sum

_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"
_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
_CSV = _REPO / "samples" / "by-format" / "csv"


def _qoi_sample():
    candidates = list(_QOI.glob("*.qoi"))
    assert candidates, "No .qoi sample found"
    return candidates[0]


def _xcf_sample():
    candidates = list(_XCF.glob("*.xcf"))
    assert candidates, "No .xcf sample found"
    return candidates[0]


def _csv_sample():
    candidates = list(_CSV.glob("*.csv"))
    assert candidates, "No .csv sample found"
    return candidates[0]


class TestOdsMaxNumericSum:
    def test_returns_float(self):
        result = ods_max_numeric_sum(_ODS)
        assert isinstance(result, float)


class TestOdsCellDensity:
    def test_returns_float(self):
        result = ods_cell_density(_ODS)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = ods_cell_density(_ODS)
        assert result >= 0.0


class TestQoiSaturationEstimate:
    def test_returns_float(self):
        result = qoi_saturation_estimate(_qoi_sample())
        assert isinstance(result, float)

    def test_between_zero_and_one(self):
        result = qoi_saturation_estimate(_qoi_sample())
        assert 0.0 <= result <= 1.0


class TestQoiPixelContrast:
    def test_returns_float(self):
        result = qoi_pixel_contrast(_qoi_sample())
        assert isinstance(result, float)

    def test_between_zero_and_one(self):
        result = qoi_pixel_contrast(_qoi_sample())
        assert 0.0 <= result <= 1.0


class TestXcfColorModeName:
    def test_returns_str(self):
        result = xcf_color_mode_name(_xcf_sample())
        assert isinstance(result, str)

    def test_not_empty(self):
        result = xcf_color_mode_name(_xcf_sample())
        assert len(result) > 0


class TestXcfLayerSizeVariance:
    def test_returns_float(self):
        result = xcf_layer_size_variance(_xcf_sample())
        assert isinstance(result, float)

    def test_non_negative(self):
        result = xcf_layer_size_variance(_xcf_sample())
        assert result >= 0.0


class TestCsvFieldTypeVariance:
    def test_returns_float(self):
        result = csv_field_type_variance(_csv_sample())
        assert isinstance(result, float)

    def test_non_negative(self):
        result = csv_field_type_variance(_csv_sample())
        assert result >= 0.0


class TestCsvHeaderLengthSum:
    def test_returns_int(self):
        result = csv_header_length_sum(_csv_sample())
        assert isinstance(result, int)

    def test_non_negative(self):
        result = csv_header_length_sum(_csv_sample())
        assert result >= 0
